import os

from omegaconf import ListConfig, OmegaConf
from pkg_resources import resource_exists

from bigpipe_response.exceptions import InvalidConfiguration
from bigpipe_response.javascript_dom_bind.javascript_dom_bind import JavascriptDOMBind
from bigpipe_response.processors.remote_js_processor import RemoteJsProcessor



def get_class(path):
    try:
        from importlib import import_module

        module_path, _, class_name = path.rpartition(".")
        mod = import_module(module_path)
        try:
            klass = getattr(mod, class_name)
        except AttributeError:
            raise ImportError(
                "Class {} is not in module {}".format(class_name, module_path)
            )
        return klass
    except ValueError as e:
        raise e


class BigpipeSettings:

    @staticmethod
    def validate_settings(config):
        js_source_path = OmegaConf.to_container(config.js_source_path, resolve=True)
        css_source_path = OmegaConf.to_container(config.css_source_path, resolve=True)

        if js_source_path and not isinstance(js_source_path, list):
            raise InvalidConfiguration('js_source_path must be supplied as list')

        for source_base_path in js_source_path:
            if not os.path.exists(source_base_path):
                raise InvalidConfiguration('js_source_path directory dose not exists. [{}]'.format(source_base_path))

        if css_source_path and not isinstance(css_source_path, list):
            raise InvalidConfiguration('js_source_path must be supplied as list')

        for source_base_path in css_source_path:
            if not os.path.exists(source_base_path):
                raise InvalidConfiguration('css_source_path directory dose not exists. [{}]'.format(source_base_path))

        if not config.rendered_output_path or not os.path.isdir(config.rendered_output_path):
            raise InvalidConfiguration('rendered_output_path need to be a an exists path')

        if not isinstance(config.is_production_mode, bool):
            raise InvalidConfiguration('is_production_mode must be of type boolean')

        if not config.js_processor_name:
            raise InvalidConfiguration('js_processor_name must be set')

        if not config.js_processor_source_ext or not isinstance(OmegaConf.to_container(config.js_processor_source_ext, resolve=True), list):
            raise InvalidConfiguration('js_processor_source_ext must be a populated list')

        if not config.js_processor_target_ext:
            raise InvalidConfiguration('js_processor_target_ext must be set')

        if not config.js_processor_handler_path.strip().lower().endswith('.js'):
            raise InvalidConfiguration('js_processor_handler_path must be with js extension.')

        path, resource = RemoteJsProcessor.build_js_resource(config.js_processor_handler_path)

        if not config.js_processor_handler_path or not resource_exists(path, resource):
            raise InvalidConfiguration('js_processor_handler_path must be set to a javascript file')

        if JavascriptDOMBind not in get_class(config.js_dom_bind).__bases__:
            raise InvalidConfiguration('js_dom_bind must be set and instance of javascriptdombind')

        if not config.css_processor_name:
            raise InvalidConfiguration('css_processor_name must be set')

        if not config.css_processor_source_ext or not isinstance(OmegaConf.to_container(config.css_processor_source_ext, resolve=True), list):
            raise InvalidConfiguration('css_processor_source_ext must be a populated list')

        if not config.css_processor_target_ext:
            raise InvalidConfiguration('css_processor_target_ext must be set')

        if config.css_complete_dependencies_by_js is None:
            raise InvalidConfiguration('css_complete_dependencies_by_js must be set to boolean')

        if config.css_link_bundle_dependencies is None:
            raise InvalidConfiguration('css_link_bundle_dependencies must be set to boolean')

        if not config.i18n_processor_name:
            raise InvalidConfiguration('i18n_processor_name must be set')

        if not config.js_server_port_start:
            raise InvalidConfiguration('js_server_port_start must be set to a port number')

        if not config.js_server_port_count:
            raise InvalidConfiguration('js_server_port_start must be set to number of ports to scan')
