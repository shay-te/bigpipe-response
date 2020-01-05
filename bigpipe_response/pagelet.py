from django.http import HttpRequest


class Pagelet(object):

    def __init__(self, parent_request, target_element_id, route_view, params, method: str = 'GET'):
        self.route_view = route_view
        self.parent_request = parent_request
        self.target = target_element_id
        self.params = params
        self.method = method

    def render(self):
        return self.route_view(self.parent_request, **self.params)
