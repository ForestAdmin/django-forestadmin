from django.http import HttpResponse

from django_forest.utils import get_token
from django_forest.utils.permissions import Permission


class PermissionMiddleware:
    # TODO: smart action and stats
    mapping = {
        'list': {
            'GET': 'browseEnabled',
            'POST': 'addEnabled',
            'DELETE': 'deleteEnabled'
        },
        'detail': {
            'GET': 'readEnabled',
            'PUT': 'editEnabled',
            'DELETE': 'deleteEnabled'
        },
        'count': {
            'GET': 'browseEnabled'
        },
        'csv': {
            'GET': 'exportEnabled'
        }
    }

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

    def is_authorized(self, request, resource, token):
        permission_name = self.mapping[request.resolver_match.url_name][request.method]
        permission = Permission(resource,
                                permission_name,
                                token['rendering_id'],
                                token['id'])
        if not Permission.is_authorized(permission):
            raise Exception('not authorized')

    def process_view(self, request, view_func, *args, **kwargs):
        if request.resolver_match.app_name.startswith('django_forest:resources'):
            try:
                token = get_token(request)
                self.is_authorized(request, args[1]['resource'], token)
            except Exception:
                return HttpResponse(status=403)
