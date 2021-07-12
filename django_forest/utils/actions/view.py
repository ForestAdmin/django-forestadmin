import json

from django.http import HttpResponse
from django.views import generic

from django_forest.utils import get_token
from django_forest.utils.permissions import Permission


class ActionView(generic.View):
    def get_body(self, body):
        body_unicode = body.decode('utf-8')
        return json.loads(body_unicode)

    def get_smart_action_request_info(self, request):
        return {
            'endpoint': request.path,
            'http_method': request.method
        }

    def is_authorized(self, resource, token, smart_action_request_info):
        permission_name = 'actions'
        permission = Permission(resource,
                                permission_name,
                                token['rendering_id'],
                                token['id'],
                                smart_action_request_info=smart_action_request_info)
        if not Permission.is_authorized(permission):
            raise Exception('not authorized')

    def dispatch(self, request, *args, **kwargs):
        body = self.get_body(request.body)
        collection_name = body['data']['attributes']['collection_name']
        # check permissions
        try:
            token = get_token(request)
            smart_action_request_info = self.get_smart_action_request_info(request)
            self.is_authorized(collection_name, token, smart_action_request_info)
        except Exception:
            return HttpResponse(status=403)
        else:
            return super().dispatch(request, *args, **kwargs)
