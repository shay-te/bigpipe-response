import os
import unittest

from bigpipe_response.bigpipe import Bigpipe
from bigpipe_response.bigpipe_response import BigpipeResponse
from bigpipe_response.content_loader import ContentLoader
from bigpipe_response.helpers import to_include
from tests.test_utils import TestUtils

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.data.settings')
import django
django.setup()

TestUtils.setup_logger()
Bigpipe.init(TestUtils.get_test_configuration().bigpipe_response)
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
            content_result = content_loader.load_content('body', [], [])
            self.assertNotEqual(content_result.content, None)
            self.assertNotEqual(content_result.js, None)
            self.assertNotEqual(content_result.css, None)
            self.assertNotEqual(content_result.i18n, None)
            self.assertNotEqual(content_result.js_effected_files, None)
            self.assertNotEqual(content_result.css_effected_files, None)
            self.assertGreater(content_result.js.index('function_inside_simple_js_object'), 1)
            self.assertGreater(content_result.css.index('.test-class{color:#ADADAD}'), 1)
            self.assertGreater(len(content_result.i18n), 1)
            self.assertNotEqual(content_result.i18n['CONST_USER_open_question_placeholder_1'], None)

    def test_multiple_processors(self):
        module_processor_name = Bigpipe.get().config.processors.js_modules.params.processor_name
        content_loader = ContentLoader(render_type=BigpipeResponse.RenderType.JAVASCRIPT,
                                       render_source='TestMainPage',
                                       js_dependencies=['simple_js_file'] + to_include(['React=react', 'ReactDOM=react-dom', 'createReactClass=create-react-class'], is_link=False, processor_name=module_processor_name),
                                       scss_dependencies=['main'],
                                       i18n_dependencies=["CONST_USER_open_question_placeholder.*"])
        content_result = content_loader.load_content('body', [], [])
        self.assertNotEqual(content_result.content, None)
        self.assertNotEqual(content_result.js, None)
        self.assertNotEqual(content_result.css, None)
        self.assertNotEqual(content_result.i18n, None)
        self.assertGreater(content_result.js.index("Copyright (c) Facebook, Inc. and its affiliates"), 1)
        self.assertGreater(content_result.js.index("react.production.min.js"), 1)
        self.assertGreater(content_result.js.index("react-dom.production.min.js"), 1)

    def test_css_included_by_javascript(self):
        content_loader = ContentLoader(render_type=BigpipeResponse.RenderType.JAVASCRIPT, render_source='TestMainPage')
        content_result = content_loader.load_content('body', [], [])
        self.assertNotEqual(content_result.content, None)
        self.assertNotEqual(content_result.js, None)
        self.assertNotEqual(content_result.css, None)
        self.assertNotEqual(content_result.i18n, None)
        self.assertGreaterEqual(content_result.css.index('.test-second-page'), 0)

    def test_es6_react_component(self):
        content_loader = ContentLoader(render_type=BigpipeResponse.RenderType.JAVASCRIPT,
                                       render_source='TestComponentES6')
        content_result = content_loader.load_content('body', [], [])
        self.assertNotEqual(content_result.content, None)
        self.assertNotEqual(content_result.js, None)
        self.assertNotEqual(content_result.css, None)
        self.assertNotEqual(content_result.i18n, None)

    def test_render_source_not_link(self):
        self.assertRaises(ValueError, ContentLoader, render_type=BigpipeResponse.RenderType.JAVASCRIPT,  render_source='@TestMainPage')

    def test_links_in_results(self):
        content_loader = ContentLoader(render_type=BigpipeResponse.RenderType.JAVASCRIPT,
                                       render_source='TestMainPage',
                                       js_dependencies=['@simple_js_file'],
                                       scss_dependencies=['@main'])

        content_result = content_loader.load_content('body', [], [])
        self.assertNotEqual(content_result.js_links, None)
        self.assertEqual(len(content_result.js_links), 1)
        for js_link in content_result.js_links:
            link_path = os.path.normpath('{}/{}'.format(Bigpipe.get().config.rendered_output_path, js_link))
            self.assertEqual(os.path.isfile(link_path), True)
            file_content = open(link_path, mode='r', encoding='utf-8').read()
            self.assertGreaterEqual(file_content.index("function_inside_simple_js_object"), 0)

        for css_link in content_result.css_links:
            link_path = os.path.normpath('{}/{}'.format(Bigpipe.get().config.rendered_output_path, css_link))
            self.assertEqual(os.path.isfile(link_path), True)
            file_content = open(link_path, mode='r', encoding='utf-8').read()
            self.assertGreaterEqual(file_content.index(".test-class"), 0)

