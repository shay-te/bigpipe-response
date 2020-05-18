import logging
import os

from hydra.utils import get_class
from omegaconf import DictConfig, OmegaConf
from bigpipe_response.bigpipe_render_options import BigpipeRenderOptions
from bigpipe_response.conf.bigpipe_settings import BigpipeSettings
from bigpipe_response.javascript_manager import JavascriptManager


class Bigpipe(object):

    __instance = None

    def __init__(self, config: DictConfig, processors: list):
        self.logger = logging.getLogger(self.__class__.__name__)

        #
        # config
        #
        default_config = OmegaConf.load(os.path.join(os.path.dirname(__file__), 'conf', 'bigpipe.yaml'))
        self.conf = OmegaConf.merge(default_config, config)
        BigpipeSettings.validate_settings(self.conf)


        #
        # Set render default options
        #
        self.default_render_option = BigpipeRenderOptions(
            js_processor_name=self.conf.javascript.default_processor,
            css_processor_name=self.conf.css.default_processor,
            i18n_processor_name=self.conf.i18n.default_processor,
            js_bundle_link_dependencies=self.conf.javascript.bundle_link_dependencies,
            js_dom_bind=get_class(self.conf.javascript.dom_bind)(),
            css_bundle_link_dependencies=self.conf.css.bundle_link_dependencies,
            css_complete_dependencies_by_js=self.conf.css.complete_dependencies_by_js,
        )

        #
        # Install js dependencies
        #
        self.logger.info("Installing javascript dependencies.")
        javascript_manager = JavascriptManager(self.conf)
        self.javascript_folder = javascript_manager.javascript_folder
        #
        # processors manager
        #
        from bigpipe_response.processors_manager import ProcessorsManager
        self.processors_manager = ProcessorsManager(self.conf, self.javascript_folder, processors)

        self.logger.info("Bigpipe Response Ready.")

    @staticmethod
    def init(config: DictConfig, processors: list = []):
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

