import enum
import json
import queue
import sys
import threading
import traceback
import logging
from django.http import StreamingHttpResponse

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

        self.logger = logging.getLogger(self.__class__.__name__)
        self.request = request
        self.pagelets = pagelets
        self.processed_js_files, self.processed_css_files = [], []

        from bigpipe_response.content_loader import ContentLoader
        self.content_loader = ContentLoader(render_type, render_source, render_context, render_options, js_dependencies, scss_dependencies, i18n_dependencies)


    def __stream_content(self):
        last_pagelet_target = None
        try:
            content, js, css, i18n, js_effected_files, css_effected_files = self.content_loader.load_content('body', [], [])
            self.processed_js_files = self.processed_js_files + js_effected_files
            self.processed_css_files = self.processed_css_files + css_effected_files

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
                error_target = 'Error in request source [{}]{}'.format(self.content_loader.render_source, ', on pagelet target element [{}]'.format(last_pagelet_target) if last_pagelet_target else '')
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

    def __process_paglet(self, pagelet, result_queue):
        try:
            pagelet_response = pagelet.render()
            if isinstance(pagelet_response, BigpipeResponse):

                content, js, css, i18n, js_effected_files, css_effected_files = pagelet_response.content_loader.load_content(pagelet.target, self.processed_js_files, self.processed_css_files)
                self.processed_js_files = self.processed_js_files + js_effected_files
                self.processed_css_files = self.processed_css_files + css_effected_files
                result_queue.put(pagelet_response.__get_pagelet_content(pagelet.target, content, js, css, i18n))
            else:
                logging.warning('for pagelets expected only bigpipe response to operate, will return response content. {}'.format(pagelet_response))
                result_queue.put(pagelet_response)
        except BaseException as ex:
            result_queue.put(ex)

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


