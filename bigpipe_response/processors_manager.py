import logging
import os

from bigpipe_response.bigpipe import Bigpipe
from omegaconf import OmegaConf

from bigpipe_response.conf.bigpipe_settings import BigpipeSettings
from bigpipe_response.processors.base_file_processor import BaseFileProcessor
from bigpipe_response.processors.base_processor import BaseProcessor
from bigpipe_response.processors.i18n_processor import I18nProcessor
from bigpipe_response.processors.remote_js_file_processor import RemoteJsFileProcessor


class ProcessorsManager(object):
    def __init__(self, conf, processors: list = []):
        self.conf = conf
        self.logger = logging.getLogger(self.__class__.__name__)

        # set output directory
        self.output_dir = os.path.normpath(os.path.join(self.conf.rendered_output_path, self.conf.rendered_output_container))
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        self.virtual_source_dir = os.path.join(self.output_dir, "temp_virtual_source")
        if not os.path.exists(self.virtual_source_dir):
            os.makedirs(self.virtual_source_dir)


        # Bundle dependencies
        self.logger.info("Settings up processors.")
        self.__processors = {
            **self.__generate_default_processors(),
            **{processor.processor_name: processor for processor in processors},
        }
        for proc_name, processor in self.__processors.items():
            if not isinstance(processor, BaseProcessor):
                raise ValueError("processor must be a baseclass of 'BaseProcessor'. Got: {} ".format(processor.__class__.__name__))
            self.make_processor_dir(proc_name)


    def filter_unregistered_dependencies(self, proc_name: str, dependencies: list):
        if not proc_name in self.__processors:
            raise ValueError("processor by name [{}] dose not exists.".format(proc_name))
        if not isinstance(self.__processors[proc_name], BaseFileProcessor):
            raise ValueError("processor by name [{}] must be of type BaseFileProcessor.".format(proc_name)
            )
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
            # 1 only BaseFileProcessor are supported
            # 2 there is nothing to do in case of source file not exists ant no dependencies to import
            # 3 register the new generated missing source
            # 4 process the source

            if not isinstance(processor, BaseFileProcessor):
                raise ValueError("generate_missing_source option supports only BaseFileProcessor")

            if not processor.is_component_registered(input):
                if not include_dependencies:
                    raise ValueError("generate_missing_source was set and include_dependencies is empty, nothing to do")

                processor.register_component(input, self.__generate_processor_input(proc_name, "{}.{}".format(input, processor.target_ext)),)

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

    def __generate_default_processors(self):
        from bigpipe_response.processors.css_processor import CSSProcessor
        from bigpipe_response.processors.remote_js_processor import RemoteJsProcessor
        
        jsx_processor = RemoteJsFileProcessor(
            self.conf.processors.js.name,
            self.conf.processors.js.javascript_handler,
            OmegaConf.to_container(self.conf.processors.js.source_path, resolve=True),
            list(self.conf.processors.js.source_ext),
            self.conf.processors.js.target_ext,
            exclude_dir='node_modules')

        module_processor = RemoteJsProcessor(
            self.conf.processors.js_modules.name,
            self.conf.processors.js.javascript_handler)

        css_processor = CSSProcessor(
            self.conf.processors.css.name,
            OmegaConf.to_container(self.conf.processors.css.source_path, resolve=True),
            list(self.conf.processors.css.source_ext),
            self.conf.processors.css.target_ext)

        i18n_processor = I18nProcessor(self.conf.processors.i18n.name)

        return {
            # js
            jsx_processor.processor_name: jsx_processor,
            module_processor.processor_name: module_processor,
            # css
            css_processor.processor_name: css_processor,
            # i18n
            i18n_processor.processor_name: i18n_processor,
        }

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

    def make_processor_dir(self, processor_name: str):
        output_directory = os.path.join(self.output_dir, Bigpipe.get().config.rendered_output_path, Bigpipe.get().config.rendered_output_container, processor_name)
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        return output_directory