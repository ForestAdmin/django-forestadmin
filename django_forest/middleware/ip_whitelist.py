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

    def process_view(self, request, view_func, *args, **kwargs):

        if not IpWhitelist.fetched:  # TODO if invalid ip, fetch again
            IpWhitelist.get_rules()

        if IpWhitelist.use_ip_whitelist:
            client_ip, is_routable = get_client_ip(request)
            if client_ip is None:
                return HttpResponse(status=403)
            else:
                if not IpWhitelist.is_ip_matches_any_rule(client_ip):
                    return HttpResponse(status=403)