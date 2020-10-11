import os
import unittest

from bigpipe_response.bigpipe import Bigpipe
from tests.test_utils import TestUtils

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings')

TestUtils.setup_logger()
config = TestUtils.get_test_configuration()
Bigpipe.init(config.bigpipe)
print("Installing javascript dependencies.")

TestUtils.empty_output_folder(Bigpipe.get().config.rendered_output_path)


class TestBigpipeProcessor(unittest.TestCase):
    def tearDown(self):
        print("shutdown Bigpipe")
        Bigpipe.get().shutdown()

    def test_css_manager(self):
        processor_result = Bigpipe.get().processors.run_processor(Bigpipe.get().config.processors.css.params.processor_name,
                                                                  "main")
        fp = open(processor_result.output_file, "r")
        content = fp.read()
        fp.close()

        self.assertNotEqual(content, None)
        self.assertNotEqual(content, "")

        self.assertRaises(
            ValueError,
            Bigpipe.get().processors.run_processor,
            Bigpipe.get().config.processors.css.params.processor_name,
            "paramsadasd",
        )

    def test_js_manager(self):
        # Not existing component
        self.assertRaises(
            ValueError,
            Bigpipe.get().processors.run_processor,
            Bigpipe.get().config.processors.jsx.params.processor_name,
            "dasdasdasd",
        )

        # Existing working component
        processor_result = Bigpipe.get().processors.run_processor(
            Bigpipe.get().config.processors.jsx.params.processor_name, "TestMainPage"
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
                Bigpipe.get().config.processors.jsx.params.processor_name, "ComponentWithError"
            )

        try:
            Bigpipe.get().processors.run_processor(
                Bigpipe.get().config.processors.jsx.params.processor_name, "ComponentWithError"
            )
        except Exception as e:
            self.assertGreater(
                str(e).index("Expected corresponding JSX closing tag"), 0
            )
