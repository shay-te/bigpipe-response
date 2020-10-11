import json

from bigpipe_response.javascript_dom_bind.javascript_dom_bind import JavascriptDOMBind


class ReactDomBind(JavascriptDOMBind):

    def generate_bind_command(self, render_source: str, render_context: dict, target_element: str):
        return '\nReactDOM.render(React.createElement({},\n {}),\n document.getElementById(\'{}\'));'.format(render_source, json.dumps(render_context), target_element)
