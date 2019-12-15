import json
import logging

import requests
import urllib.parse


class RemoteJSClient(object):

    def __init__(self, url: str, token: str):
        self.session = requests.Session()
        self.url = url
        self.headers = {'Authorization': 'Basic {}'.format(token)}
        self.logger = logging.getLogger(self.__class__.__name__)

    def register_processor(self, processor_name: str, process_file: str):
        url = 'register_processor/{}'.format(processor_name)
        return self.__post(url, {}, files={'processor_file': process_file})

    def process_resource(self, processor_name: str, input_file: str, output_file: str, include_dependencies: list, exclude_dependencies: list, options: dict = {}):
        url = 'process_file/{}'.format(processor_name)
        data = {'input': input_file, 'output': output_file, 'include': include_dependencies, 'exclude': exclude_dependencies, 'options': options}
        return self.__post(url, data)

    def process_render(self, processor_name: str, input_file: str, context: dict, i18n: dict):
        return self.__post('render_file/{}'.format(processor_name), {'input': input_file, 'context': context, 'i18n': i18n})

    def ding(self):
        return self.__post('ding', {})

    def __post(self, url_relative: str, data: dict, files: dict = None):
        url_absolute = urllib.parse.urljoin(self.url, url_relative)
        response = self.session.post(url_absolute, json=data, headers=self.headers, timeout=10, files=files)
        response_json = json.loads(response.content.decode('utf-8'))
        try:
            if response.status_code == 200:
                return response_json
            else:
                raise ValueError(response_json['message'])
        except BaseException as ex:
            self.logger.error(ex)
            raise ex

    def close(self):
        self.session.close()