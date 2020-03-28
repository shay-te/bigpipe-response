import logging
import traceback

import pkg_resources

from bigpipe_response.remote.remote_js_client import RemoteJSClient
from bigpipe_response.remote.remote_js_server import RemoteJsServer
import socket


class RemoteClientServer(object):
    def __init__(
        self,
        js_folder: str,
        is_production: bool,
        port_start: int,
        port_count: int,
    ):
        self.js_folder = js_folder
        self.is_production = is_production
        self._processors = {}
        self.port_start = port_start
        self.port_end = port_start + port_count
        self.logger = logging.getLogger(self.__class__.__name__)

    def register_processor_handler(self, processor_name, resource_str):
        if not processor_name:
            raise ValueError("processor cannot be null")
        if processor_name in self._processors.keys():
            raise ValueError("processor already registered")

        self._processors[processor_name] = self.__get_js_resource_as_string(processor_name, resource_str)

    def __get_js_resource_as_string(self, processor_name, resourse_str):
        if not resourse_str:
            raise ValueError('processor_js_resource must be set')

        arr = resourse_str.rsplit('.', 2)
        resource_path = arr[0]
        resource_name = '{}.{}'.format(arr[1], arr[2])
        self.logger.info('Loading javascript resource. resource_path: `{}`, resource_name: `{}`'.format(resource_path, resource_name))

        if not pkg_resources.resource_exists(resource_path, resource_name):
            raise ValueError('processor_js_resource must dose not exists')

        return pkg_resources.resource_string(resource_path, resource_name)

    def __send_register_processors(self):
        for processor_name, javascript_code in self._processors.items():
            self.remote_js_client.register_processor(processor_name, javascript_code)

    def send_process_file(
        self,
        processor_name: str,
        input_file: str,
        output_file: str,
        include_dependencies: list,
        exclude_dependencies: list,
        options: dict = {},
    ):
        self.__validate_server_available()
        return self.remote_js_client.process_resource(
            processor_name,
            input_file,
            output_file,
            include_dependencies,
            exclude_dependencies,
            options,
        )

    def send_render_file(self, processor_name, input_file, context, i18n):
        self.__validate_server_available()
        return self.remote_js_client.process_render(
            processor_name, input_file, context, i18n
        )

    def shutdown(self):
        if self.remote_js_server:
            self.remote_js_server.stop_server()

    def __validate_server_available(self):
        if not self.remote_js_server or not self.remote_js_server.is_server_running():
            if self.remote_js_client:
                self.remote_js_client.close()
            self.start()

    def start(self):
        if not len(self._processors):
            raise ValueError('No processors was set, use "set_processors" method.')

        remote_js_server = RemoteJsServer(self.js_folder, self.is_production)

        port_scan_start = self.port_start
        self.logger.info('Looking for available port in range "{} - {}"'.format(self.port_start, self.port_end))
        while port_scan_start < self.port_end:
            port = self.__scan_for_available_port(port_scan_start, self.port_end)
            if port:
                try:
                    token = remote_js_server.start_server(port)
                    self.remote_js_server = remote_js_server
                    self.remote_js_client = RemoteJSClient("http://localhost:{}".format(port), token)
                    self.logger.info('Remote Javascript Server started at port `{}`.')
                    self.logger.info('Registering processors to: remote js server.')
                    self.__send_register_processors()
                    return
                except BaseException as ex:
                    self.logger.error("Available port found ({}), But unable to start server. Error: \n{}".format(port, traceback.format_exc()))
                    port_scan_start = port_scan_start + 1
            else:
                break

        err_msg = "Unable to find available port in range ({} - {})".format(self.port_start, self.port_end)
        self.logger.error(err_msg)
        raise ValueError(err_msg)

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
