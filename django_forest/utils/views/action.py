from django.http import HttpResponse

from django_forest.utils import get_token
from django_forest.utils.permissions import Permission
from .base import BaseView


class ActionView(BaseView):
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
        resource = body['data']['attributes']['collection_name']

        try:
            self.Model = self.get_model(resource)
        except Exception as e:
            return self.error_response(e)
        else:
            # check permissions
            try:
                token = get_token(request)
                smart_action_request_info = self.get_smart_action_request_info(request)
                self.is_authorized(resource, token, smart_action_request_info)
            except Exception:
                return HttpResponse(status=403)
            else:
                return super().dispatch(request, *args, **kwargs)
