import re

from django.http import HttpResponse
from jose import jwt

from django_forest.utils.forest_setting import get_forest_setting
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

    def get_token(self, request):
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split()[1]
        # NOTICE: Necessary for downloads authentication.
        elif 'cookie' in request.headers:
            # TODO review
            REGEX_COOKIE_SESSION_TOKEN = r'forest_session_token=([^;]*)'
            m = re.search(REGEX_COOKIE_SESSION_TOKEN, request.headers['cookie'])
            token = m.group(1)

        auth_secret = get_forest_setting('AUTH_SECRET')
        return jwt.decode(token, auth_secret, algorithms=['HS256'])

    def get_app_name(self, request):
        return request.resolver_match.app_name

    def process_view(self, request, view_func, *args, **kwargs):
        if self.get_app_name(request).startswith('django_forest:resources'):
            token = self.get_token(request)
            resource = args[1]['resource']

            permission_name = self.mapping[request.resolver_match.url_name][request.method]
            collection_list_parameters = None
            if permission_name == 'browseEnabled':
                collection_list_parameters = {
                    'user_id': token['id'],
                    'filters': request.GET.get('filters'),
                }

            permission = Permission(resource,
                                    permission_name,
                                    token['rendering_id'],
                                    token['id'],
                                    collection_list_parameters=collection_list_parameters)
            if not Permission.is_authorized(permission):
                return HttpResponse(status=403)
