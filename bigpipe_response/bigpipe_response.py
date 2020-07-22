import enum
import json
import logging
import queue
import sys
import threading
import traceback

from django.http import StreamingHttpResponse

from bigpipe_response.bigpipe import Bigpipe
from bigpipe_response.bigpipe_render_options import BigpipeRenderOptions
from bigpipe_response.content_result import ContentResult
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

        self.logger = logging.getLogger(self.__class__.__name__)
        self.request = request
        self.pagelets = pagelets
        self.processed_js_files, self.processed_css_files = [], []

        from bigpipe_response.content_loader import ContentLoader
        self.content_loader = ContentLoader(render_type, render_source, render_context, render_options, js_dependencies, scss_dependencies, i18n_dependencies)

    def __stream_content(self):
        last_pagelet_target = None
        try:
            content_result = self.content_loader.load_content('body', [], [])
            self.processed_js_files = self.processed_js_files + content_result.js_effected_files
            self.processed_css_files = self.processed_css_files + content_result.css_effected_files

            for entry_content in self.__yield_content(content_result):
                yield entry_content

            dependencies = {}
            que = queue.Queue()
            paglent_count = len(self.pagelets)
            for pagelet in self.pagelets:
                last_pagelet_target = pagelet.target
                if pagelet.depends_on:
                    dependencies[pagelet.target] = pagelet.depends_on
                threading.Thread(target=self.__process_paglet, args=(pagelet, que), daemon=True).start()

            # Validate dependencies
            self.__validate_deendencies(dependencies)

            yield_paglets = []
            yield_later = {}
            for _ in range(paglent_count):
                pagelet_response = que.get()
                if isinstance(pagelet_response, BaseException): raise pagelet_response

                # Handle depends_on
                # When depends_on flag is set, the result will be cached and pushed only after the dependency is loaded
                target = pagelet_response['target']
                if target in dependencies:
                    dependent_target = dependencies.get(target)
                    if dependent_target not in yield_paglets:
                        yield_later.setdefault(dependent_target, []).append(pagelet_response)
                        continue

                yield_paglets.append(target)
                yield self._render_paglet_content(pagelet_response)

                if target in yield_later:
                    for yield_pagelet_response in yield_later.get(target):
                        yield self._render_paglet_content(yield_pagelet_response)
                    del yield_later[target]

            for target, yield_pagelet_response in yield_later.items():
                yield self._render_paglet_content(yield_pagelet_response)
                del yield_later[target]

        except BaseException as ex:
            self.logger.error("Error handling bigpipe response", exc_info=sys.exc_info())

            if not Bigpipe.get().config.is_production_mode: # DEVELOPMENT MODE
                error_target = 'Error in request source [{}]{}'.format(self.content_loader.render_source, ', on pagelet target element [{}]'.format(last_pagelet_target) if last_pagelet_target else '')
                content, js, css = BigpipeDebugger.get_exception_content(error_target, (str(ex.errors) if hasattr(ex, 'errors') else str(ex)), traceback.format_exc())
                i18n = {}
                content_result_error = ContentResult(content, js, css, i18n, [], [], [], [])
                if last_pagelet_target:
                    yield self._render_paglet_content(self.__get_pagelet_content(last_pagelet_target, content_result_error))
                else:
                    for entry_content in self.__yield_content(content_result_error):
                        yield entry_content
            else:
                raise ex

        yield '</body></html>\n'

    def __process_paglet(self, pagelet, result_queue):
        try:
            pagelet_response = pagelet.render()
            if isinstance(pagelet_response, BigpipeResponse):
                content_result = pagelet_response.content_loader.load_content(pagelet.target, self.processed_js_files, self.processed_css_files)
                self.processed_js_files = self.processed_js_files + content_result.js_effected_files
                self.processed_css_files = self.processed_css_files + content_result.css_effected_files
                result_queue.put(pagelet_response.__get_pagelet_content(pagelet.target, content_result))
            else:
                logging.warning('for pagelets expected only bigpipe response to operate, will return response content. {}'.format(pagelet_response))
                result_queue.put(pagelet_response)
        except BaseException as ex:
            result_queue.put(ex)

    #
    # Yield content
    #
    def __yield_content(self, content_result: ContentResult):
        if content_result.content:
            yield content_result.content
        if content_result.i18n:
            yield '\n<script>\n\trenderI18n({})\n</script>\n'.format(json.dumps(content_result.i18n))
        if content_result.css:
            yield '\n<style>\n\t{}\n</style>\n'.format(content_result.css)
        if content_result.js:
            yield '\n<script>\n\t{}\n</script>\n'.format(content_result.js)

    def __get_pagelet_content(self, paglet_target: str, content_result: ContentResult):
        result = {'target': paglet_target}
        if content_result.css:
            result['css'] =  content_result.css
        if content_result.content:
            result['html'] = content_result.content
        if content_result.js:
            result['js'] = content_result.js
        if content_result.i18n:
            result['i18n'] = content_result.i18n
        if content_result.js_links:
            result['js_links'] = content_result.js_links
        if content_result.css_links:
            result['css_links'] = content_result.css_links
        if Bigpipe.get().config.is_production_mode:
            result['remove'] = True
        return result

    def _render_paglet_content(self, pagelet_content):
        return """
            <script id='{}'>
                renderPagelet({})
            </script>
        """.format('script_{}'.format(pagelet_content['target']), json.dumps(pagelet_content))

    def __validate_deendencies(self, dependencies: dict):
        for key, value in dependencies.items():
            if value in dependencies:
                raise ValueError('Dependencies lock. dependency `{}` already defined'.format(value))

