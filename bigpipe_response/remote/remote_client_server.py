import logging
import traceback

from bigpipe_response.remote.node_installer import NodeInstaller
from bigpipe_response.remote.remote_js_client import RemoteJSClient
from bigpipe_response.remote.remove_js_server import RemoteJsServer
import socket
from omegaconf import OmegaConf

class RemoteClientServer(object):

    def __init__(self, js_folder: str, is_production: bool, port_start: int, port_count: int, extra_node_packages: list = []):
        self.js_folder = js_folder
        self.is_production = is_production
        self._processors = {}
        self.port_start = port_start
        self.port_end = port_start + port_count
        self.logger = logging.getLogger(self.__class__.__name__)

        packages = ['yargs', 'restify', 'rollup', 'rollup-plugin-jsx', 'rollup-plugin-uglify', '@rollup/plugin-virtual', 'react', 'create-react-class', 'react-dom', 'register-module'] + extra_node_packages
        NodeInstaller.get().install_javascript_dependencies(packages)

    def set_processors(self, processors):
        if not processors: raise ValueError('processor cannot be null')
        self._processors = {processor.processor_name: processor for processor in processors}

    def __send_register_processors(self):
        for processor_name, processor in self._processors.items():
            self.remote_js_client.register_processor(processor_name, processor.get_processor_js_handler_path())

    def send_process_file(self, processor_name: str, input_file: str, output_file: str, include_dependencies: list, exclude_dependencies: list, options: dict = {}):
        self.__validate_server_available()
        return self.remote_js_client.process_resource(processor_name, input_file, output_file, include_dependencies, exclude_dependencies, options)

    def send_render_file(self, processor_name, input_file, context, i18n):
        self.__validate_server_available()
        return self.remote_js_client.process_render(processor_name, input_file, context, i18n)

    def shutdown(self):
        if self.remote_js_server:
            self.remote_js_server.stop_server()

    def __validate_server_available(self):
        if not self.remote_js_server or not self.remote_js_server.is_server_running():
            if self.remote_js_client:
                self.remote_js_client.close()
            self.start()

    def start(self):
        if not len(self._processors): raise ValueError('No processors was set, use \"set_processors\" method.')

        remote_js_server = RemoteJsServer(self.js_folder, self.is_production)

        port_scan_start = self.port_start
        self.logger.info('Looking for available port in range ({} - {})'.format(self.port_start, self.port_end))
        while port_scan_start < self.port_end:
            port = self.__scan_for_available_port(port_scan_start, self.port_end)
            if port:
                try:
                    token = remote_js_server.start_server(port)
                    self.remote_js_server = remote_js_server
                    self.remote_js_client = RemoteJSClient('http://localhost:{}'.format(port), token)
                    self.__send_register_processors()
                    return
                except BaseException as ex:
                    self.logger.error('Available port found ({}), But unable to start server. Error: \n{}'.format(port, traceback.format_exc()))
                    port_scan_start = port_scan_start + 1
            else:
                break

        self.logger.error('Unable to find available port in range ({} - {})'.format(self.port_start, self.port_end))
        raise ValueError('Unable to find available port to start the server')

    def __scan_for_available_port(self, from_port, to_port):
        for port in range(from_port, to_port):
            if self.__is_port_open(port):
                return port
        return None

    def __is_port_open(self, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = False
        try:
            sock.bind(("127.0.0.1", port))
            result = True
        except Exception as e:
            pass
        sock.close()
        return result
