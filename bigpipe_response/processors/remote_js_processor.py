import logging
import pkg_resources
from bigpipe_response.processors.base_file_processor import BaseFileProcessor
from bigpipe_response.remote.remote_client_server import RemoteClientServer


class RemoteJsProcessor(BaseFileProcessor):

    def __init__(self, processor_name: str, remote_client_server: RemoteClientServer, processor_js_resource: str, is_production: bool, code_base_directories: list, output_directory: str, source_ext_list: list, target_ext: str, exclude_dir=None):
        BaseFileProcessor.__init__(self, processor_name, is_production, code_base_directories, output_directory, source_ext_list, target_ext, exclude_dir=exclude_dir)

        self.resource_path, self.resource_name = RemoteJsProcessor.build_js_resource(processor_js_resource)

        if not processor_js_resource:
            raise ValueError('processor_js_resource must be set')
        if not pkg_resources.resource_exists(self.resource_path, self.resource_name):
            raise ValueError('processor_js_resource must dose not exists')

        self.logger = logging.getLogger(self.__class__.__name__)
        self.processor_name = processor_name
        self.remote_client_server = remote_client_server

    @staticmethod
    def build_js_resource(resource):
        arr = resource.rsplit('.', 2)
        return arr[0], '{}.{}'.format(arr[1], arr[2])

    def get_processor_js_as_string(self):
        return pkg_resources.resource_string(self.resource_path, self.resource_name)

    def process_resource(self, input_file: str, output_file: str, include_dependencies: list, exclude_dependencies: list, options: dict = {}):
        include_files = []
        for include_file in include_dependencies:
            include_files.append(self._component_to_file[include_file])
        return self.remote_client_server.send_process_file(self.processor_name, input_file, output_file, include_files, exclude_dependencies, options)

    def render_resource(self, input_file: str, context: dict, i18n: dict):
        return self.remote_client_server.send_render_file(self.processor_name, input_file, context, i18n)
