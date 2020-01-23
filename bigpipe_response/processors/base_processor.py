import os
from abc import abstractmethod

from bigpipe_response.processors.processor_result import ProcessorResult
from bigpipe_response.remote.js_processor_client import JSRemoteClient


#
# This is the most base processor available for BigpipeResponse
# here we can see the basic functionalities of all processors
#
class BaseProcessor(object):

    def __init__(self, processor_name: str, target_ext: str):
        if not target_ext:
            raise ValueError('target_ext must be set')

        self.processor_name = processor_name
        self.target_ext = target_ext
        self.is_production_mode = None
        self._output_file_to_effected_files = {}

    #
    # source: what is the source we are transforming into the output_file
    # output_file: calculated file path, where to write the processed data
    # include_dependencies: dependencies to include in the output_File
    # exclude_dependencies: dependencies to exclude from the output_file
    # options: dict with special instructions for this processor
    # returns: list of effected files.
    #
    @abstractmethod
    def process_resource(self, source, output_file: str, include_dependencies: list, exclude_dependencies: list, options: dict = {}):
        pass

    #
    # source: what is the source we are transforming into a string
    # context: data to be included into the transformed string
    # i18n: internalisation data to include in the transformed string
    #
    # returns: the rendered source
    #
    @abstractmethod
    def render_resource(self, source, context: dict, i18n: dict):
        pass

    #
    # validate_input called with the source parameter before any call to  `process_resource` or `render_resource`
    #
    def validate_input(self, source: str):
        if not source:
            raise ValueError('Component by, source: [{}]. cannot be blank')

    #
    # called before `process_resource`
    # this method and will process the input if necessary and generate the `output_file` parameter
    #
    # returns: processed source, output_file
    #
    def process_source(self, source: str, options: dict = {}, include_dependencies: list = [], exclude_dependencies: list = []):
        return source, self.build_output_file_path(source, include_dependencies, exclude_dependencies)

    #
    # called by bigpipe_response engine. this method will
    # 1. validate the input
    # 2. process the source (if necessary) and generate the `output_file` parameter
    # 3. will determinate if to call to `process_source` method or use previous `output_file`
    #    the `process_resource`  is using the cache when 2 terms are met
    #    a. the `output_file` already exists
    #    b. the `effected_files` for that `output_file` are cached in memory (self._output_file_to_effected_files)
    #       the variable `self._output_file_to_effected_files` is not persistent stored any where
    #       !! this means for first run, bigpipe_response will always run the `process_resource` method
    #
    # return ProcessorResult object the contains, the effected_files and the output_file
    #
    def run(self, source: str, options: dict = {}, include_dependencies: list = [], exclude_dependencies: list = []):
        self.validate_input(source)

        processed_source, output_file = self.process_source(source, options, include_dependencies, exclude_dependencies)

        if output_file not in self._output_file_to_effected_files or not os.path.isfile(output_file):
            effected_files = self.process_resource(processed_source, output_file, include_dependencies, exclude_dependencies, options)
            self._output_file_to_effected_files[output_file] = effected_files
        else:
            effected_files = self._output_file_to_effected_files[output_file]

        return ProcessorResult(effected_files, output_file)

    #
    # called by bigpipe_response engine. this method will
    #
    def render(self, source: str, context: dict, i18n: dict):
        self.validate_input(source)

    #
    # after Bigipe is initialized this event will be called on all processors.
    # js_remote_client: an interface for the remote js server with basic method to.
    #   a. register_processor_handler. register javascript handler related to this processor in the remote js server
    #   b. is_production_mode. true/false of Bigpipe is configured with production mode
    #   c. where this processor is storing output_files
    def on_start(self, js_remote_client: JSRemoteClient, is_production_mode: bool, output_dir: str):
        pass

    #
    # after Bigipe.shutdown() is called. bigpipe will shutdown all processors before shutting down the remote server
    #
    def on_shutdown(self):
        pass

    #
    # internal call to `on_start`. this will cache the js_remote_client, is_production_mode, output_dir
    # in the processor the user wont have to
    #
    def _start(self, js_remote_client: JSRemoteClient, is_production_mode: bool, output_dir: str):
        self.js_remote_client = js_remote_client
        self.is_production_mode = is_production_mode
        self.output_dir = output_dir
        self.on_start(js_remote_client, is_production_mode, output_dir)

    #
    # internal call to `on_shutdown`.
    #
    def _shutdown(self):
        self.on_shutdown()

    #
    # used by `process_source`/`process_source` method to generate the output filename format
    #
    def build_output_file_path(self, input_file_name: str, include_dependencies: list = [], exclude_dependencies: list = []):
        return os.path.join(self.output_dir, '{}.__.{}.__.{}-{}.{}'.format(input_file_name, self.processor_name, self.__dependencies_to_hash(include_dependencies), self.__dependencies_to_hash(exclude_dependencies), self.target_ext))

    #
    # in the future bigpipe will make sure that pagelet will not use the same dependencies.
    #
    def __dependencies_to_hash(self, dependencies_list: list):
        # return hashlib.blake2b(str(dependencies_list).encode(), digest_size=5).hexdigest() if dependencies_list else '_' NOT YET SUPPORTED
        return '_'

