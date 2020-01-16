from bigpipe_response.remote.js_processor_client import JSRemoteClient
from bigpipe_response.processors.base_processor import BaseProcessor


class RemoteJsProcessor(BaseProcessor):

    def __init__(self, processor_name: str, javascript_handler: str, target_ext: str):
        BaseProcessor.__init__(self, processor_name, target_ext)
        self.javascript_handler = javascript_handler

    def on_start(self, js_remote_client: JSRemoteClient, is_production_mode: bool, output_dir: str):
        self.js_remote_client.register_processor_handler(self.processor_name, self.javascript_handler)

    def process_resource(self, input_file: str, output_file: str, include_dependencies: list, exclude_dependencies: list, options: dict = {}):
        return self.js_remote_client.process_resource(self.processor_name, input_file, output_file, include_dependencies, exclude_dependencies, options)

    def render_resource(self, input_file: str, context: dict, i18n: dict):
        return self.js_remote_client.render_resource(self.processor_name, input_file, context, i18n)
