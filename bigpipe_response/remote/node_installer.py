import json
import logging
import os
from subprocess import Popen, STDOUT, PIPE


class NodeInstaller(object):

    __instance = None

    def __init__(self, js_folder: str):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.js_folder = js_folder

        if not os.path.isdir(js_folder):
            os.makedirs(js_folder)

    @staticmethod
    def init(js_folder: str):
        if NodeInstaller.__instance is None:
            NodeInstaller.__instance = NodeInstaller(js_folder)

    @staticmethod
    def get():
        if NodeInstaller.__instance is None:
            raise NameError('NodeInstaller not initialized')
        return NodeInstaller.__instance

    def get_javascript_folder(self):
        return self.js_folder

    def install_javascript_dependencies(self, packages: list):
        self.logger.info('NodeInstaller.install_javascript_dependencies {}. (first run may take a while)'.format(packages))
        node_modules_dir = os.path.join(self.js_folder, 'node_modules')
        if not os.path.isdir(node_modules_dir):
            self.logger.info('node_modules folder missing installing all dependencies')
            self.__install_packages(self.js_folder, packages)
        else:
            packages_diff = []
            package_lock_json_file = os.path.join(self.js_folder, 'package-lock.json')
            if not os.path.isfile(package_lock_json_file):
                packages_diff = packages
            else:
                with open(package_lock_json_file) as file:
                    dependencies = json.loads(file.read(), strict=False)['dependencies']
                    for package in packages:
                        if package not in dependencies:
                            packages_diff.append(package)

            if packages_diff:
                self.logger.info('node_modules exists but with missing dependencies, installing missing dependencies: {}'.format(packages_diff))
                self.__install_packages(self.js_folder, packages_diff)
            else:
                self.logger.info('all node dependencies already installed')

    def __install_packages(self, js_folder: str, packages: list):
        command_install_dev = 'npm install {}'.format(' '.join(packages))
        exitcode, out, err = self.__execute_command(js_folder, command_install_dev)
        if exitcode != 0:
            raise ValueError('enable to install [{}], exit with error [{}]'.format(command_install_dev, err))
        self.logger.info('NodeInstaller output:\n{}\n'.format(out))

    def __execute_command(self, js_folder, command):
        proc = Popen(command, stdout=PIPE, stderr=PIPE, shell=True, cwd=js_folder)
        out, err = proc.communicate()
        return proc.returncode, out.decode('utf-8'), err.decode('utf-8')
