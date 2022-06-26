import logging
import os
import re
from abc import abstractmethod
try:
    # Python <= 3.9
    from collections import Iterable
except ImportError:
    # Python > 3.9
    from collections.abc import Iterable

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from bigpipe_response.decorators import Debounce
from bigpipe_response.processors.base_processor import BaseProcessor
from bigpipe_response.remote.js_processor_client import JSRemoteClient


class BaseFileProcessor(BaseProcessor, FileSystemEventHandler):

    # example values: source_ext: scss, target_ext: css
    def __init__(self, processor_name: str, source_paths: list, source_ext: list, target_ext: str, exclude_dir=None):
        BaseProcessor.__init__(self, processor_name, target_ext)

        if not source_ext or not target_ext:
            raise ValueError('"source_ext" and "target_ext" must be set.')

        if not isinstance(source_ext, Iterable) or not isinstance(target_ext, str):
            raise ValueError('"source_ext" should be a list and "target_ext" should be a string')

        if not source_paths:
            raise ValueError('source_paths cannot be None')

        if not isinstance(source_paths, Iterable):
            raise ValueError('source_paths need to be a list of paths to scan')

        self.logger = logging.getLogger(self.__class__.__name__)
        self.source_paths = source_paths
        self.source_ext = source_ext
        self.target_ext = target_ext
        self.exclude_dir = exclude_dir

        self._component_to_file = {}
        self._component_to_virtual = {}
        self._processed_files = []
        self.is_production_mode = None

        for i in range(len(self.source_paths)):  # Omegaconf resolvers will be  will translated this way
            source_path = self.source_paths[i]
            if os.path.isdir(source_path):
                self.__register_folder(source_path)
            else:
                raise ValueError('processor `{}`. the source_paths `{}` dose not exists'.format(self.processor_name, source_path))

    def on_start(self, js_remote_client: JSRemoteClient, is_production_mode: bool, output_dir: str):
        if not is_production_mode:
            self.observer = Observer()
            for i in range(len(self.source_paths)):  # Omegaconf resolvers will be  will translated this way
                source_path = self.source_paths[i]
                self.observer.schedule(self, path=source_path, recursive=True)
            self.observer.start()

    def validate_input(self, source: str):
        super().validate_input(source)

        if not re.match('^[@A-Za-z0-9_-]*$', source):
            raise ValueError('Component by source: [{}]. only string that contains letters, numbers, at, underscores and dashes are allowed'.format(source))

        if source not in self._component_to_file:
            raise ValueError('render_source: `{}`. is not registerd in processor `{}`. The folder {} was scanned. but by name `{}` dose not exists. '.format(source, self.processor_name, self.source_paths, source))

        input_file = self._component_to_file[source]
        if not os.path.isfile(input_file):
            raise ValueError('File dose not exist. render_source `{}` is pointing to file `{}`.'.format(source, input_file))

    def process_dependencies(self, include_dependencies: list, exclude_dependencies: list):
        filtered_in = [dependency for dependency in include_dependencies if not self.is_component_virtual(dependency)]
        return filtered_in, exclude_dependencies

    def process_source(self, source: str, options: dict = {}, include_dependencies: list = [], exclude_dependencies: list = []):
        input_file = self._component_to_file[source]
        output_file = self.build_output_file_path(os.path.basename(input_file), options, include_dependencies, exclude_dependencies)

        if not self.is_production_mode:
            self._processed_files.append(output_file)

        return input_file, output_file

    def render(self, source: str, context: dict, i18n: dict):
        super().render(source, context, i18n)
        input_file = self._component_to_file[source]
        output_file = self.build_output_file_path(os.path.basename(input_file))
        if not os.path.isfile(output_file):
            self.process_resource(input_file, output_file, [], [], {})
        return self.render_resource(output_file, context, i18n)

    # Clean output files
    def _clear(self):
        self.logger.info('File changes cleaning up all output files')
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

    def __scan_folder(self, source_path, register=True):
        effected = False
        for root, dirnames, filenames in os.walk(source_path):
            for file in filenames:
                if self.exclude_dir and self.exclude_dir in root:
                    continue

                if register:
                    local_effected = self.__register_file(root, file)
                else:
                    local_effected = self.__unregister_file(root, file)
                if local_effected:
                    effected = True
        return effected

    def __register_folder(self, source_path):
        self.__scan_folder(source_path, True)

    def __unregister_folder(self, source_path):
        self.__scan_folder(source_path, False)

    def __register_file(self, folder, file):
        file_name, file_extension = os.path.splitext(file)
        if file_extension and file_extension[0] == '.':
            file_extension = file_extension[1::]

        if file_extension in self.source_ext:
            if file_name not in self._component_to_file:
                self._component_to_file[file_name] = os.path.join(folder, file)
                return True
            else:
                self.logger.error('ERROR: Bigpipe SourceWatcher. {} already registered, will use first file: {}'.format(file_name,
                                                                                                                        self._component_to_file[file_name]))

    def __unregister_file(self, folder, file):
        file_name, file_extension = os.path.splitext(file)
        if file_name in self._component_to_file:
            return True
            del self._component_to_file[file_name]

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

    #
    #
    # FileSystemEventHandler
    #
    #

    @Debounce(0.35)
    def on_any_event(self, event):
        self._clear()

    @Debounce(0.35)
    def on_created(self, event):
        if event.is_directory:
            if self.__register_folder(event.src_path):
                self.logger.info('Registering new folder `{}`'.format(event.src_path))
        else:
            folder = os.path.dirname(event.src_path)
            file = os.path.basename(event.src_path)
            if self.__register_file(folder, file):
                self.logger.info('Registering new file `{}`'.format(event.src_path))

    @Debounce(0.35)
    def on_deleted(self, event):
        if event.is_directory:
            if self.__unregister_folder(event.src_path):
                self.logger.info('Unregistering new folder `{}`'.format(event.src_path))

        else:
            folder = os.path.dirname(event.src_path)
            file = os.path.basename(event.src_path)
            if self.__unregister_file(folder, file):
                self.logger.info('Unregistering new file `{}`'.format(event.src_path))