import logging

from django.http import HttpResponse

from django_forest.utils import get_token
from django_forest.utils.permissions import Permission
from django_forest.utils.views.base import BaseView

logger = logging.getLogger(__name__)


class ActionView(BaseView):
    def get_smart_action_request_info(self, request):
        return {
            'endpoint': request.path,
            'http_method': request.method
        }

    def is_authorized(self, request, token, resource):
        smart_action_request_info = self.get_smart_action_request_info(request)
        permission = Permission(resource,
                                'actions',
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
            logger.exception(e)
            return self.error_response(e)
        else:
            # check permissions
            try:
                token = get_token(request)
                self.is_authorized(request, token, resource)
            except Exception:
                return HttpResponse(status=403)
            else:
                return super().dispatch(request, *args, **kwargs)
