import json
import os
from datetime import timedelta

from django.conf import settings
from jose import jwt


from django.utils import timezone
from django.http import JsonResponse
from django.views.generic import View
from oic.oauth2 import AuthorizationResponse

from django_forest.authentication.oidc.client_manager import OidcClientManager
from django_forest.authentication.utils import get_callback_url
from django_forest.utils.error_handler import MESSAGES

from django_forest.utils.forest_api_requester import ForestApiRequester


# Based on https://pyoidc.readthedocs.io/en/latest/examples/rp.html
class CallbackView(View):

    # TODO review
    def expiration_in_seconds(self):
        return timezone.now() + timedelta(hours=1)

    def authenticate(self, rendering_id, auth_data):
        route = f'/liana/v2/renderings/{rendering_id}/authorization'
        headers = {'forest-token': auth_data['forest_token']}
        response = ForestApiRequester.get(route, headers=headers)

        if response.status_code == 200:
            body = response.json()
            user = body['data']['attributes']
            user['id'] = body['data']['id']
            return user
        else:
            # TODO
            raise Exception()

    def verify_code_and_generate_token(self, redirect_url, request):
        client = OidcClientManager.get_client_for_callback_url(redirect_url)
        aresp = client.parse_response(AuthorizationResponse,
                                      info=request.get_full_path_info(),
                                      sformat='urlencoded',
                                      state=request.GET['state'],
                                      scope=['openid', 'email', 'profile'])
        resp = client.do_access_token_request(state=request.GET['state'],
                                              scope=['openid', 'email', 'profile'],
                                              authn_method='',
                                              request_args={'code': aresp['code']},
                                              verify=False)

        if 'state' not in request.GET:
            raise Exception(MESSAGES['SERVER_TRANSACTION']['INVALID_STATE_MISSING'])
        if 'renderingId' not in request.GET['state']:
            raise Exception(MESSAGES['SERVER_TRANSACTION']['INVALID_STATE_RENDERING_ID'])
        try:
            rendering_id = json.loads(request.GET['state'])['renderingId']
        except Exception:
            raise Exception(MESSAGES['SERVER_TRANSACTION']['INVALID_STATE_FORMAT'])
        else:
            user = self.authenticate(rendering_id, {'forest_token': resp['access_token']})

            AUTH_SECRET = getattr(settings, 'FOREST', {}).get('AUTH_SECRET', os.getenv('AUTH_SECRET'))
            return jwt.encode({
                'id': user['id'],
                'email': user['email'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'team': user['teams'][0],
                'rendering_id': rendering_id,
                'exp': self.expiration_in_seconds()
            },
                AUTH_SECRET,
                algorithm='HS256')

    def get(self, request, *args, **kwargs):
        try:
            callback_url = get_callback_url()
            token = self.verify_code_and_generate_token(callback_url, request)

            AUTH_SECRET = getattr(settings, 'FOREST', {}).get('AUTH_SECRET', os.getenv('AUTH_SECRET'))
            result = {
                'token': token,
                'tokenData': jwt.decode(token, AUTH_SECRET, algorithms=['HS256'])
            }
        except Exception as error:
            return JsonResponse({'errors': [{'status': 500, 'detail': error}]}, status=500)
        else:
            return JsonResponse(result)
