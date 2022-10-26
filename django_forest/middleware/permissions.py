import json

from django.http import HttpResponse

from django_forest.utils import get_token
from django_forest.utils.permissions import Permission


class PermissionMiddleware:
    mapping = {
        'list': {
            'GET': 'browseEnabled',
            'POST': 'addEnabled',
            'PUT': 'editEnabled',
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
        },
        'liveQueries': {
            'POST': 'liveQueries'
        },
        'statsWithParameters': {
            'POST': 'statsWithParameters'
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

    def populate_query_request_info(self, permission_name, body, kwargs):
        if permission_name in 'liveQueries':
            kwargs['query_request_info'] = body['query']
        elif permission_name in 'statsWithParameters':
            if 'timezone' in body:
                del body['timezone']
            if 'group_by_field' in body:
                #  usefull if the group_by_field is a related field
                body['group_by_field'] = body['group_by_field'].split(':')[0]
            kwargs['query_request_info'] = body

    def is_authorized(self, request, token, resource):
        permission_name = self.mapping[request.resolver_match.url_name][request.method]

        is_chart = permission_name in ('liveQueries', 'statsWithParameters')
        kwargs = {}
        if is_chart:
            body = json.loads(request.body.decode('utf-8'))
            self.populate_query_request_info(permission_name, body, kwargs)

        if not (is_chart and token['permission_level'] in ['admin', 'editor', 'developer']):
            permission = Permission(resource,
                                    permission_name,
                                    token['rendering_id'],
                                    token['id'],
                                    **kwargs)
            if not Permission.is_authorized(permission):
                raise Exception('not authorized')

    def get_resource(self, args):
        resource = None
        if 'resource' in args[1]:
            resource = args[1]['resource']
        return resource

    def process_view(self, request, view_func, *args, **kwargs):
        if request.resolver_match.app_name.startswith('django_forest:resources') or \
                request.resolver_match.app_name.startswith('django_forest:stats'):

            token = get_token(request)
            resource = self.get_resource(args)

            try:
                self.is_authorized(request, token, resource)
            except Exception as e:
                return HttpResponse(f'Unauthorized request ({e})', status=403)
