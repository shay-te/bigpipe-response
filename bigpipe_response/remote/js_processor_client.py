from bigpipe_response.remote.remote_client_server import RemoteClientServer


class JSRemoteClient(object):

    def __init__(self, remote_client_server: RemoteClientServer):
        self.remote_client_server = remote_client_server

    def register_processor_handler(self, processor_name, resource_str):
        return self.remote_client_server.register_processor_handler(processor_name, resource_str)

    def process_resource(self, processor_name: str, input_file: str, output_file: str, include_dependencies: list, exclude_dependencies: list, options: dict = {}):
        return self.remote_client_server.send_process_file(processor_name, input_file, output_file, include_dependencies, exclude_dependencies, options)

    def render_resource(self, processor_name: str, input_file: str, context: dict, i18n: dict):
        return self.remote_client_server.send_render_file(processor_name, input_file, context, i18n)
