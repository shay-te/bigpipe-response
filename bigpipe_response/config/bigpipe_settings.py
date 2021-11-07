import os

from hydra.utils import get_class
from omegaconf import OmegaConf

from bigpipe_response.exceptions import InvalidConfiguration
from bigpipe_response.processors.base_file_processor import BaseFileProcessor
from bigpipe_response.processors.remote_js_file_processor import RemoteJsFileProcessor
from bigpipe_response.processors.remote_js_processor import RemoteJsProcessor


class BigpipeSettings:

    @staticmethod
    def validate_folder_name(folder_name, property_name):
        if not folder_name or not isinstance(folder_name, str):
            raise InvalidConfiguration('{} cannot be blank'.format(property_name))

        keep_characters = ('_')
        fixed_folder_name = "".join(c for c in folder_name if c.isalnum() or c in keep_characters).rstrip()
        if fixed_folder_name != folder_name:
            raise InvalidConfiguration('{} must be set to a valid folder name. no spaces, dots are allowed. suggestions: {}'.format(property_name, fixed_folder_name))

    @staticmethod
    def validate_rendered_output_path(config):
        if not config.rendered_output_path or not os.path.isdir(config.rendered_output_path):
            raise InvalidConfiguration('rendered_output_path need to be a an exists path')

    @staticmethod
    def validate_settings(config):
        BigpipeSettings.validate_rendered_output_path(config)

        BigpipeSettings.validate_folder_name(config.rendered_output_container, 'rendered_output_container')

        if not isinstance(config.is_production_mode, bool):
            raise InvalidConfiguration('is_production_mode must be of type boolean')

        from bigpipe_response.javascript_dom_bind.javascript_dom_bind import JavascriptDOMBind
        #
        # path, resource = RemoteJsProcessor.build_js_resource(config.processors.js.javascript_handler)
        # if not resource_exists(path, resource):
        #     raise InvalidConfiguration('config.processors.js.javascript_handler must be set to a javascript file')

        if JavascriptDOMBind not in get_class(config.javascript.dom_bind).__bases__:
            raise InvalidConfiguration('config.processors.js.js_dom_bind must be set and instance of JavascriptDOMBind')

        if config.css.complete_dependencies_by_js is None:
            raise InvalidConfiguration('config.processors.css.complete_dependencies_by_js must be set to boolean')

        if config.css.bundle_link_dependencies is None:
            raise InvalidConfiguration('config.processors.css.bundle_link_dependencies must be set to boolean')

        if not config.remote.port_start:
            raise InvalidConfiguration('config.processors.js.remote_port_start must be set to a port number')

        if not config.remote.port_count:
            raise InvalidConfiguration('config.processors.js.remote_port_count must be set to number of ports to scan')

        for key, conf_processors in config.processors.items():

            if 'processor_name' not in conf_processors:
                raise InvalidConfiguration('processor processor_name must be set')

            if '_target_' not in conf_processors:
                raise InvalidConfiguration('processor class must be set')

            processor_classes = get_class(conf_processors['_target_']).__bases__
            if BaseFileProcessor in processor_classes:

                if not conf_processors.source_paths:
                    raise InvalidConfiguration('processor `{}`. `source_paths` is missing'.format(conf_processors))

                source_paths = OmegaConf.to_container(conf_processors.source_paths, resolve=True)

                if source_paths and not isinstance(source_paths, list):
                    raise InvalidConfiguration('processor `{}` "source_paths " must as list'.format(conf_processors))

                for sp_index in range(len(source_paths)):
                    source_base_path = source_paths[sp_index]
                    if not os.path.exists(source_base_path):
                        raise InvalidConfiguration('processor `{}` source_paths directory dose not exists. `{}`'.format(conf_processors, source_base_path))

                if not conf_processors.source_ext or not isinstance(OmegaConf.to_container(conf_processors.source_ext, resolve=True), list):
                    raise InvalidConfiguration('processors named `{}`. source_ext musy be a populated list '.format(conf_processors.processor_name))

                if not conf_processors.target_ext:
                    raise InvalidConfiguration('processors named `{}`. target_ext must be set')

            if RemoteJsFileProcessor in processor_classes or RemoteJsProcessor in processor_classes:

                if not conf_processors.javascript_handler:
                    raise InvalidConfiguration('processors named `{}`. javascript_handler must be set.'.format(conf_processors.javascript_handler))

                if not conf_processors.javascript_handler.strip().lower().endswith('.js'):
                    raise InvalidConfiguration('processors named `{}`. javascript_handler must be with js extension.'.format(conf_processors.javascript_handler))


    @staticmethod
    def __class_exist(className, classType):
        result = False
        try:
            result = (eval("type("+className+")") == classType)
        except NameError:
            pass
        return result
