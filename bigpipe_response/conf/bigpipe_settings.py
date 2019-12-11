import os

from bigpipe_response.conf import default_settings
from bigpipe_response.exceptions import InvalidConfiguration
from bigpipe_response.javascript_dom_bind.javascript_dom_bind import JavascriptDOMBind


class BigpipeSettings:

    def __init__(self, settings_module_path):
        if not os.path.isfile(settings_module_path):
            raise  InvalidConfiguration('configuration module dose not exists [{}]'.format(settings_module_path))

        # update this dict from global settings (but only for ALL_CAPS settings)
        for setting in dir(default_settings):
            if setting.isupper():
                setattr(self, setting, getattr(default_settings, setting))

        # store the settings module in case someone later cares
        self.SETTINGS_MODULE = 'bigpipe_module'

        import importlib.util
        spec = importlib.util.spec_from_file_location(self.SETTINGS_MODULE, settings_module_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        self._explicit_settings = set()
        for setting in dir(mod):
            if setting.isupper():
                setting_value = getattr(mod, setting)

                setattr(self, setting, setting_value)
                self._explicit_settings.add(setting)

        self.__validate_settings()

    def __validate_settings(self):
        if self.CLIENT_BASE_PATH and not isinstance(self.CLIENT_BASE_PATH, list):
            raise InvalidConfiguration('CLIENT_BASE_PATH must be supplied as list')

        if not self.RENDERED_OUTPUT_PATH or not os.path.isdir(self.RENDERED_OUTPUT_PATH):
            raise InvalidConfiguration('RENDERED_OUTPUT_PATH need to be a an exists path')

        if not isinstance(self.IS_PRODUCTION_MODE, bool):
            raise InvalidConfiguration('IS_PRODUCTION_MODE must be of type boolean')

        if not self.JS_PROCESSOR_NAME:
            raise InvalidConfiguration('JS_PROCESSOR_NAME must be set')

        if not self.JS_PROCESSOR_SOURCE_EXT or not isinstance(self.JS_PROCESSOR_SOURCE_EXT, list):
            raise InvalidConfiguration('JS_PROCESSOR_SOURCE_EXT must be a populated list')

        if not self.JS_PROCESSOR_TARGET_EXT:
            raise InvalidConfiguration('JS_PROCESSOR_TARGET_EXT must be set')

        if not self.JS_PROCESSOR_HANDLER_PATH or not os.path.isfile(self.JS_PROCESSOR_HANDLER_PATH) :
            raise InvalidConfiguration('JS_PROCESSOR_HANDLER_PATH must be set to a javascript file')

        if not self.JS_PROCESSOR_HANDLER_PATH.strip().lower().endswith('.js'):
            raise InvalidConfiguration('JS_PROCESSOR_HANDLER_PATH must be with js extension.')

        if not self.JS_DOM_BIND or not isinstance(self.JS_DOM_BIND, JavascriptDOMBind):
            raise InvalidConfiguration('JS_DOM_BIND must be set and instance of JavascriptDOMBind')

        if not self.CSS_PROCESSOR_NAME:
            raise InvalidConfiguration('CSS_PROCESSOR_NAME must be set')

        if not self.CSS_PROCESSOR_SOURCE_EXT or not isinstance(self.CSS_PROCESSOR_SOURCE_EXT, list):
            raise InvalidConfiguration('CSS_PROCESSOR_SOURCE_EXT must be a populated list')

        if not self.CSS_PROCESSOR_TARGET_EXT:
            raise InvalidConfiguration('CSS_PROCESSOR_TARGET_EXT must be set')

        if self.CSS_COMPLETE_DEPENDENCIES_BY_JS is None:
            raise InvalidConfiguration('CSS_COMPLETE_DEPENDENCIES_BY_JS must be set to boolean')

        if self.CSS_LINK_BUNDLE_DEPENDENCIES is None:
            raise InvalidConfiguration('CSS_LINK_BUNDLE_DEPENDENCIES must be set to boolean')

        if not self.I18N_PROCESSOR_NAME:
            raise InvalidConfiguration('I18N_PROCESSOR_NAME must be set')

        if not self.JS_SERVER_PORT_START:
            raise InvalidConfiguration('JS_SERVER_PORT_START must be set to a port number')

        if not self.JS_SERVER_PORT_COUNT:
            raise InvalidConfiguration('JS_SERVER_PORT_START must be set to number of ports to scan')

    def __repr__(self):
        return '<%(cls)s "%(settings_module)s">' % {
            'cls': self.__class__.__name__,
            'settings_module': self.SETTINGS_MODULE,
        }

