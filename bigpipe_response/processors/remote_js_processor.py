from bigpipe_response.processors.base_processor import BaseProcessor
from bigpipe_response.bigpipe import Bigpipe


class RemoteJsProcessor(BaseProcessor):

    def __init__(self, processor_name: str, processor_js_resource: str):
        BaseProcessor.__init__(self, processor_name, 'js')
        Bigpipe.get().remote_client_server.register_processor_handler(processor_name, processor_js_resource)

    def process_resource(self, input_file: str, output_file: str, include_dependencies: list, exclude_dependencies: list, options: dict = {}):
        return Bigpipe.get().remote_client_server.send_process_file(self.processor_name, input_file, output_file, include_dependencies, exclude_dependencies, options)

    def render_resource(self, input_file: str, context: dict, i18n: dict):
        return Bigpipe.get().remote_client_server.send_render_file(self.processor_name, input_file, context, i18n)
