import json
import logging
import os
import threading
import time
from subprocess import Popen, STDOUT, PIPE


class NodeInstaller(object):

    __instance = None

    def __init__(self, js_folder: str):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.js_folder = js_folder

        if not os.path.isdir(js_folder):
            os.makedirs(js_folder)

        self.logger.info('Start NodeInstaller at folder "{}"'.format(self.js_folder))

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

    def install_javascript_dependencies(self, packages: list, local_packages: dict):
        self.logger.info('NodeInstaller.install_javascript_dependencies {}. '.format(list(local_packages.values()) + packages))
        node_modules_dir = os.path.join(self.js_folder, 'node_modules')
        if not os.path.isdir(node_modules_dir):
            self.logger.info('WAIT!!. patience please. First run takes a while. "node_modules" folder missing installing all dependencies')
            self.__install_packages(self.js_folder, local_packages.values())
            self.__install_packages(self.js_folder, packages)
        else:
            packages_diff = []
            package_lock_json_file = os.path.join(self.js_folder, 'package-lock.json')
            if not os.path.isfile(package_lock_json_file):
                packages_diff = packages
            else:
                with open(package_lock_json_file) as file:
                    dependencies = json.loads(file.read(), strict=False)['dependencies']
                    for local_package_key, local_package_value in local_packages.items():
                        if local_package_key not in dependencies:
                            packages_diff.append(local_package_value)

                    for package in packages:
                        if package not in dependencies:
                            packages_diff.append(package)

            if packages_diff:
                self.logger.info('"node_modules" folder exists but with missing dependencies, installing missing dependencies: {}'.format(packages_diff))
                self.__install_packages(self.js_folder, packages_diff)
            else:
                self.logger.info('all node dependencies already installed')

    def __install_packages(self, js_folder: str, packages: list):
        command_install_dev = 'npm install {}'.format(' '.join(packages))
        exitcode, out, err = self.__execute_command(js_folder, command_install_dev)
        if exitcode != 0:
            raise ValueError('enable to install [{}], exit with error [{}]'.format(command_install_dev, err))
        self.logger.info('NodeInstaller output:\n{}\nerror:'.format(out, err))

    def __execute_command(self, js_folder, command):
        proc = Popen(command, stdout=PIPE, stderr=PIPE, shell=True, cwd=js_folder)
        self.installing_javascript = True
        threading.Thread(target=self.__print_spinner, daemon=True).start()
        out, err = proc.communicate()
        self.installing_javascript = False
        return proc.returncode, out.decode('utf-8'), err.decode('utf-8')

    def __print_spinner(self):
        while self.installing_javascript:
            for i in '|\\-/':
                print('\b' + i, end='')
                time.sleep(0.1)
        print('\b', end='')
