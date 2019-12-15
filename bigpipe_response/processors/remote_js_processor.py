import logging
import os
import pkg_resources
from bigpipe_response.processors.base_file_processor import BaseFileProcessor
from bigpipe_response.remote.remote_client_server import RemoteClientServer

def split_path(resource):
    idx = resource.rfind("/")
    if idx == -1:
        path = ""
        filename = resource
    else:
        path = resource[0 : idx]
        filename = resource[idx + 1:]
    return path, filename


class RemoteJsProcessor(BaseFileProcessor):

    def __init__(self, processor_name: str, remote_client_server: RemoteClientServer, processor_js_handler_path: str, is_production: bool, code_base_directories: list, output_directory: str, source_ext_list: list, target_ext: str, exclude_dir=None):
        BaseFileProcessor.__init__(self, processor_name, is_production, code_base_directories, output_directory, source_ext_list, target_ext, exclude_dir=exclude_dir)
        if not processor_js_handler_path:
            raise ValueError('processor_js_handler_path must be set')
        # if not os.path.isfile(processor_js_handler_path):
        #     raise ValueError('processor_js_handler_path must dose not exists')

        path, filename = split_path(processor_js_handler_path)
        if not pkg_resources.resource_exists(path, filename):
            raise ValueError('processor_js_handler_path must dose not exists')

        jsfile = pkg_resources.resource_string(path, filename)

        self.logger = logging.getLogger(self.__class__.__name__)
        self.processor_name = processor_name
        self.remote_client_server = remote_client_server
        self.processor_js_handler_path = jsfile #3processor_js_handler_path

    def get_processor_js_handler_path(self):
        return self.processor_js_handler_path

    def process_resource(self, input_file: str, output_file: str, include_dependencies: list, exclude_dependencies: list, options: dict = {}):
        include_files = []
        for include_file in include_dependencies:
            include_files.append(self._component_to_file[include_file])
        return self.remote_client_server.send_process_file(self.processor_name, input_file, output_file, include_files, exclude_dependencies, options)

    def render_resource(self, input_file: str, context: dict, i18n: dict):
        return self.remote_client_server.send_render_file(self.processor_name, input_file, context, i18n)
