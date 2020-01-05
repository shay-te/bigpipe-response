import os
from abc import abstractmethod

from bigpipe_response.processors.processor_result import ProcessorResult
from bigpipe_response.remote.js_processor_client import JSRemoteClient


class BaseProcessor(object):

    def __init__(self, processor_name: str, target_ext: str):
        if not target_ext:
            raise ValueError('target_ext must be set')

        self.processor_name = processor_name
        self.target_ext = target_ext
        self.is_production_mode = None
        self._output_file_to_effected_files = {}
        self._processed_files = []


    def get_name(self):
        return self.processor_name

    @abstractmethod
    def process_resource(self, input_file: str, output_file: str, include_dependencies: list, exclude_dependencies: list, options: dict = {}):
        pass

    @abstractmethod
    def render_resource(self, input_file: str, context: dict, i18n: dict):
        pass

    def validate_input(self, source: str):
        if not source:
            raise ValueError('Component by, source: [{}]. cannot be blank')

    def process_source(self, source: str, options: dict = {}, include_dependencies: list = [], exclude_dependencies: list = []):
        return source, self.build_output_file_path(source, include_dependencies, exclude_dependencies)

    def run(self, source: str, options: dict = {}, include_dependencies: list = [], exclude_dependencies: list = []):
        self.validate_input(source)

        processed_source, output_file = self.process_source(source, options, include_dependencies, exclude_dependencies)

        if output_file not in self._output_file_to_effected_files or not os.path.isfile(output_file):
            effected_files = self.process_resource(processed_source, output_file, include_dependencies, exclude_dependencies, options)
            self._output_file_to_effected_files[output_file] = effected_files
        else:
            effected_files = self._output_file_to_effected_files[output_file]

        return ProcessorResult(effected_files, output_file)

    def render(self, source: str, context: dict, i18n: dict):
        self.validate_input(source)

    def on_start(self, js_remote_client: JSRemoteClient, is_production_mode: bool, output_dir: str):
        pass

    def on_shutdown(self):
        pass

    def _start(self, js_remote_client: JSRemoteClient, is_production_mode: bool, output_dir: str):
        self.js_remote_client = js_remote_client
        self.is_production_mode = is_production_mode
        self.output_dir = output_dir
        self.on_start(js_remote_client, is_production_mode, output_dir)

    def _shutdown(self):
        self.on_shutdown()

    def build_output_file_path(self, input_file_name: str, include_dependencies: list = [], exclude_dependencies: list = []):
        return os.path.join(self.output_dir, '{}.__.{}.__.{}-{}.{}'.format(input_file_name, self.processor_name, self.__dependencies_to_hash(include_dependencies), self.__dependencies_to_hash(exclude_dependencies), self.target_ext))

    def __dependencies_to_hash(self, dependencies_list: list):
        # return hashlib.blake2b(str(dependencies_list).encode(), digest_size=5).hexdigest() if dependencies_list else '_' NOT YET SUPPORTED
        return '_'

