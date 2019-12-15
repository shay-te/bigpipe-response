import logging
import os
from shutil import copyfile

from bigpipe_response.bigpipe_render_options import BigpipeRenderOptions
from bigpipe_response.processors_manager import ProcessorsManager
from hydra import utils

class Bigpipe(object):

    __instance = None

    def __init__(self, config, processors: list = []):
        # for idx in range(len(config.client_base_path)):
        #     config.client_base_path[idx] = utils.to_absolute_path(config.client_base_path[idx])
        # config.rendered_output_path = utils.to_absolute_path(config.rendered_output_path)

        self.conf = config
        self.logger = logging.getLogger(self.__class__.__name__)

        # set render default options
        self.default_render_option = BigpipeRenderOptions(js_processor_name=self.conf.js_processor_name,
                                                          css_processor_name=self.conf.css_processor_name,
                                                          i18n_processor_name=self.conf.i18n_processor_name,
                                                          js_link_bundle_dependencies=self.conf.js_link_bundle_dependencies,
                                                          css_link_bundle_dependencies=self.conf.css_link_bundle_dependencies,
                                                          css_complete_dependencies_by_js=self.conf.css_complete_dependencies_by_js,
                                                          javascript_dom_bind=self.conf.js_dom_bind)

        # processors manager
        self.processors_manager = ProcessorsManager(self.conf, processors)

        # install js dependencies

        javascript_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'js')
        copyfile(os.path.join(javascript_folder, 'browser', 'bigpipe.js'), os.path.join(self.conf.rendered_output_path, 'bigpipe.js'))

    @staticmethod
    def init(config, processors: list = []):
        if Bigpipe.__instance is None:
            Bigpipe.__instance = Bigpipe(config, processors=processors)

    @staticmethod
    def get():
        if Bigpipe.__instance is None:
            raise NameError('Bigpipe not initialized')
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



