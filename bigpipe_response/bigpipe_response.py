import enum
import json
import os
import queue
import sys
import threading
import traceback
import logging
from django.http import StreamingHttpResponse
from django.template import loader
from django.conf import settings
from django.utils import translation

from bigpipe_response.bigpipe import Bigpipe
from bigpipe_response.bigpipe_render_options import BigpipeRenderOptions
from bigpipe_response.debugger.bigpipe_debugger import BigpipeDebugger


class BigpipeResponse(StreamingHttpResponse):

    class RenderType(enum.Enum):
        TEMPLATE = enum.auto()
        JAVASCRIPT = enum.auto()
        JAVASCRIPT_RENDER = enum.auto()

    def __init__(self, request,
                 render_type=RenderType.TEMPLATE,
                 render_source=None,
                 render_context={},
                 pagelets=[],
                 js_dependencies=[],
                 scss_dependencies=[],
                 i18n_dependencies=[],
                 render_options: BigpipeRenderOptions = None):

        super().__init__(streaming_content=self.__stream_content())
        if request is None:
            raise ValueError('request cannot be None')
        if render_type is None:
            raise ValueError('render_type cannot be None')
        if render_source is None:
            raise ValueError('render_source cannot be None')
        if render_context is None or not isinstance(render_context, dict):
            raise ValueError('render context must be a dict')
        if render_options is not None and not isinstance(render_options, BigpipeRenderOptions):
            raise ValueError('render_options can be None or instance of BigpipeRenderOptions')

        self.logger = logging.getLogger(self.__class__.__name__)
        self.request = request
        self.render_type = render_type
        self.render_source = render_source
        self.render_context = render_context
        self.pagelets = pagelets
        self.js_dependencies = js_dependencies
        self.scss_dependencies = scss_dependencies
        self.i18n_dependencies = i18n_dependencies
        self.render_options = Bigpipe.get().get_render_option(render_options)
        self.local_language = translation.get_language()
        self.processed_js_files, self.processed_css_files = [], []

    def __process_paglet(self, pagelet, result_queue):
        try:
            pagelet_response = pagelet.render()
            if isinstance(pagelet_response, BigpipeResponse):
                content, js, css, i18n, ignore_js_dependencies, ignore_css_dependencies = pagelet_response.__get_entry_content(pagelet.target, self.processed_js_files, self.processed_css_files)
                self.processed_js_files = self.processed_js_files + ignore_js_dependencies
                self.processed_css_files = self.processed_css_files + ignore_css_dependencies
                result_queue.put(pagelet_response.__get_pagelet_content(pagelet.target, content, js, css, i18n))
            else:
                logging.warning('for pagelets expected only bigpipe response to operate, will return response content. {}'.format(pagelet_response))
                result_queue.put(pagelet_response)
        except BaseException as ex:
            result_queue.put(ex)

    def __stream_content(self):
        last_pagelet_target = None
        try:
            content, js, css, i18n, self.processed_js_files, self.processed_css_files = self.__get_entry_content('body', [], [])

            for entry_content in self.__yield_content(content, js, css, i18n):
                yield entry_content

            que = queue.Queue()
            paglent_count = len(self.pagelets)
            for pagelet in self.pagelets:
                last_pagelet_target = pagelet.target
                threading.Thread(target=self.__process_paglet, args=(pagelet, que), daemon=True).start()

            for _ in range(paglent_count):
                pageelet_response = que.get()
                if isinstance(pageelet_response, BaseException): raise pageelet_response
                yield pageelet_response

        except BaseException as ex:
            self.logger.error("Error handling bigpipe response", exc_info=sys.exc_info())

            if not Bigpipe.get().config.is_production_mode: # DEVELOPMENT MODE
                error_target = 'Error in request source [{}]{}'.format(self.render_source, ', on pagelet target element [{}]'.format(last_pagelet_target) if last_pagelet_target else '')
                content, js, css = BigpipeDebugger.get_exception_content(error_target, (str(ex.errors) if hasattr(ex, 'errors') else str(ex)), traceback.format_exc())
                i18n = {}
                if last_pagelet_target:
                    yield self.__get_pagelet_content(last_pagelet_target, content, js, css, i18n)
                else:
                    for entry_content in self.__yield_content(content, js, css, i18n):
                        yield entry_content
            else:
                raise ex

        yield '</body></html>\n'

    def __get_entry_content(self, target_element: str, ignored_js_dependencies: list, ignored_css_dependencies: list):
        js_links, js_files = self.__split_dependencies_list(self.js_dependencies)
        css_links, css_files = self.__split_dependencies_list(self.scss_dependencies)

        # context
        render_context_dict = self.__get_context(js_links, css_links)

        # i18n
        i18n = self.__run_processor_i18n()

        # js
        js, js_effected_files = self.__get_js_content(target_element=target_element, context=render_context_dict, include_dependencies=js_files, exclude_dependencies=ignored_js_dependencies)

        # css
        css, css_effected_files = self.__get_css_content(include_dependencies=css_files, js_dependencies=js_files + js_effected_files, exclude_dependencies=ignored_css_dependencies)

        # get content
        content = self.__get_content(render_context_dict, i18n)

        return content, js, css, i18n, js_effected_files, css_effected_files

    def __get_context(self, js_links, css_links):
        links = {}
        if js_links:
            links['js_links'] = self.__get_dependencies_links(self.render_options.js_processor_name, self.render_options.js_link_bundle_dependencies, js_links)
        if css_links:
            links['css_links'] = self.__get_dependencies_links(self.render_options.css_processor_name, self.render_options.css_link_bundle_dependencies, css_links)

        return {**self.render_context, **links}

    def __get_content(self, render_context_dict: dict, i18n: dict):
        if self.render_type == BigpipeResponse.RenderType.TEMPLATE:
            return loader.get_template(self.render_source).render(render_context_dict)

        elif self.render_type == BigpipeResponse.RenderType.JAVASCRIPT_RENDER:
            return self.__render_processor(self.render_options.js_processor_name, self.render_source, render_context_dict, i18n)
        return ''

    def __get_js_content(self, target_element: str, context: dict, include_dependencies: list, exclude_dependencies: list):
        content, effected_files = [], []

        if include_dependencies:
            processor_result = self.__run_processor(self.render_options.js_processor_name,
                                                    '{}_dependencies'.format(self.render_source),
                                                    include_dependencies=include_dependencies,
                                                    exclude_dependencies=exclude_dependencies,
                                                    generate_missing_source=True)
            content.append(self.__get_file_content(processor_result.output_file))
            effected_files = effected_files + processor_result.effected_files

        if self.render_type == BigpipeResponse.RenderType.JAVASCRIPT:
            processor_result = self.__run_processor(self.render_options.js_processor_name,
                                                    self.render_source,
                                                    exclude_dependencies=exclude_dependencies)
            content.append(self.__get_file_content(processor_result.output_file))
            effected_files = effected_files + processor_result.effected_files
            if self.render_options.javascript_dom_bind:
                content.append(self.render_options.javascript_dom_bind.generate_bind_command(self.render_source, context, target_element))

        return ''.join(content), effected_files

    def __get_css_content(self, include_dependencies: list, js_dependencies: list, exclude_dependencies: list):
        if self.render_options.css_complete_dependencies_by_js:
            render_source_as_dependency = [self.render_source] if self.render_type != BigpipeResponse.RenderType.TEMPLATE else []
            js_to_css_dependencies = [os.path.splitext(os.path.basename(js_dependency))[0] for js_dependency in render_source_as_dependency + js_dependencies]
            css_extra_files = Bigpipe.get().processors.filter_unregistered_dependencies(self.render_options.css_processor_name, js_to_css_dependencies)
            include_dependencies = list(set(include_dependencies + css_extra_files))  # remove duplicates

        if include_dependencies:
            css_dependencies_result = self.__run_processor(self.render_options.css_processor_name,
                                                           self.render_source,
                                                           include_dependencies=include_dependencies,
                                                           exclude_dependencies=[],  # exclude_dependencies,
                                                           generate_missing_source=True)
            # effected files will be only 'include_dependencies' and NOT 'css_dependencies_result.effected_files'.
            # since included files my have scss variables
            return self.__get_file_content(css_dependencies_result.output_file), include_dependencies
        else:
            return '', []


    #
    # Links
    #
    def __get_dependencies_links(self, bigpipe_processor_name: str, bundle_dependencies: bool, inputs: list):
        if not inputs:
            return []
        if bundle_dependencies:
            return [self.__get_dependency_as_link(bigpipe_processor_name, 'bundle_{}'.format(self.render_source), inputs, generate_missing_source=True)]
        else:
            return [self.__get_dependency_as_link(bigpipe_processor_name, input, [], generate_missing_source=False) for input in inputs]

    def __get_dependency_as_link(self, bigpipe_processor_name: str, input: str, include_dependencies: list, generate_missing_source: bool):
        output_file = self.__run_processor(bigpipe_processor_name, input, include_dependencies, generate_missing_source=generate_missing_source).output_file
        static_uri = Bigpipe.get().config.static_uri.strip('/') if Bigpipe.get().config.static_uri else ''
        output_file = output_file[len(Bigpipe.get().config.rendered_output_path)::].replace('\\', '/')
        return '{}/{}'.format(static_uri, output_file.strip('/'))

    #
    # Yield content
    #
    def __yield_content(self, content: str, js: str, css: str, i18n: dict):
        if content:
            yield content
        if i18n:
            yield '\n<script>\n\trenderI18n({})\n</script>\n'.format(json.dumps(i18n))
        if css:
            yield '\n<style>\n\t{}\n</style>\n'.format(css)
        if js:
            yield '\n<script>\n\t{}\n</script>\n'.format(js)

    def __get_pagelet_content(self, paglet_target: str, content: str, js: str, css: str, i18n: dict):
        result = {'target': paglet_target}
        if css:
            result['css'] = css
        if content:
            result['html'] = content
        if js:
            result['js'] = js
        if i18n:
            result['i18n'] = i18n
        if Bigpipe.get().config.is_production_mode:
            result['remove'] = True

        return """
            <script id='{}'>
                renderPagelet({})
            </script>
        """.format('script_{}'.format(paglet_target), json.dumps(result))

    #
    #  Bigpipe call processors
    #
    def __run_processor_i18n(self):
        if getattr(settings, 'LOCALE_PATHS') and self.i18n_dependencies:
            i18n_json_file = self.__run_processor(self.render_options.i18n_processor_name, self.render_source, options={'language': self.local_language, 'i18n_dependencies': self.i18n_dependencies}).output_file
            return json.loads(self.__get_file_content(i18n_json_file))
        return {}

    def __run_processor(self, bigpipe_processor_name: str, source: str, include_dependencies: list = [], exclude_dependencies: list = [], options: dict = {}, generate_missing_source: bool = False):
        render_source = source.replace('.', '_') if self.render_type == BigpipeResponse.RenderType.TEMPLATE else source
        return Bigpipe.get().processors.run_processor(bigpipe_processor_name, render_source, options, include_dependencies, exclude_dependencies, generate_missing_source=generate_missing_source)

    def __render_processor(self, bigpipe_processor_name: str, source: str, context: dict, i18n: dict):
        return Bigpipe.get().processors.render_processor(bigpipe_processor_name, source, context, i18n)
    #
    # helpers
    #
    def __split_dependencies_list(self, dependencies: list):
        links, files = [], []
        [links.append(dependency[1:]) if dependency.startswith('@') else files.append(dependency) for dependency in dependencies]
        return links, files

    def __get_file_content(self, file_path):
        fp = open(file_path, "r")
        content = fp.read()
        fp.close()
        return content