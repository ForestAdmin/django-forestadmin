import json

from django.http import JsonResponse
from django.views.generic import View

from django_forest.authentication.oidc.client_manager import OidcClientManager
from django_forest.authentication.utils import get_callback_url
from django_forest.utils.error_handler import MESSAGES


# Based on https://pyoidc.readthedocs.io/en/latest/examples/rp.html
class IndexView(View):
    def _get_and_check_rendering_id(self, request):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        rendering_id = body.get('renderingId', None)
        if not rendering_id:
            raise Exception(MESSAGES['SERVER_TRANSACTION']['MISSING_RENDERING_ID'])

        if not (isinstance(rendering_id, str) or isinstance(rendering_id, int)):
            raise Exception(MESSAGES['SERVER_TRANSACTION']['INVALID_RENDERING_ID'])

        return int(rendering_id)

    def _get_authorization_url(self, redirect_url, state):
        client = OidcClientManager.get_client_for_callback_url(redirect_url)
        args = {
            'client_id': client.client_id,
            'response_type': 'code',
            'scope': ['openid', 'email', 'profile'],
            'state': json.dumps(state),
            'redirect_uri': redirect_url,
        }
        auth_req = client.construct_AuthorizationRequest(request_args=args)
        authorization_url = auth_req.request(client.authorization_endpoint)

        return authorization_url

    def post(self, request, *args, **kwargs):
        try:
            rendering_id = self._get_and_check_rendering_id(request)
            callback_url = get_callback_url()

            authorization_url = self._get_authorization_url(callback_url, {'renderingId': rendering_id})
        except Exception as error:
            return JsonResponse({'errors': [{'status': 500, 'detail': str(error)}]}, status=500)
        else:
            return JsonResponse({'authorizationUrl': authorization_url})
