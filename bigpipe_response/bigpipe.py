import logging
import os
from shutil import copyfile

from omegaconf import OmegaConf

from bigpipe_response import utils
from bigpipe_response.bigpipe_render_options import BigpipeRenderOptions
from bigpipe_response.conf.bigpipe_settings import BigpipeSettings


class Bigpipe(object):

    __instance = None

    def __init__(self, config: OmegaConf, processors: list):
        BigpipeSettings.validate_settings(config)

        self.conf = config
        self.logger = logging.getLogger(self.__class__.__name__)

        #
        # Set render default options
        #
        self.default_render_option = BigpipeRenderOptions(
            js_processor_name=self.conf.processors.js.name,
            css_processor_name=self.conf.processors.css.name,
            i18n_processor_name=self.conf.processors.i18n.name,
            js_bundle_link_dependencies=self.conf.processors.js.bundle_link_dependencies,
            css_bundle_link_dependencies=self.conf.processors.css.bundle_link_dependencies,
            css_complete_dependencies_by_js=self.conf.processors.css.complete_dependencies_by_js,
            javascript_dom_bind=utils.get_class(self.conf.processors.js.javascript_dom_bind)(),
        )

        #
        # processors manager
        #
        from bigpipe_response.processors_manager import ProcessorsManager

        self.processors_manager = ProcessorsManager(self.conf, processors)



    @staticmethod
    def init(config: OmegaConf, processors: list = []):
        if Bigpipe.__instance is None:
            Bigpipe.__instance = Bigpipe(config, processors)

    @staticmethod
    def get():
        if Bigpipe.__instance is None:
            raise NameError("Bigpipe not initialized")
        return Bigpipe.__instance

    def shutdown(self):
        self.processors_manager.shutdown()

    @property
    def processors(self):
        return self.processors_manager

    @property
    def config(self):
        return self.conf

    def get_render_option(self, render_option: BigpipeRenderOptions):
        if render_option:
            # Fill default values where None
            for key, value in self.default_render_option.__dict__.items():
                option_value = getattr(render_option, key)
                if option_value is None:
                    setattr(render_option, key, value)
            return render_option
        return self.default_render_option

