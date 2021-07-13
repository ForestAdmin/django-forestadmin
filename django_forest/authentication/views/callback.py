import json
import logging
from datetime import timedelta, datetime
from jose import jwt
from oic.oauth2 import AuthorizationResponse
from django.http import JsonResponse
from django.views.generic import View

from django_forest.authentication.oidc.client_manager import OidcClientManager
from django_forest.authentication.utils import get_callback_url
from django_forest.utils.error_handler import MESSAGES
from django_forest.utils.forest_api_requester import ForestApiRequester
from django_forest.utils.forest_setting import get_forest_setting


logger = logging.getLogger(__name__)


# Based on https://pyoidc.readthedocs.io/en/latest/examples/rp.html
class CallbackView(View):

    def _expiration_in_seconds(self):
        return datetime.timestamp(datetime.utcnow() + timedelta(hours=1))

    def _handle_2fa_error(self, response):
        body = response.json()
        if 'errors' in body and isinstance(body['errors'], list) and len(body['errors']) > 0:
            server_error = body['errors'][0]
            if 'name' in server_error and server_error['name'] == 'TwoFactorAuthenticationRequiredForbiddenError':
                raise Exception(MESSAGES['SERVER_TRANSACTION']['TWO_FACTOR_AUTHENTICATION_REQUIRED'])

    def _handle_authent_response(self, response):
        if response.status_code == 200:
            body = response.json()
            user = body['data']['attributes']
            user['id'] = body['data']['id']
            return user
        elif response.status_code == 404:
            raise Exception(MESSAGES['SERVER_TRANSACTION']['SECRET_NOT_FOUND'])
        elif response.status_code == 422:
            raise Exception(MESSAGES['SERVER_TRANSACTION']['SECRET_AND_RENDERINGID_INCONSISTENT'])
        else:
            self._handle_2fa_error(response)

        raise Exception(MESSAGES['SERVER_TRANSACTION']['AUTHORIZATION'])

    def _authenticate(self, rendering_id, auth_data):
        route = f'/liana/v2/renderings/{rendering_id}/authorization'
        headers = {'forest-token': auth_data['forest_token']}

        try:
            response = ForestApiRequester.get(route, headers=headers)
        except Exception as e:
            logger.error(f'Authorization error: {str(e)}')
            raise e
        else:
            return self._handle_authent_response(response)

    def _verify_code_and_generate_token(self, redirect_url, request):
        if 'state' not in request.GET:
            raise Exception(MESSAGES['SERVER_TRANSACTION']['INVALID_STATE_MISSING'])
        if 'renderingId' not in request.GET['state']:
            raise Exception(MESSAGES['SERVER_TRANSACTION']['INVALID_STATE_RENDERING_ID'])

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
        try:
            rendering_id = json.loads(request.GET['state'])['renderingId']
        except Exception:
            raise Exception(MESSAGES['SERVER_TRANSACTION']['INVALID_STATE_FORMAT'])
        else:
            user = self._authenticate(rendering_id, {'forest_token': resp['access_token']})

            auth_secret = get_forest_setting('FOREST_AUTH_SECRET')
            return jwt.encode({
                'id': user['id'],
                'email': user['email'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'team': user['teams'][0],
                'rendering_id': rendering_id,
                'exp': self._expiration_in_seconds()
            },
                auth_secret,
                algorithm='HS256')

    def get(self, request, *args, **kwargs):
        try:
            callback_url = get_callback_url()
            token = self._verify_code_and_generate_token(callback_url, request)

            auth_secret = get_forest_setting('FOREST_AUTH_SECRET')
            result = {
                'token': token,
                'tokenData': jwt.decode(token, auth_secret, algorithms=['HS256'])
            }
        except Exception as error:
            return JsonResponse({'errors': [{'status': 500, 'detail': str(error)}]}, status=500)
        else:
            return JsonResponse(result)
