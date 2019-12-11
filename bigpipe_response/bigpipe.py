import logging

from bigpipe_response.bigpipe_render_options import BigpipeRenderOptions
from bigpipe_response.conf.bigpipe_settings import BigpipeSettings
from bigpipe_response.processors_manager import ProcessorsManager


class Bigpipe(object):

    __instance = None

    def __init__(self, settings, processors: list = []):
        self.conf = BigpipeSettings(settings)
        self.logger = logging.getLogger(self.__class__.__name__)

        # set render default options
        self.default_render_option = BigpipeRenderOptions(js_processor_name=self.conf.JS_PROCESSOR_NAME,
                                                          css_processor_name=self.conf.CSS_PROCESSOR_NAME,
                                                          i18n_processor_name=self.conf.I18N_PROCESSOR_NAME,
                                                          js_link_bundle_dependencies=self.conf.JS_LINK_BUNDLE_DEPENDENCIES,
                                                          css_link_bundle_dependencies=self.conf.CSS_LINK_BUNDLE_DEPENDENCIES,
                                                          css_complete_dependencies_by_js=self.conf.CSS_COMPLETE_DEPENDENCIES_BY_JS,
                                                          javascript_dom_bind=self.conf.JS_DOM_BIND)

        self.processors_manager = ProcessorsManager(self.conf, processors)

    @staticmethod
    def init(settings, processors: list = []):
        if Bigpipe.__instance is None:
            Bigpipe.__instance = Bigpipe(settings, processors=processors)

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



