from bigpipe_response.javascript_dom_bind.javascript_dom_bind import JavascriptDOMBind


class BigpipeRenderOptions(object):

    def __init__(self,
                 js_processor_name: str = None,
                 css_processor_name: str = None,
                 i18n_processor_name: str = None,
                 js_link_bundle_dependencies: bool = None,
                 css_link_bundle_dependencies: bool = None,
                 css_complete_dependencies_by_js: bool = None,
                 javascript_dom_bind: JavascriptDOMBind = None):

        self.js_processor_name = js_processor_name
        self.css_processor_name = css_processor_name
        self.i18n_processor_name = i18n_processor_name
        self.js_link_bundle_dependencies = js_link_bundle_dependencies
        self.css_link_bundle_dependencies = css_link_bundle_dependencies
        self.css_complete_dependencies_by_js = css_complete_dependencies_by_js
        self.javascript_dom_bind = javascript_dom_bind
