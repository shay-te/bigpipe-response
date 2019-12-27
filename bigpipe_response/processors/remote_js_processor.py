from bigpipe_response.remote.remote_client_server import RemoteClientServer

from bigpipe_response.processors.base_processor import BaseProcessor


class RemoteJsProcessor(BaseProcessor):

    def __init__(self, processor_name: str, processor_js_resource: str):
        BaseProcessor.__init__(self, processor_name, 'js')
        self.processor_js_resource = processor_js_resource
        self.remote_client_server = None

    def on_start(self, remote_client_server: RemoteClientServer, is_production_mode: bool, output_dir: str):
        self.remote_client_server = remote_client_server
        self.remote_client_server.register_processor_handler(self.processor_name, self.processor_js_resource)

    def process_resource(self, input_file: str, output_file: str, include_dependencies: list, exclude_dependencies: list, options: dict = {}):
        return self.remote_client_server.send_process_file(self.processor_name, input_file, output_file, include_dependencies, exclude_dependencies, options)

    def render_resource(self, input_file: str, context: dict, i18n: dict):
        return self.remote_client_server.send_render_file(self.processor_name, input_file, context, i18n)
