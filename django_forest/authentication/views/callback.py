import json
import logging
import requests

from datetime import timedelta, datetime
from jose import jwt
from oic.oauth2 import AuthorizationResponse
from django.http import JsonResponse
from django.views.generic import View
from django_forest.authentication.exception import AuthenticationClientException, AuthenticationThirdPartyException

from django_forest.authentication.oidc.client_manager import OidcClientManager
from django_forest.authentication.utils import authentication_exception
from django_forest.utils.error_handler import MESSAGES
from django_forest.utils.forest_api_requester import ForestApiRequester
from django_forest.utils.forest_setting import get_forest_setting

try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo


logger = logging.getLogger(__name__)


# Based on https://pyoidc.readthedocs.io/en/latest/examples/rp.html
class CallbackView(View):

    def _expiration_in_seconds(self):
        return datetime.timestamp(datetime.utcnow().replace(tzinfo=zoneinfo.ZoneInfo('UTC')) + timedelta(hours=1))

    def _handle_2fa_error(self, response):
        body = response.json()
        if 'errors' in body and isinstance(body['errors'], list) and len(body['errors']) > 0:
            server_error = body['errors'][0]
            if 'name' in server_error and server_error['name'] == 'TwoFactorAuthenticationRequiredForbiddenError':
                raise AuthenticationThirdPartyException(
                    MESSAGES['SERVER_TRANSACTION']['TWO_FACTOR_AUTHENTICATION_REQUIRED']
                )

    def _handle_authent_error(self, response):
        if response.status_code == 404:
            raise AuthenticationThirdPartyException(
                MESSAGES['SERVER_TRANSACTION']['SECRET_NOT_FOUND']
            )
        elif response.status_code == 422:
            raise AuthenticationThirdPartyException(
                MESSAGES['SERVER_TRANSACTION']['SECRET_AND_RENDERINGID_INCONSISTENT']
            )
        else:
            body = response.json()
            if isinstance(body.get('errors'), list) and len(body['errors']) > 0:
                server_error = body['errors'][0]
                if server_error.get('name') == 'TwoFactorAuthenticationRequiredForbiddenError':
                    raise AuthenticationThirdPartyException(
                        MESSAGES['SERVER_TRANSACTION']['TWO_FACTOR_AUTHENTICATION_REQUIRED']
                    )

        logger.warning(f"Unknown error on the authentication process {response.status_code} {response.json()}")
        raise AuthenticationThirdPartyException(
            MESSAGES['SERVER_TRANSACTION']['AUTHORIZATION']
        )

    def parse_authorization_response(self, client, state, full_path_info):
        return client.parse_response(
            AuthorizationResponse,
            info=full_path_info,
            sformat='urlencoded',
            state=state,
            scope=['openid', 'email', 'profile']
        )

    def _get_state_params(self, request):
        try:
            state = json.loads(
                request.GET['state']
            )
        except KeyError:
            raise AuthenticationClientException(
                MESSAGES['SERVER_TRANSACTION']['INVALID_STATE_MISSING']
            )
        except ValueError:
            raise AuthenticationClientException(
                MESSAGES['SERVER_TRANSACTION']['INVALID_STATE_FORMAT']
            )
        return state

    def _authenticate(self, client, state, code):
        access_token_request = client.do_access_token_request(
            state=json.dumps(state),
            scope=['openid', 'email', 'profile'],
            authn_method='',
            request_args={'code': code},
            verify=False,
            skew=5
        )
        rendering_id = state['renderingId']
        route = f'/liana/v2/renderings/{rendering_id}/authorization'

        url = ForestApiRequester.build_url(route)
        headers = {'forest-token': access_token_request['access_token']}

        try:
            response = ForestApiRequester.get(
                url,
                headers=headers
            )
        except requests.exceptions.RequestException:
            raise AuthenticationThirdPartyException(
                MESSAGES['SERVER_TRANSACTION']['AUTHORIZATION']
            )
        if response.status_code == 200:
            body = response.json()
            user = body['data']['attributes']
            user['id'] = body['data']['id']
            return user
        else:
            self._handle_authent_error(response)

    def _verify_code_and_generate_token_body(self, request):
        client = OidcClientManager.get_client()
        state = self._get_state_params(request)
        if 'renderingId' not in state:
            raise AuthenticationClientException(MESSAGES['SERVER_TRANSACTION']['INVALID_STATE_RENDERING_ID'])
        authorization_resp = self.parse_authorization_response(
            client,
            state,
            request.get_full_path_info(),
        )
        user = self._authenticate(
            client,
            state,
            authorization_resp['code']
        )
        return {
            'id': user['id'],
            'email': user['email'],
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'team': user['teams'][0],
            'rendering_id': state['renderingId'],
            'exp': self._expiration_in_seconds()
        }

    @authentication_exception
    def get(self, request, *args, **kwargs):
        token_body = self._verify_code_and_generate_token_body(request)
        auth_secret = get_forest_setting('FOREST_AUTH_SECRET')
        return JsonResponse({
            'token': jwt.encode(
                token_body,
                auth_secret,
                algorithm='HS256'
            ),
            'tokenData': token_body
        })
