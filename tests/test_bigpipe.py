import os
import unittest

from bigpipe_response.pagelet import Pagelet
from django.http import HttpResponse, HttpRequest
from django.utils.translation import activate
from django.utils.translation.trans_real import DjangoTranslation

from bigpipe_response.bigpipe import Bigpipe
from bigpipe_response.bigpipe_response import BigpipeResponse
from tests.test_utils import TestUtils

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.data.settings')
import django
django.setup()

TestUtils.setup_logger()
Bigpipe.init(TestUtils.get_test_configuration().bigpipe)
TestUtils.empty_output_folder(Bigpipe.get().config.rendered_output_path)
print("Installing javascript dependencies.")


def generate_dummy_request():
    return HttpRequest()


TestUtils.setup_logger()


class TestBigpipe(unittest.TestCase):

    def tearDown(self):
        print('Shutdown Bigpipe')
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
        self.assertEqual(response_len, 4)
        self.assertGreater(response_content[response_len-1].decode('utf-8').index('</html>'), 1)

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

    def test_loading_with_paglets(self):
        def top_blue_bar(request):
            return BigpipeResponse(HttpResponse(), render_type=BigpipeResponse.RenderType.JAVASCRIPT, render_source='TestMainPage')

        pagelets = [
            Pagelet(generate_dummy_request(), 'pagelet_top_blue_bar', top_blue_bar, {}),
        ]

        response = BigpipeResponse(HttpResponse(),
                                   render_type=BigpipeResponse.RenderType.JAVASCRIPT,
                                   render_source='TestMainPage',
                                   js_dependencies=['simple_js_file'],
                                   scss_dependencies=['main'],
                                   i18n_dependencies=["CONST_USER_open_question_placeholder.*", "profileboxes_no_more_profiles"],
                                   pagelets=pagelets)

        response_content = list(response.streaming_content)
        response_len = len(response_content)
        self.assertEqual(response_len, 5)
        self.assertGreater(response_content[response_len-1].decode('utf-8').index('</html>'), 1)

    def test_js_not_exists_component(self):
        # test will pass only when production mode is on, otherwise bigpipe will render an error message
        response = BigpipeResponse(HttpResponse(), render_type=BigpipeResponse.RenderType.JAVASCRIPT, render_source='TestMainPageNotExists')
        with self.assertRaises(ValueError):
            list(response.streaming_content)

