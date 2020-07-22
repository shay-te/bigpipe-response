import logging
import os
import sys

from hydra._internal.hydra import GlobalHydra
from hydra.experimental import initialize, compose
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
        tests_data_path = os.path.join(test_path, 'data', 'config')
        if not OmegaConf.get_resolver('full_path'):
            OmegaConf.register_resolver('full_path', lambda sub_path: os.path.join(test_path, sub_path))

        if not GlobalHydra().is_initialized():
            initialize(config_dir=tests_data_path, strict=True, caller_stack_depth=2)
        return compose("test_config.yaml", overrides=config_override)
