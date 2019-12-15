import os

parent_dir = os.path.realpath(os.getcwd())
js_path = os.path.normpath(os.path.join(parent_dir, 'data'))
output_path = os.path.normpath(os.path.join(parent_dir, 'data_output'))

JS_SOURCE_PATH = [js_path]
CSS_SOURCE_PATH = [js_path]
RENDERED_OUTPUT_PATH = output_path
STATIC_URI = ''
IS_PRODUCTION_MODE = True
