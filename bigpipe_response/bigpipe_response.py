import enum
import json
import logging
import queue
import sys
import threading
import traceback

from django.http import StreamingHttpResponse
from django.http.response import HttpResponseBase

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

            for entry_content in self.__build_bigpipe_data_main_yield(content_result):
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
                content_result_pagelet = que.get()

                if not isinstance(content_result_pagelet, ContentResult):
                    content_result_pagelet_type = type(content_result_pagelet) if content_result_pagelet else None
                    self.logger.error('expected `ContentResult` got `{}` return for pagelet path `{}`'.format(content_result_pagelet_type, self.request.path))
                    if isinstance(content_result_pagelet, HttpResponseBase):
                        raise ValueError('Expected `ContentResult`, got `HttpResponseBase` instead')
                    raise content_result_pagelet

                bigpipe_paglet_data = content_result_pagelet.to_dict(pagelet.target)
                # Handle depends_on
                # When depends_on flag is set, the result will be cached and pushed only after the dependency is loaded
                target = bigpipe_paglet_data['target']
                if target in dependencies:
                    dependent_target = dependencies.get(target)
                    if dependent_target not in yield_paglets:
                        yield_later.setdefault(dependent_target, []).append(bigpipe_paglet_data)
                        continue

                yield_paglets.append(target)
                yield self._render_paglet_content(bigpipe_paglet_data)

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
                    yield self._render_paglet_content(content_result_error.to_dict(last_pagelet_target))
                else:
                    for entry_content in self.__build_bigpipe_data_main_yield(content_result_error):
                        yield entry_content
            else:
                raise ex

        yield '</body></html>\n'

    def __process_paglet(self, pagelet, result_queue):
        try:
            pagelet_response = pagelet.render()
            if isinstance(pagelet_response, BigpipeResponse):
                # 1. execute, and get the pagelet content.
                content_result = pagelet_response.content_loader.load_content(pagelet.target, self.processed_js_files, self.processed_css_files)

                # 2. build and collect ignore list of loaded. since the main request initiated.
                self.processed_js_files = self.processed_js_files + content_result.js_effected_files
                self.processed_css_files = self.processed_css_files + content_result.css_effected_files

                # 3. build pagelet as bigpipe data
                result_queue.put(content_result)
            else:
                logging.error('Pagelet response for target `{}` is not of type `BigpipeResponse`, will return response content. {}'.format(pagelet.target, pagelet_response))
                result_queue.put(pagelet_response)
        except BaseException as ex:
            result_queue.put(ex)

    #
    # Yield content
    #
    def __build_bigpipe_data_main_yield(self, content_result: ContentResult):
        if content_result.content:
            yield content_result.content
        if content_result.i18n:
            yield '\n<script>\n\trenderI18n({})\n</script>\n'.format(json.dumps(content_result.i18n))
        if content_result.css:
            yield '\n<style>\n\t{}\n</style>\n'.format(content_result.css)
        if content_result.js:
            yield '\n<script>\n\t{}\n</script>\n'.format(content_result.js)

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

