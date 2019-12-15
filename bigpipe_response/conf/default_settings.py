import os

from bigpipe_response.javascript_dom_bind.react_dom_bind import ReactDomBind

processors_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'processors')

RENDERED_OUTPUT_PATH: None
STATIC_URI: None
IS_PRODUCTION_MODE: None

JS_PROCESSOR_NAME = 'jsx'
JS_SOURCE_PATH: None
JS_PROCESSOR_SOURCE_EXT = ['js', 'jsx']
JS_PROCESSOR_TARGET_EXT = 'js'
JS_PROCESSOR_HANDLER_PATH = os.path.join(processors_folder, 'RollupReactProcessor.js')
JS_DOM_BIND = ReactDomBind()
JS_LINK_BUNDLE_DEPENDENCIES = True

CSS_PROCESSOR_NAME = 'css'
CSS_SOURCE_PATH: None
CSS_PROCESSOR_SOURCE_EXT = ['scss']
CSS_PROCESSOR_TARGET_EXT = 'css'
CSS_COMPLETE_DEPENDENCIES_BY_JS = True
CSS_LINK_BUNDLE_DEPENDENCIES = True

I18N_PROCESSOR_NAME = 'i18n'

JS_SERVER_PORT_START = 7480
JS_SERVER_PORT_COUNT = 10

JS_SERVER_EXTRA_NODE_PACKAGES = []
