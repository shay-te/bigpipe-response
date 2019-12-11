import atexit
import json
import logging
import os
import random
import signal
import string
import sys
import threading

import requests
from contextlib import suppress
from subprocess import Popen, PIPE
from time import sleep


class RemoteJsServer(object):

    def __init__(self, working_directory: str, is_production: bool):
        if not working_directory: raise ValueError('Working directory must be set')
        self.is_production = is_production
        self.working_directory = working_directory
        self.process = None
        self.logger = logging.getLogger(self.__class__.__name__)
        atexit.register(self.stop_server)

    def is_server_running(self):
        return True if self.process and self.process.poll() is None else False

    def start_server(self, port):
        if self.process: raise EnvironmentError('RemoteJsServer is already running.')

        self.logger.info('Initializing RemoteJsServer. Attempt to start remove javascript server on port  port {}'.format(port))
        try:
            token = self.__generate_token()

            process = Popen(['node', 'index.js', '--port={}'.format(port), '--token={}'.format(token), '--mode={}'.format('PRODUCTION' if self.is_production else 'DEVELOPMENT')],
                            # stdout=PIPE,
                            # stderr=PIPE,
                            cwd=self.working_directory,
                            shell=False)

            sleep(0.6)  # wait for server to start
            poll = process.poll()
            if poll is None:
                # threading.Thread(target=self.__output_reader, args=(process.stdout,)).start()
                # threading.Thread(target=self.__output_reader, args=(process.stderr,)).start()

                self.__validate_server_is_running(port, token)
                self.__register_server_start(process, token)
                return token
            else:
                out, err = process.communicate()
                raise OSError(err)
        except BaseException as e:
            raise OSError('ERROR: remote javascript server failed to start in port [{}]'.format(port)) from e

    def stop_server(self):
        if self.process:
            pid = self.process.pid
            with suppress(Exception):
                os.kill(pid, signal.SIGINT)
                os.kill(pid, signal.SIGTERM)

            self.process.poll()
            self.process.kill()
            self.process.terminate()
            if self.process.poll() is None:
                with suppress(Exception):
                    self.process.stdout.close()
                    self.process.stderr.close()
            self.logger.info("RemoteJsServer.stop_server, trying to kill node process.")

    def __validate_server_is_running(self, port, token):
        response = requests.post('http://localhost:{}/ding'.format(port), headers={'Authorization': 'Basic {}'.format(token)})
        if response.status_code == 200:
            response_json = json.loads(response.content.decode('utf-8'))
            if response_json['message'].index('dong') == 0:
                return True
        raise ValueError('Server is not running under port [{}]'.format(port))

    def __register_server_start(self, process, token):
        self.process = process
        self.token = token

    def __generate_token(self, string_length=6):
        letters_and_digits = string.ascii_letters + string.digits
        return ''.join(random.choice(letters_and_digits) for _ in range(string_length))

    # def __output_reader(self, stream):
    #     for line in iter(stream.readline, b''):
    #         print('got line: {0}'.format(line.decode('utf-8')), end='')
