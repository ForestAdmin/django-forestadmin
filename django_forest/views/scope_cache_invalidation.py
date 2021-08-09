import logging

from django.http import JsonResponse

from django_forest.utils.scope import ScopeManager

# Get an instance of a logger
from django_forest.utils.views.base import BaseView

logger = logging.getLogger(__name__)


class ScopeCacheInvalidationView(BaseView):
    def post(self, request, *args, **kwargs):

        if not self.is_authenticated(request):
            return JsonResponse({'errors': [{'detail': 'Please authenticate'}]}, status=403)

        body = self.get_body(request.body)
        if 'renderingId' not in body:
            msg = 'missing renderingId'
            logger.error(msg)
            return self.error_response(msg)

        ScopeManager.invalidate_scope_cache(str(body['renderingId']))
        return JsonResponse({}, status=200)
