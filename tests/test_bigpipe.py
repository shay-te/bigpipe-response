import os
import unittest
from django.http import HttpResponse
from django.utils.translation import activate
from django.utils.translation.trans_real import DjangoTranslation
from omegaconf import OmegaConf

from bigpipe_response.bigpipe import Bigpipe
from bigpipe_response.bigpipe_response import BigpipeResponse
from tests.test_utils import TestUtils

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.data.settings')
import django
django.setup()

tests_path = os.path.dirname(os.path.abspath(__file__))
OmegaConf.clear_resolvers()
OmegaConf.register_resolver('full_path', lambda sub_path: os.path.join(tests_path, sub_path))
config = OmegaConf.merge(OmegaConf.load(os.path.join(tests_path, '..', 'bigpipe_response', 'conf', 'bigpipe.yaml')), OmegaConf.load(os.path.join(tests_path, 'data', 'bigpipe_settings.yaml')))
Bigpipe.init(config.bigpipe)
print("Installing javascript dependencies.")
Bigpipe.get().start()

TestUtils.empty_output_folder(Bigpipe.get().config.rendered_output_path)


class TestBigpipe(unittest.TestCase):

    def tearDown(self):
        print('shutdown Bigpipe')
        Bigpipe.get().shutdown()

    def test_js_manager(self):
        # response_content will return a list of all elements to render + the closing of </body></html>
        # in case of fail to load resources the length of response_content will be 1 due only too the </body></html> only
        response = BigpipeResponse(HttpResponse(),
                                   render_type=BigpipeResponse.RenderType.JAVASCRIPT,
                                   render_source='TestMainPage',
                                   js_dependencies=['simple_js_file'],
                                   scss_dependencies=['main'],
                                   i18n_dependencies=["CONST_USER_open_question_placeholder.*", "profileboxes_no_more_profiles"])
        response_content = list(response.streaming_content)
        response_len = len(response_content)
        self.assertEqual(response_len,4)
        self.assertGreater(response_content[response_len-1].decode('utf-8').index('</html>'), 1)

    def test_js_not_exists_component(self):
        # test will pass only when production mode is on, otherwise bigpipe will render an error message
        response = BigpipeResponse(HttpResponse(), render_type=BigpipeResponse.RenderType.JAVASCRIPT, render_source='TestMainPageNotExists')
        with self.assertRaises(ValueError):
            list(response.streaming_content)

    def test_js_render(self):
        prop_data_string_en = '--i-am-props-data-string---'
        i18n_string_en = "Where you want to be in your next relationship"

        hebrew_translation = DjangoTranslation('he')
        prop_data_string_he = hebrew_translation._catalog['CONST_USER_open_question_placeholder_1']
        i18n_string_he = hebrew_translation._catalog['CONST_USER_open_question_placeholder_4']

        response_en = BigpipeResponse(HttpResponse(),
                                      render_type=BigpipeResponse.RenderType.JAVASCRIPT_RENDER,
                                      render_source='TestMainPage',
                                      render_context={'props_data': prop_data_string_en},
                                      i18n_dependencies=["CONST_USER_open_question_placeholder.*", "profileboxes_no_more_profiles"])
        response_str_en = list(response_en)[0].decode("utf-8")
        self.assertEqual(response_str_en[0:5], '<html')
        self.assertGreater(response_str_en.index(prop_data_string_en), 10)
        self.assertGreater(response_str_en.index(i18n_string_en), 10)

        activate('he')

        response_he = BigpipeResponse(HttpResponse(),
                                      render_type=BigpipeResponse.RenderType.JAVASCRIPT_RENDER,
                                      render_source='TestMainPage',
                                      render_context={'props_data': prop_data_string_he},
                                      i18n_dependencies=["CONST_USER_open_question_placeholder.*", "profileboxes_no_more_profiles"])
        response_str_he = list(response_he)[0].decode("utf-8")
        self.assertEqual(response_str_he[0:5], '<html')
        self.assertGreater(response_str_he.index(prop_data_string_he), 10)
        self.assertGreater(response_str_he.index(i18n_string_he), 10)


