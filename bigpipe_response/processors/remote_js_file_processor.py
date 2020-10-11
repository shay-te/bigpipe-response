from bigpipe_response.processors.base_file_processor import BaseFileProcessor
from bigpipe_response.remote.js_processor_client import JSRemoteClient


class RemoteJsFileProcessor(BaseFileProcessor):

    def __init__(self, processor_name: str, javascript_handler: str, source_paths: list, source_ext: list, target_ext: str, exclude_dir=None):
        BaseFileProcessor.__init__(self, processor_name, source_paths, source_ext, target_ext, exclude_dir=exclude_dir)
        self.javascript_handler = javascript_handler

    def on_start(self, js_remote_client: JSRemoteClient, is_production_mode: bool, output_dir: str):
        BaseFileProcessor.on_start(self, js_remote_client, is_production_mode, output_dir)
        self.js_remote_client.register_processor_handler(self.processor_name, self.javascript_handler)

    def process_resource(self, input_file: str, output_file: str, include_dependencies: list, exclude_dependencies: list, options: dict = {}):
        include_files = []
        for include_file in include_dependencies:
            include_files.append(self._component_to_file[include_file])
        return self.js_remote_client.process_resource(self.processor_name, input_file, output_file, include_files, exclude_dependencies, options)

    def render_resource(self, input_file: str, context: dict, i18n: dict):
        return self.js_remote_client.render_resource(self.processor_name, input_file, context, i18n)
