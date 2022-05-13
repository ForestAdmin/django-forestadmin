from django.http import HttpResponse
from ipware import get_client_ip

from django_forest.utils.ip_whitelist import IpWhitelist


class IpWhitelistMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    def get_client_ip(self, request):
        client_ip, _ = get_client_ip(request)
        return client_ip

    def is_ip_valid(self, request):
        if IpWhitelist.use_ip_whitelist:
            client_ip = self.get_client_ip(request)
            if client_ip is None:
                return False
            return IpWhitelist.is_ip_matches_any_rule(client_ip)
        return True

    def process_view(self, request, view_func, *args, **kwargs):

        # if invalid ip, fetch again
        if not IpWhitelist.fetched or not self.is_ip_valid(request):
            try:
                IpWhitelist.get_rules()
            except Exception as e:
                return HttpResponse(f'Unable to retrieve the ip white list ({e})', status=403)

        if not self.is_ip_valid(request):
            return HttpResponse('IP client is invalid', status=403)
