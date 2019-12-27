import os
import unittest

from omegaconf import OmegaConf

from bigpipe_response.bigpipe import Bigpipe
from tests.test_utils import TestUtils

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings')

tests_path = os.path.dirname(os.path.abspath(__file__))
OmegaConf.clear_resolvers()
OmegaConf.register_resolver('full_path', lambda sub_path: os.path.join(tests_path, sub_path))
config = OmegaConf.merge(OmegaConf.load(os.path.join(tests_path, '..', 'bigpipe_response', 'conf', 'bigpipe.yaml')), OmegaConf.load(os.path.join(tests_path, 'data', 'bigpipe_settings.yaml')))

Bigpipe.init(config.bigpipe)
print("Installing javascript dependencies.")

TestUtils.empty_output_folder(Bigpipe.get().config.rendered_output_path)


class TestBigpipeProcessor(unittest.TestCase):
    def tearDown(self):
        print("shutdown Bigpipe")
        Bigpipe.get().shutdown()

    def test_css_manager(self):
        self.assertRaises(
            ValueError,
            Bigpipe.get().processors.run_processor,
            Bigpipe.get().config.processors.css.name,
            "paramsadasd",
        )
        processor_result = Bigpipe.get().processors.run_processor(
            Bigpipe.get().config.processors.css.name, "main"
        )
        fp = open(processor_result.output_file, "r")
        content = fp.read()
        fp.close()

        self.assertNotEqual(content, None)
        self.assertNotEqual(content, "")

    def test_js_manager(self):
        # Not existing component
        self.assertRaises(
            ValueError,
            Bigpipe.get().processors.run_processor,
            Bigpipe.get().config.processors.js.name,
            "dasdasdasd",
        )

        # Existing working component
        processor_result = Bigpipe.get().processors.run_processor(
            Bigpipe.get().config.processors.js.name, "TestMainPage"
        )
        fp = open(processor_result.output_file, "r")
        content = fp.read()
        fp.close()

        self.assertNotEqual(content, None)
        self.assertNotEqual(content, "")
        self.assertNotEqual(content.index("var TestSecondPage"), -1)
        self.assertNotEqual(content.index("TestMainPage"), -1)

        # Component with error
        with self.assertRaises(ValueError):
            Bigpipe.get().processors.run_processor(
                Bigpipe.get().config.processors.js.name, "ComponentWithError"
            )

        try:
            Bigpipe.get().processors.run_processor(
                Bigpipe.get().config.processors.js.name, "ComponentWithError"
            )
        except Exception as e:
            self.assertGreater(
                str(e).index("Expected corresponding JSX closing tag"), 0
            )
