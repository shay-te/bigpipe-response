import logging
import os

from hydra.utils import instantiate
from omegaconf import DictConfig

from bigpipe_response.conf.bigpipe_settings import BigpipeSettings
from bigpipe_response.processors.base_file_processor import BaseFileProcessor
from bigpipe_response.processors.base_processor import BaseProcessor
from bigpipe_response.remote.js_processor_client import JSRemoteClient
from bigpipe_response.remote.remote_client_server import RemoteClientServer


class ProcessorsManager(object):

    def __init__(self, config: DictConfig, javascript_folder: str, processors: list = []):
        self.conf = config
        self.logger = logging.getLogger(self.__class__.__name__)
        #
        # set output directory
        #
        self.output_dir = os.path.normpath(os.path.join(self.conf.rendered_output_path, self.conf.rendered_output_container))
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        self.virtual_source_dir = os.path.join(self.output_dir, "temp_virtual_source")
        if not os.path.exists(self.virtual_source_dir):
            os.makedirs(self.virtual_source_dir)



        #
        # Remote javascript server initialize.
        #
        self.logger.info("Initialize javascript server.")

        self.remote_client_server = RemoteClientServer(javascript_folder,
                                                       self.conf.is_production_mode,
                                                       self.conf.remote.port_start,
                                                       self.conf.remote.port_count,
                                                       self.conf.remote.timeout)
        #
        # starting processors
        #
        self.logger.info("Settings up processors.")
        self.__processors = {
            **self.__generate_default_processors(),
            **{processor.processor_name: processor for processor in processors},
        }

        js_remote_client = JSRemoteClient(self.remote_client_server)
        for proc_name, processor in self.__processors.items():
            if not isinstance(processor, BaseProcessor):
                raise ValueError("processor must be a baseclass of 'BaseProcessor'. Got: {} ".format(processor.__class__.__name__))

            processor._start(js_remote_client, self.conf.is_production_mode, self.get_processor_output_dir(proc_name))

        #
        # start remote js server
        #
        self.logger.info("Starting remote javascript server.")
        self.remote_client_server.start()

    def filter_unregistered_dependencies(self, proc_name: str, dependencies: list):
        if not proc_name in self.__processors:
            raise ValueError("processor by name [{}] dose not exists.".format(proc_name))
        if not isinstance(self.__processors[proc_name], BaseFileProcessor):
            raise ValueError("processor by name [{}] must be of type BaseFileProcessor.".format(proc_name))
        proc = self.__processors[proc_name]
        return [dependency for dependency in dependencies if proc.is_component_registered(dependency)]

    def run_processor(
        self,
        proc_name: str,
        input: str,
        options: dict = {},
        include_dependencies: list = [],
        exclude_dependencies: list = [],
        generate_missing_source: bool = False,
    ):
        if not proc_name in self.__processors:
            raise ValueError("processor by name [{}] dose not exists.".format(proc_name))

        processor = self.__processors[proc_name]
        if generate_missing_source:
            # in case of generate missing source
            # 1 case BaseFileProcessor, register the new input
            # 2 there is nothing to do in case of source file not exists ant no dependencies to import
            # 3 register the new generated missing source
            # 4 process the source
            if not include_dependencies:
                raise ValueError("generate_missing_source was set and include_dependencies is empty, nothing to do")

            if isinstance(processor, BaseFileProcessor) and not processor.is_component_registered(input):
                processor.register_component(input, self.__generate_processor_input(proc_name, "{}.{}".format(input, processor.target_ext)), True)

        return self.__processors[proc_name].run(input, options, include_dependencies, exclude_dependencies)

    def render_processor(self, proc_name: str, input: str, context: dict, i18n: dict):
        BigpipeSettings.validate_folder_name(proc_name, 'processor_name')
        if not proc_name in self.__processors:
            raise ValueError("processor by name [{}] dose not exists.".format(proc_name))
        return self.__processors[proc_name].render(input, context, i18n)

    def shutdown(self):
        for key, value in self.__processors.items():
            try:
                self.__processors[key]._shutdown()
            except:
                self.logger.error("Error shutting fown processor by name [{}]".format(key))
        self.remote_client_server.shutdown()

    def __generate_default_processors(self):
        result = {}
        for proc_name, processor in self.conf.processors.items():
            try:
                result[proc_name] = instantiate(processor)
            except:
                raise ValueError('unable to instantiate processor name [{}]'.format(proc_name))
        return result

    def __generate_processor_input(self, proc_name: str, source: str):
        proc_virtual_source_dir = os.path.join(self.virtual_source_dir, proc_name)
        if not os.path.exists(proc_virtual_source_dir):
            os.makedirs(proc_virtual_source_dir)

        path = os.path.join(proc_virtual_source_dir, source)
        if not os.path.isfile(path):
            saved_umask = os.umask(0o077)
            with open(path, "w") as tmp:
                tmp.write("")
            os.umask(saved_umask)
        return path

    def get_processor_output_dir(self, processor_name: str):
        if processor_name in self.__processors:
            proc_output_dir = os.path.join(self.output_dir, processor_name)
            if not os.path.exists(proc_output_dir):
                os.makedirs(proc_output_dir)
            return proc_output_dir
        raise ValueError('cant get output directory processor is not registered by name [{}]'.format(processor_name))

