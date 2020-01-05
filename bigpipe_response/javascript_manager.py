import logging
import os
import tempfile
from shutil import copyfile

from omegaconf import OmegaConf

from bigpipe_response.remote.node_installer import NodeInstaller
from django.views.i18n import JavaScriptCatalog, get_formats


class JavascriptManager(object):

    def __init__(self, config):
        self.conf = config
        self.local_javascript_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "js")

        if self.conf.java_script_install_folder and not os.path.isdir(self.conf.java_script_install_folder):
            raise ValueError('Config "java_script_install_folder" was set to "{}". but the folder dose not exists'.format(self.conf.java_script_install_folder))

        if self.conf.java_script_install_folder:
            self.javascript_folder = self.conf.java_script_install_folder
        else:
            self.javascript_folder = os.path.join(tempfile.gettempdir(), 'bigpipe_response')
            if not os.path.isdir(self.javascript_folder):
                os.makedirs(self.javascript_folder)

        self.__copy_assets()

        local_packages = {}

        if self.javascript_folder is not self.local_javascript_folder:
            # "bigpipe_response" same as in package.json
            local_packages = {"bigpipe_response": os.path.join(self.local_javascript_folder, 'bigpipe_response-1.0.0.tgz')}

        NodeInstaller.init(self.javascript_folder)
        NodeInstaller.get().install_javascript_dependencies(OmegaConf.to_container(self.conf.remote.extra_node_packages, resolve=True), local_packages)

    def __copy_assets(self):
        # copy bigpipe.js to public dir
        copyfile(
            os.path.join(self.local_javascript_folder, "browser", "bigpipe.js"),
            os.path.join(self.conf.rendered_output_path, "bigpipe.js"),
        )

        # copy i18n generates file into "js/dependencies" folder.
        # remote javascript base_processor will use this file as a dependency for server side rendering.
        jsi18n_file = os.path.join(self.local_javascript_folder, "dependencies", "jsi18n.js")
        if not os.path.isfile(jsi18n_file):
            with open(jsi18n_file, "wb") as jsi18n_file:
                # generate the django javascript i18n file to a string
                file_content = (
                    JavaScriptCatalog()
                    .render_to_response({"catalog": {}, "formats": get_formats(), "plural": {}})
                    .content
                )
                jsi18n_file.write(file_content)
                jsi18n_file.close()

