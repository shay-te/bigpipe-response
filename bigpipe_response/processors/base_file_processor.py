import logging
import os
import re
from abc import abstractmethod
from collections import Iterable

from bigpipe_response.remote.js_processor_client import JSRemoteClient
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from bigpipe_response.decorators import Debounce
from bigpipe_response.processors.base_processor import BaseProcessor


class BaseFileProcessor(BaseProcessor):

    # example values: source_ext: scss, target_ext: css
    def __init__(self, processor_name: str, code_base_directories: list, source_ext: list, target_ext: str, exclude_dir=None):
        BaseProcessor.__init__(self, processor_name, target_ext)

        if not source_ext or not target_ext:
            raise ValueError('"source_ext" and "target_ext" must be set.')

        if not isinstance(source_ext, Iterable) or not isinstance(target_ext, str):
            raise ValueError('"source_ext" should be a list and "target_ext" should be a string')

        if not code_base_directories:
            raise ValueError('code_base_directories cannot be None')

        if not isinstance(code_base_directories, Iterable):
            raise ValueError('code_base_directories need to be a list of paths to scan')

        self.logger = logging.getLogger(self.__class__.__name__)
        self.code_base_directories = code_base_directories
        self.source_ext = source_ext
        self.target_ext = target_ext
        self.exclude_dir = exclude_dir

        self._component_to_file = {}
        self._component_to_virtual = {}
        self._processed_files = []
        self.is_production_mode = None

        for i in range(len(self.code_base_directories)):  # Omegaconf resolvers will be  will translated this way
            code_base_directory = self.code_base_directories[i]
            if os.path.isdir(code_base_directory):
                self.__scan_folder(code_base_directory)
            else:
                raise ValueError('processor "{}". the code_base_directory "{}" dose not exists'.format(self.processor_name, code_base_directory))

    def on_start(self, js_remote_client: JSRemoteClient, is_production_mode: bool, output_dir: str):
        if not is_production_mode:
            self.observer = Observer()
            for i in range(len(self.code_base_directories)):  # Omegaconf resolvers will be  will translated this way
                code_base_directory = self.code_base_directories[i]
                self.observer.schedule(SourceChangesHandler(self), path=code_base_directory, recursive=True)
            self.observer.start()

    def validate_input(self, source: str):
        super().validate_input(source)

        if not re.match('^[A-Za-z0-9_-]*$', source):
            raise ValueError('Component by source: [{}]. only string that contains letters, numbers, underscores and dashes are allowed'.format(source))

        if source not in self._component_to_file:
            raise ValueError('render_source: "{}". is not registerd in processor "{}". The folder {} was scanned. but by name "{}" dose not exists. '.format(source, self.processor_name, self.code_base_directories, source))

        input_file = self._component_to_file[source]
        if not os.path.isfile(input_file):
            raise ValueError('File dose not exist. render_source "{}" is pointing to file "{}".'.format(source, input_file))

    def process_source(self, source: str, options: dict = {}, include_dependencies: list = [], exclude_dependencies: list = []):
        input_file = self._component_to_file[source]
        output_file = self.build_output_file_path(os.path.basename(input_file), include_dependencies, exclude_dependencies)

        if not self.is_production_mode:
            self._processed_files.append(output_file)

        return input_file, output_file

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
    def on_shutdown(self):
        self._clear()

    def is_component_registered(self, component_name):
        return True if component_name in self._component_to_file else False

    def is_component_virtual(self, component_name):
        return True if component_name in self._component_to_virtual else False

    def register_component(self, component_name: str, path: str, is_virtual: bool = False):
        self._component_to_file[component_name] = path
        if is_virtual:
            self._component_to_virtual[component_name] = is_virtual

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
