import logging
import os
import sys

import hydra
from hydra.core.global_hydra import GlobalHydra
from omegaconf import OmegaConf


class TestUtils(object):

    @staticmethod
    def setup_logger():
        # default logging to stdout
        root = logging.getLogger()
        root.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "[%(asctime)s][%(name)s][%(levelname)s] - %(message)s"
        )
        handler.setFormatter(formatter)
        root.addHandler(handler)

    @staticmethod
    def empty_output_folder(output_path):
        # empty output directory
        for root, dirs, files in os.walk(output_path):
            for file in files:
                print('Delete file :  {}'.format(file))
                os.remove(os.path.join(root, file))

    @staticmethod
    def get_test_configuration(config_override: list = []):
        test_path = os.path.dirname(os.path.abspath(__file__))
        source_path = os.path.join(test_path, 'data')
        output_path = os.path.join(test_path, 'output')

        if not os.path.exists(output_path):
            os.makedirs(output_path)

        if not OmegaConf.has_resolver('output_path'):
            OmegaConf.register_new_resolver('output_path', lambda sub_path: output_path)
            OmegaConf.register_new_resolver('source_path', lambda sub_path: source_path)

        if not GlobalHydra().is_initialized():
            hydra.initialize(config_path='data/config', caller_stack_depth=2)
        return hydra.compose("test_config.yaml", overrides=config_override)
