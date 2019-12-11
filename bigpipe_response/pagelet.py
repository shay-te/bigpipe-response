from django.http import HttpRequest


class Pagelet(object):

    def __init__(self, parent_request, target_element_id, route_view, params, method: str = 'GET'):
        self.route_view = route_view
        self.parent_request = parent_request
        self.target = target_element_id
        self.params = params
        self.method = method

    def render(self):
        new_request = HttpRequest()
        new_request.method = self.method
        new_request.user = self.parent_request.user

        new_request.GET = self.parent_request.GET
        new_request.POST = self.parent_request.POST
        new_request.COOKIES = self.parent_request.COOKIES
        new_request.META = self.parent_request.META
        new_request.FILES = self.parent_request.FILES

        return self.route_view(new_request, **self.params)
