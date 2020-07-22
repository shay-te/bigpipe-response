import json
import os

from django.conf import settings
from django.template import loader
from django.utils import translation

from bigpipe_response.bigpipe import Bigpipe
from bigpipe_response.bigpipe_render_options import BigpipeRenderOptions
from bigpipe_response.bigpipe_response import BigpipeResponse
from bigpipe_response.content_result import ContentResult
from bigpipe_response.dependencies_marshalling import DependenciesMarshalling


class ContentLoader(object):

    def __init__(self, render_type: str, render_source: str = None, render_context: str = {}, render_options: BigpipeRenderOptions = None, js_dependencies: list = [], scss_dependencies: list = [], i18n_dependencies: list = []):
        if render_type is None:
            raise ValueError('render_type cannot be None')
        if render_source is None:
            raise ValueError('render_source cannot be None')
        if render_context is None or not isinstance(render_context, dict):
            raise ValueError('render context must be a dict')
        if render_options is not None and not isinstance(render_options, BigpipeRenderOptions):
            raise ValueError('render_options can be None or instance of BigpipeRenderOptions')
        render_source_unmarshalled = DependenciesMarshalling.unmarshall(render_source)[0]
        if render_source_unmarshalled['link']:
            raise ValueError('render_source cannot be link')

        self.render_options = Bigpipe.get().get_render_option(render_options)
        self.render_type = render_type
        self.render_source = render_source_unmarshalled['source']
        self.render_source_processor_name = render_source_unmarshalled['processor_name'] or self.render_options.js_processor_name
        self.render_context = render_context
        self.js_dependencies = js_dependencies
        self.scss_dependencies = scss_dependencies
        self.i18n_dependencies = i18n_dependencies

        self.local_language = translation.get_language()

    def load_content(self, target_element: str, ignored_js_dependencies: list, ignored_css_dependencies: list):
        #
        # link handing
        #
        js_links_proc_to_dep, js_processors_name_order = self.__group_dependencies(True, self.js_dependencies, self.render_options.js_processor_name)
        css_links_proc_to_dep, css_processors_name_order = self.__group_dependencies(True, self.scss_dependencies, self.render_options.css_processor_name)

        # context
        render_context_dict = self.__get_context(self.render_context, js_links_proc_to_dep, css_links_proc_to_dep, js_processors_name_order, css_processors_name_order)

        #
        # content handing
        #

        # i18n
        i18n = self.__run_processor_i18n(self.render_source, self.render_options.i18n_processor_name, self.i18n_dependencies)

        # javascript
        js_content_proc_to_dep, js_processors_name_order = self.__group_dependencies(False, self.js_dependencies, self.render_options.js_processor_name)
        js, js_effected_files = self.__get_js_content(target_element,
                                                      render_context_dict,
                                                      js_processors_name_order,
                                                      js_content_proc_to_dep,
                                                      ignored_js_dependencies)

        # css
        css_extra_dependencies = self.__get_css_extra_source(js_content_proc_to_dep, js_effected_files)
        css_content_proc_to_dep, css_processors_name_order = self.__group_dependencies(False, self.scss_dependencies, self.render_options.css_processor_name, css_extra_dependencies)

        css, css_effected_files = self.__get_css_content(css_processors_name_order,
                                                         css_content_proc_to_dep,
                                                         ignored_css_dependencies)

        content = self.__get_content(render_context_dict, i18n)

        return ContentResult(content,
                             js,
                             css,
                             i18n,
                             render_context_dict['js_links'],
                             render_context_dict['css_links'],
                             js_effected_files,
                             css_effected_files)

    def __group_dependencies(self, links_only: bool, dependencies: list, default_processor: str, extra_dependencies_list: list = []):
        content = {}
        processors_order = []
        for dep in DependenciesMarshalling.unmarshall(dependencies):
            proc_name = dep['processor_name'] if dep['processor_name'] else default_processor
            if dep['link'] is True and links_only or not dep['link'] and not links_only:
                if proc_name not in processors_order: # Keep add order
                    processors_order.append(proc_name)
                content.setdefault(proc_name, []).append(dep['source'])

        if extra_dependencies_list:
            extra_dependencies = self.__filter_unregistered_dependencies(default_processor, extra_dependencies_list)
            if extra_dependencies:
                current_dependencies = []
                if default_processor in processors_order:
                    current_dependencies = content[default_processor]
                else:
                    processors_order.append(default_processor)
                content[default_processor] = list(set(current_dependencies + extra_dependencies))  # remove duplicates

        return content, list(processors_order)

    #
    # __run_processor_content_as_string will Run processors by the order of the processors names
    # "processors_name_ordered": the order of processors described in the dependencies list.
    # "processor_name_to_sources": keys are the "processor_name" and values is the list of dependencies to run
    # "exclude_dependencies": When dependencies to exclude.
    #
    # returns tuple:
    # (content, effected_files) .
    # content is list containing the content of all processors run
    # effected_files what files was processed to collected the content
    #
    def __run_processor_content_as_string(self, processors_name_ordered: list, processor_name_to_sources: dict, exclude_dependencies: list):
        content, effected_files = [], []
        for processor_name in processors_name_ordered:
            if processor_name in processor_name_to_sources:
                dependencies = processor_name_to_sources[processor_name]
                processor_result = self.__run_processor(processor_name,
                                                        '{}_dependencies'.format(self.render_source),
                                                        include_dependencies=dependencies,
                                                        exclude_dependencies=exclude_dependencies,
                                                        generate_missing_source=True)
                content.append(self.__get_file_content(processor_result.output_file))
                effected_files = effected_files + processor_result.effected_files
        return content, effected_files

    def __get_js_content(self, target_element: str, context: dict, processors_name_order: list, processor_name_to_sources: dict, exclude_dependencies: list):
        content, effected_files = self.__run_processor_content_as_string(processors_name_order, processor_name_to_sources, exclude_dependencies)

        if self.render_type == BigpipeResponse.RenderType.JAVASCRIPT:
            processor_result = self.__run_processor(self.render_source_processor_name,
                                                    self.render_source,
                                                    exclude_dependencies=exclude_dependencies)
            content.append(self.__get_file_content(processor_result.output_file))
            effected_files = effected_files + processor_result.effected_files
            if self.render_options.js_dom_bind:
                content.append(self.render_options.js_dom_bind.generate_bind_command(self.render_source, context, target_element))

        return ''.join(content), effected_files

    def __get_css_content(self, processors_name_order: list, processor_name_to_sources: dict, exclude_dependencies: list):
        content, effected_files = self.__run_processor_content_as_string(processors_name_order, processor_name_to_sources, [])

        # NOTICE! NOT YET SUPPORTED.
        # effected files will be only 'include_dependencies' and NOT 'css_dependencies_result.effected_files'.
        # since included files my have scss variables
        effected_files_css = []
        for proc_name, dependencies in processor_name_to_sources.items():
            effected_files_css = effected_files_css + dependencies
        return ''.join(content), effected_files_css

    # __get_css_extra_source will get javascript loaded components and give them for the css processor to include
    def __get_css_extra_source(self, processor_name_to_sources: dict, js_effected_files: list):
        if self.render_options.css_complete_dependencies_by_js:
            js_to_css_dependencies = list()
            # add render source
            if self.render_type is not BigpipeResponse.RenderType.TEMPLATE:
                js_to_css_dependencies.append(self.render_source)

            # add collect all javascript dependencies.
            for key, sources in processor_name_to_sources.items():
                for source in sources:
                    if source not in js_to_css_dependencies:
                        js_to_css_dependencies.append(source)

            # add javascript effected files
            # For example `Button.jsx` will collect `Button.scss` if exists
            for js_effect_file in js_effected_files:
                file_name = os.path.splitext(os.path.basename(js_effect_file))[0]
                if file_name not in js_to_css_dependencies:
                    js_to_css_dependencies.append(file_name)

            return js_to_css_dependencies

    def __get_content(self, render_context_dict: dict, i18n: dict):
        if self.render_type == BigpipeResponse.RenderType.TEMPLATE:
            return loader.get_template(self.render_source).render(render_context_dict)

        elif self.render_type == BigpipeResponse.RenderType.JAVASCRIPT_RENDER:
            return self.__render_processor(self.render_options.js_processor_name, self.render_source, render_context_dict, i18n)
        return ''

    #
    # Links
    #
    def __get_dependencies_links(self, processors_name_order: list, processor_name_to_sources: list, bundle_dependencies: bool):
        links, output_files = [], []
        render_options = {'output_file_prefix': '@'}
        for processor_name in processors_name_order:
            # Validating that 'processor_name' exists in the include list.
            # since 'processors_name_ordered' is a list of all processors names (links and content).
            # it may be that the processor_name dose not have links to process
            if processor_name in processor_name_to_sources:
                sources = processor_name_to_sources[processor_name]
                if bundle_dependencies:
                    source_name = self.render_source if self.render_source else sources[0]
                    output_files = output_files + [self.__run_processor(processor_name, source_name, sources, options=render_options, generate_missing_source=True).output_file]
                else:
                    output_files = output_files + [self.__run_processor(processor_name, source_name, options=render_options, generate_missing_source=False).output_file for source_name in sources]

        static_uri = Bigpipe.get().config.static_uri.strip('/') if Bigpipe.get().config.static_uri else ''

        # Build the path for the browser
        for output_file in output_files:
            output_directory_length = len(Bigpipe.get().config.rendered_output_path)
            output_file = output_file[output_directory_length::].replace('\\', '/')
            links.append('{}/{}'.format(static_uri, output_file.strip('/')))
        return links

    #
    #  Bigpipe call processors
    #
    def __run_processor_i18n(self, render_source: str, i18n_processor_name: str, i18n_dependencies: list):
        if getattr(settings, 'LOCALE_PATHS') and i18n_dependencies:
            i18n_json_file = self.__run_processor(i18n_processor_name, render_source, options={'language': self.local_language, 'i18n_dependencies': self.i18n_dependencies}).output_file
            return json.loads(self.__get_file_content(i18n_json_file))
        return {}

    def __run_processor(self, bigpipe_processor_name: str, source: str, include_dependencies: list = [], exclude_dependencies: list = [], options: dict = {}, generate_missing_source: bool = False):
        render_source = source.replace('.', '_')
        return Bigpipe.get().processors.run_processor(bigpipe_processor_name, render_source, options, include_dependencies, exclude_dependencies, generate_missing_source=generate_missing_source)

    def __render_processor(self, bigpipe_processor_name: str, source: str, context: dict, i18n: dict):
        return Bigpipe.get().processors.render_processor(bigpipe_processor_name, source, context, i18n)

    def __filter_unregistered_dependencies(self, processor_name, css_extra_files):
        return Bigpipe.get().processors.filter_unregistered_dependencies(processor_name, css_extra_files)

    #
    # helpers
    #
    def __get_context(self, context, js_links_processor_name_to_sources: list, css_links_processor_name_to_sources: list, js_processors_ordered, css_processors_ordered):
        links = {'js_links': [], 'css_links': []}
        if js_links_processor_name_to_sources:
            links['js_links'] = self.__get_dependencies_links(js_processors_ordered, js_links_processor_name_to_sources, self.render_options.js_bundle_link_dependencies)
        if css_links_processor_name_to_sources:
            links['css_links'] = self.__get_dependencies_links(css_processors_ordered, css_links_processor_name_to_sources, self.render_options.css_bundle_link_dependencies)

        return {**context, **links}

    def __get_file_content(self, file_path):
        fp = open(file_path, "r", encoding='utf8', errors='ignore')
        content = fp.read()
        fp.close()
        return content