import os
import unittest

from bigpipe_response.bigpipe import Bigpipe


from bigpipe_response.bigpipe_response import BigpipeResponse
from bigpipe_response.content_loader import ContentLoader
from tests.test_utils import TestUtils

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.data.settings')
import django
django.setup()

Bigpipe.init(TestUtils.get_test_configuration().bigpipe)
TestUtils.empty_output_folder(Bigpipe.get().config.rendered_output_path)
print("Installing javascript dependencies.")


class TestContentLoader(unittest.TestCase):
    def tearDown(self):
        print('Shutdown Bigpipe')
        Bigpipe.get().shutdown()

    def test_content_loader(self):
            content_loader = ContentLoader(render_type=BigpipeResponse.RenderType.JAVASCRIPT,
                                           render_source='TestMainPage',
                                           js_dependencies=['simple_js_file'],
                                           scss_dependencies=['main'],
                                           i18n_dependencies=["CONST_USER_open_question_placeholder.*", "profileboxes_no_more_profiles"])
            content, js, css, i18n, js_effected_files, css_effected_files = content_loader.load_content('body', [], [])
            self.assertNotEqual(content, None)
            self.assertNotEqual(js, None)
            self.assertNotEqual(css, None)
            self.assertNotEqual(i18n, None)
            self.assertNotEqual(js_effected_files, None)
            self.assertNotEqual(css_effected_files, None)
            self.assertGreater(js.index('function_inside_simple_js_object'), 1)
            self.assertGreater(css.index('.test-class{color:#ADADAD}'), 1)
            self.assertGreater(len(i18n), 1)
            self.assertNotEqual(i18n['CONST_USER_open_question_placeholder_1'], None)
