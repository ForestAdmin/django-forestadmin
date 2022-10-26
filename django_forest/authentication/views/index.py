import json
import logging

from oic.oic.message import AuthorizationRequest

from django.http import JsonResponse
from django.views.generic import View
from django_forest.authentication.exception import AuthenticationClientException

from django_forest.authentication.oidc.client_manager import OidcClientManager
from django_forest.authentication.utils import authentication_exception
from django_forest.utils.error_handler import MESSAGES


logger = logging.getLogger(__name__)

# Based on https://pyoidc.readthedocs.io/en/latest/examples/rp.html


class IndexView(View):

    def _get_payload(self, request):
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            raise AuthenticationClientException(
                'request.body is not a valid json object'
            )
        return payload

    def _get_rendering_id(self, payload):
        try:
            rendering_id = payload['renderingId']
        except KeyError:
            raise AuthenticationClientException(
                MESSAGES['SERVER_TRANSACTION']['MISSING_RENDERING_ID']
            )
        if not any(isinstance(rendering_id, _type) for _type in [str, int]):
            raise AuthenticationClientException(MESSAGES['SERVER_TRANSACTION']['INVALID_RENDERING_ID'])
        return int(rendering_id)

    def _get_authorization_url(self, state):
        client = OidcClientManager.get_client()
        args = {
            'client_id': client.client_id,
            'response_type': 'code',
            'scope': ['openid', 'email', 'profile'],
            'state': json.dumps(state),
            'redirect_uri': client.redirect_uris[0],
        }
        auth_req: AuthorizationRequest = client.construct_AuthorizationRequest(request_args=args)
        authorization_url = auth_req.request(client.authorization_endpoint)
        return authorization_url

    @authentication_exception
    def post(self, request, *args, **kwargs):
        payload = self._get_payload(request)
        rendering_id = self._get_rendering_id(payload)
        authorization_url = self._get_authorization_url({'renderingId': rendering_id})
        return JsonResponse({'authorizationUrl': authorization_url})
