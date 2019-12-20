from bigpipe_response.bigpipe import Bigpipe

from bigpipe_response.processors.base_file_processor import BaseFileProcessor


class RemoteJsFileProcessor(BaseFileProcessor):

    def __init__(self, processor_name: str, processor_js_resource: str, code_base_directories: list, source_ext_list: list, target_ext: str, exclude_dir=None):
        BaseFileProcessor.__init__(self, processor_name, code_base_directories, source_ext_list, target_ext, exclude_dir=exclude_dir)
        Bigpipe.get().remote_client_server.register_processor_handler(processor_name, processor_js_resource)

    def process_resource(self, input_file: str, output_file: str, include_dependencies: list, exclude_dependencies: list, options: dict = {}):
        include_files = []
        for include_file in include_dependencies:
            include_files.append(self._component_to_file[include_file])
        return Bigpipe.get().remote_client_server.send_process_file(self.processor_name, input_file, output_file, include_files, exclude_dependencies, options)

    def render_resource(self, input_file: str, context: dict, i18n: dict):
        return Bigpipe.get().remote_client_server.send_render_file(self.processor_name, input_file, context, i18n)
