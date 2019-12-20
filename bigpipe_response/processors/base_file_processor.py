import logging
import os
import re
from abc import abstractmethod

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from bigpipe_response.bigpipe import Bigpipe
from bigpipe_response.decorators import Debounce
from bigpipe_response.processors.base_processor import BaseProcessor
from bigpipe_response.processors.processor_result import ProcessorResult


class BaseFileProcessor(BaseProcessor):

    # example values: source_ext: scss, target_ext: css
    def __init__(self, processor_name: str, code_base_directories: list, source_ext: list, target_ext: str, exclude_dir=None):
        BaseProcessor.__init__(self, processor_name, target_ext)

        if not source_ext or not target_ext:
            raise ValueError('source and target must be set ')

        if not isinstance(source_ext, list) or not isinstance(target_ext, str):
            raise ValueError('source extensions should be a list and target extension should be a string')

        if not code_base_directories:
            raise ValueError('code_base_directories cannot be None')

        if not isinstance(code_base_directories, list):
            raise ValueError('code_base_directories need to be a list of paths to scan')

        self.logger = logging.getLogger(self.__class__.__name__)
        self.code_base_directories = code_base_directories
        self.source_ext = source_ext
        self.target_ext = target_ext
        self.exclude_dir = exclude_dir

        self._component_to_file = {}
        self._output_file_to_effected_files = {}
        self._processed_files = []

        for code_base_directory in code_base_directories:
            self.__scan_folder(code_base_directory)

        if not Bigpipe.get().config.is_production_mode:
            self.observer = Observer()
            for code_base_directory in code_base_directories:
                self.observer.schedule(SourceChangesHandler(self), path=code_base_directory, recursive=True)
            self.observer.start()

    def validate_input(self, source: str):
        super().validate_input(source)

        if not re.match('^[A-Za-z0-9_-]*$', source):
            raise ValueError('Component by source: [{}]. only string that contains letters, numbers, underscores and dashes are allowed'.format(source))

        if source not in self._component_to_file:
            raise ValueError('Component path for input: [{}] is scanned under the [{}] folder. but processed file dose not exists. '.format(source, self.code_base_directories))

        input_file = self._component_to_file[source]
        if not os.path.isfile(input_file):
            raise ValueError('Source input file: [{}]. Dose not exists'.format(input_file))

    def run(self, source: str, options: dict = {}, include_dependencies: list = [], exclude_dependencies: list = []):
        super().run(source, options, include_dependencies, exclude_dependencies)
        input_file = self._component_to_file[source]
        output_file = self.build_output_file_path(os.path.basename(input_file), include_dependencies, exclude_dependencies)

        if output_file not in self._output_file_to_effected_files or not os.path.isfile(output_file):
            effected_files = self.process_resource(input_file, output_file, include_dependencies, exclude_dependencies, options)
            self._output_file_to_effected_files[output_file] = effected_files
        else:
            effected_files = self._output_file_to_effected_files[output_file]

        if not Bigpipe.get().config.is_production_mode:
            self._processed_files.append(output_file)
        return ProcessorResult(effected_files, output_file)

    def render(self, source: str, context: dict, i18n: dict):
        super().render(source, context, i18n)
        input_file = self._component_to_file[source]
        output_file = self.build_output_file_path(os.path.basename(input_file), self.target_ext)
        if not os.path.isfile(output_file):
            self.process_resource(input_file, output_file, [], [], {})
        return self.render_resource(output_file, context, i18n)

    # Clean output files
    def _clear(self):
        self.logger.debug('File changes cleaning up all output files')
        files_not_deleted = []
        for delete_file in self._processed_files:
            if os.path.exists(delete_file):
                try:
                    os.remove(delete_file)
                    if not os.path.exists(delete_file):
                        files_not_deleted.append(delete_file)
                except OSError:
                    files_not_deleted.append(delete_file)
                    self.logger.error('Error while deleting file [{}]'.format(delete_file))

        self._processed_files = files_not_deleted

    def __scan_folder(self, code_base_directory):
        for root, dirnames, filenames in os.walk(code_base_directory):
            for file in filenames:
                if self.exclude_dir and self.exclude_dir in root:
                    continue

                file_name, file_extension = os.path.splitext(file)
                if file_extension and file_extension[0] is '.':
                    file_extension = file_extension[1::]

                if file_extension in self.source_ext:
                    if file_name not in self._component_to_file:
                        file_path = os.path.join(root, file)
                        self._component_to_file[file_name] = file_path
                    else:
                        self.logger.error('ERROR: Bigpipe SourceWatcher. {} already registered, will use first file: {}'.format(file_name, self._component_to_file[file_name]))

    # BaseProcessor files.
    def _shutdown(self):
        self._clear()
        super()._shutdown()

    def is_component_registered(self, component_name):
        return True if component_name in self._component_to_file else False

    def register_component(self, component_name, path):
        self._component_to_file[component_name] = path

    @abstractmethod
    def process_resource(self, input_file: str, output_file: str, include_dependencies: list, exclude_dependencies: list, options: dict = {}):
        pass

    @abstractmethod
    def render_resource(self, input_file, context, i18n):
        pass


class SourceChangesHandler(FileSystemEventHandler):
    def __init__(self, base_processor):
        self.base_processor = base_processor

    @Debounce(0.35)
    def on_any_event(self, event):
        self.base_processor._clear()
