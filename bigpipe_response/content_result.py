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
