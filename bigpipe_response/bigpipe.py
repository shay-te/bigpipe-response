import logging
import os
from shutil import copyfile

from omegaconf import OmegaConf

from bigpipe_response import utils
from bigpipe_response.bigpipe_render_options import BigpipeRenderOptions
from bigpipe_response.conf.bigpipe_settings import BigpipeSettings
from bigpipe_response.remote.node_installer import NodeInstaller
from bigpipe_response.remote.remote_client_server import RemoteClientServer

from django.views.i18n import JavaScriptCatalog, get_formats


class Bigpipe(object):

    __instance = None

    def __init__(self, config: OmegaConf):
        BigpipeSettings.validate_settings(config)

        self.conf = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.output_dir = os.path.normpath(os.path.join(self.conf.rendered_output_path, self.conf.rendered_output_container))
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        # set render default options
        self.default_render_option = BigpipeRenderOptions(
            js_processor_name=self.conf.processors.js.name,
            css_processor_name=self.conf.processors.css.name,
            i18n_processor_name=self.conf.processors.i18n.name,
            js_link_bundle_dependencies=self.conf.processors.js.bundle_link_dependencies,
            css_link_bundle_dependencies=self.conf.processors.css.bundle_link_dependencies,
            css_complete_dependencies_by_js=self.conf.processors.css.complete_dependencies_by_js,
            javascript_dom_bind=utils.get_class(self.conf.processors.js.javascript_dom_bind)(),
        )

    def start(self):
        #
        # install js dependencies
        self.logger.info("Installing javascript dependencies.")
        javascript_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "js")
        self.__install_javascript_dependencies(javascript_folder)


        # install js dependencies
        javascript_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "js")
        copyfile(
            os.path.join(javascript_folder, "browser", "bigpipe.js"),
            os.path.join(self.conf.rendered_output_path, "bigpipe.js"),
        )
        self.remote_client_server = RemoteClientServer(javascript_folder,
                                                       self.conf.is_production_mode,
                                                       self.conf.remote.port_start,
                                                       self.conf.remote.port_count,
                                                       OmegaConf.to_container(self.conf.remote.extra_node_packages, resolve=True))


        # processors manager
        from bigpipe_response.processors_manager import ProcessorsManager

        self.processors_manager = ProcessorsManager(self.conf)

        # start remote js server
        self.logger.info("Starting remote javascript server.")
        self.remote_client_server.start()

    @staticmethod
    def init(config: OmegaConf):
        if Bigpipe.__instance is None:
            Bigpipe.__instance = Bigpipe(config)

    @staticmethod
    def get():
        if Bigpipe.__instance is None:
            raise NameError("Bigpipe not initialized")
        return Bigpipe.__instance

    def shutdown(self):
        self.processors_manager.shutdown()
        self.remote_client_server.shutdown()

    @property
    def processors(self):
        return self.processors_manager

    @property
    def config(self):
        return self.conf

    @property
    def remote(self):
        return self.remote_client_server

    def processor_dir(self, processor_name: str):
        return os.path.join(self.output_dir, processor_name)

    def get_render_option(self, render_option: BigpipeRenderOptions):
        if render_option:
            # Fill default values where None
            for key, value in self.default_render_option.__dict__.items():
                option_value = getattr(render_option, key)
                if option_value is None:
                    setattr(render_option, key, value)
            return render_option
        return self.default_render_option

    def __install_javascript_dependencies(self, javascript_folder):
        jsi18n_file = os.path.join(javascript_folder, "dependencies", "jsi18n.js")
        if not os.path.isfile(jsi18n_file):
            with open(jsi18n_file, "wb") as jsi18n_file:
                file_content = (
                    JavaScriptCatalog()
                    .render_to_response({"catalog": {}, "formats": get_formats(), "plural": {}})
                    .content
                )
                jsi18n_file.write(file_content)
                jsi18n_file.close()

        NodeInstaller.init(javascript_folder)