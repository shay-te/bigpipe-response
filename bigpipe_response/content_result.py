from bigpipe_response.bigpipe import Bigpipe


class ContentResult(object):
    def __init__(self, content: str, js: str, css: str, i18n: dict, js_links: list, css_links: list, js_effected_files: list, css_effected_files: list):
        self.content = content
        self.js = js
        self.css = css
        self.i18n = i18n
        self.js_links = js_links
        self.css_links = css_links
        self.js_effected_files = js_effected_files
        self.css_effected_files = css_effected_files

    def to_dict(self, paglet_target: str):
        result = {'target': paglet_target}
        if self.css:
            result['css'] = self.css
        if self.content:
            result['html'] = self.content
        if self.js:
            result['js'] = self.js
        if self.i18n:
            result['i18n'] = self.i18n
        if self.js_links:
            result['js_links'] = self.js_links
        if self.css_links:
            result['css_links'] = self.css_links
        if Bigpipe.get().config.is_production_mode:
            result['remove'] = True
        return result
