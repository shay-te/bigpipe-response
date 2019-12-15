import os
from abc import abstractmethod


class BaseProcessor(object):

    def __init__(self, processor_name: str, is_production: bool, output_directory: str):
        if not processor_name or not isinstance(processor_name, str):
            raise ValueError('processor_name cannot be blank')

        if not output_directory or not os.path.isdir(output_directory):
            raise ValueError('output_directory must be a existing directory')

        self.processor_name = processor_name
        self.is_production = is_production
        self.output_directory = os.path.join(output_directory, processor_name)

        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

    def get_name(self):
        return self.processor_name

    @abstractmethod
    def process_resource(self, input_file: str, output_file: str, include_dependencies: list, exclude_dependencies: list, options: dict = {}):
        pass

    @abstractmethod
    def render_resource(self, input_file, context, i18n):
        pass

    def validate_input(self, source: str):
        if not source:
            raise ValueError('Component by, source: [{}]. cannot be blank')

    def run(self, source: str, options: dict = {}, include_dependencies: list = [], exclude_dependencies: list = []):
        self.validate_input(source)

    def render(self, source: str, context: dict, i18n: dict):
        self.validate_input(source)

    def on_shutdown(self):
        pass

    def _shutdown(self):
        self.on_shutdown()

    def build_output_file_path(self, output_file_name: str, target_extension: str, include_dependencies: list = [], exclude_dependencies: list = []):
        output_file_name = '{}.{}-{}.{}'.format(output_file_name, self.__dependencies_to_hash(include_dependencies), self.__dependencies_to_hash(exclude_dependencies), target_extension)
        return os.path.join(self.output_directory, output_file_name)

    def __dependencies_to_hash(self, dependencies_list: list):
        # return hashlib.blake2b(str(dependencies_list).encode(), digest_size=5).hexdigest() if dependencies_list else '_' NOT YET SUPPORTED
        return '_'
