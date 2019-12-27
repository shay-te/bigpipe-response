import os

from omegaconf import OmegaConf


class TestUtils(object):

    @staticmethod
    def empty_output_folder(output_path):
        # empty output directory
        for root, dirs, files in os.walk(output_path):
            for file in files:
                print('Delete file :  {}'.format(file))
                os.remove(os.path.join(root, file))

    @staticmethod
    def get_test_configuration():
        tests_path = os.path.dirname(os.path.abspath(__file__))
        OmegaConf.clear_resolvers()
        OmegaConf.register_resolver('full_path', lambda sub_path: os.path.join(tests_path, sub_path))
        return OmegaConf.merge(
            OmegaConf.load(os.path.join(tests_path, '..', 'bigpipe_response', 'conf', 'bigpipe.yaml')),
            OmegaConf.load(os.path.join(tests_path, 'data', 'bigpipe_settings.yaml')))
