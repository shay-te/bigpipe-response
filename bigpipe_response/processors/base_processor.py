import os
from abc import abstractmethod

from bigpipe_response.remote.remote_client_server import RemoteClientServer

from bigpipe_response.bigpipe import Bigpipe


class BaseProcessor(object):

    def __init__(self, processor_name: str, target_ext: str):
        if not target_ext:
            raise ValueError('target_ext must be set')

        self.processor_name = processor_name
        self.target_ext = target_ext

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

    def run(self, source: str, options: dict = {}, include_dependencies: list = [], exclude_dependencies: list = []):
        self.validate_input(source)

    def render(self, source: str, context: dict, i18n: dict):
        self.validate_input(source)

    def on_start(self, remote_client_server: RemoteClientServer, is_production_mode: bool, output_dir: str):
        pass

    def on_shutdown(self):
        pass

    def _start(self, remote_client_server, is_production_mode, output_dir):
        self.output_dir = output_dir
        self.on_start(remote_client_server, is_production_mode, output_dir)

    def _shutdown(self):
        self.on_shutdown()

    def build_output_file_path(self, input_file_name: str, include_dependencies: list = [], exclude_dependencies: list = []):
        return os.path.join(self.output_dir, '{}_{}.{}-{}.{}'.format(input_file_name, self.processor_name, self.__dependencies_to_hash(include_dependencies), self.__dependencies_to_hash(exclude_dependencies), self.target_ext))

    def __dependencies_to_hash(self, dependencies_list: list):
        # return hashlib.blake2b(str(dependencies_list).encode(), digest_size=5).hexdigest() if dependencies_list else '_' NOT YET SUPPORTED
        return '_'

