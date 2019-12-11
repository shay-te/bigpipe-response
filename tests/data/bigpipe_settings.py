import os

parent_dir = os.path.realpath(os.getcwd())
js_path = os.path.normpath(os.path.join(parent_dir, 'data'))
output_path = os.path.normpath(os.path.join(parent_dir, 'data_output'))

CLIENT_BASE_PATH = [js_path]
RENDERED_OUTPUT_PATH = output_path
STATIC_URI = ''
IS_PRODUCTION_MODE = True
