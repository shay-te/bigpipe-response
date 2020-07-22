import logging
import os
import tempfile
from shutil import copyfile

from django.views.i18n import JavaScriptCatalog, get_formats
from omegaconf import OmegaConf

from bigpipe_response.remote.node_installer import NodeInstaller


class JavascriptManager(object):

    def __init__(self, config):
        self.conf = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.local_javascript_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "js")

        if self.conf.java_script_install_folder and not os.path.isdir(self.conf.java_script_install_folder):
            raise ValueError('Config "java_script_install_folder" is set to `{}`. but the folder dose not exists'.format(self.conf.java_script_install_folder))

        if self.conf.java_script_install_folder:
            self.javascript_folder = self.conf.java_script_install_folder
        else:
            self.javascript_folder = os.path.join(tempfile.gettempdir(), 'bigpipe_response_node')
            if not os.path.isdir(self.javascript_folder):
                os.makedirs(self.javascript_folder)

        self.__copy_assets()

        local_packages = {}

        if self.javascript_folder != self.local_javascript_folder:
            # "bigpipe_response" same as in package.json
            local_packages = {"bigpipe_response": os.path.join(self.local_javascript_folder, 'build', 'bigpipe_response-1.0.0.tgz')}

        NodeInstaller.init(self.javascript_folder)
        NodeInstaller.get().install_javascript_dependencies(OmegaConf.to_container(self.conf.remote.extra_node_packages, resolve=True), local_packages)

    def __copy_assets(self):
        # copy bigpipe.js to public dir
        self.logger.info('Coping "bigpipe.js" to public directory')
        copyfile(
            os.path.join(self.local_javascript_folder, "browser", "bigpipe.js"),
            os.path.join(self.conf.rendered_output_path, "bigpipe.js"),
        )

        # copy build package.json to target javascript folder
        if not os.path.isfile(os.path.join(self.javascript_folder, 'package.json')):
            self.logger.info('Coping "package.json" for building bigpipe response remote server')
            copyfile(
                os.path.join(self.local_javascript_folder, 'build', 'package.json'),
                os.path.join(self.javascript_folder, 'package.json')
            )

        # copy i18n generates file into "js/dependencies" folder.
        # remote javascript base_processor will use this file as a dependency for server side rendering.
        jsi18n_file = os.path.join(self.local_javascript_folder, "browser", "jsi18n.js")
        if not os.path.isfile(jsi18n_file):
            self.logger.info('Generating django "jsi18n.js"file and making internal copy of it')
            with open(jsi18n_file, "wb") as jsi18n_file:
                # generate the django javascript i18n file to a string
                file_content = (
                    JavaScriptCatalog()
                    .render_to_response({"catalog": {}, "formats": get_formats(), "plural": {}})
                    .content
                )
                jsi18n_file.write(file_content)
                jsi18n_file.close()

