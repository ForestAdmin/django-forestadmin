import requests
from unittest import mock
from oic.oic.message import IATError

from django.test import TestCase
from django.urls import reverse
from django.utils.http import urlencode

from django_forest.authentication.oidc.client_manager import OidcClientManager
from django_forest.tests.authentication.oidc.test_configuration_retriever import mocked_config
from django_forest.tests.authentication.oidc.test_dynamic_client_registrator import mocked_client_credentials
from django_forest.tests.utils.test_forest_api_requester import mocked_requests

mocked_token_response = {
    'id_token': 'eyJraWQiOiI2eWthczh5SVMxdHM3dmZZY3JJRTd3aG1Wc2hwbHVKLUlDbU1pRWszYWJ3IiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOjUsImF1ZCI6ImV5SnJhV1FpT2lJMmVXdGhjemg1U1ZNeGRITTNkbVpaWTNKSlJUZDNhRzFXYzJod2JIVktMVWxEYlUxcFJXc3pZV0ozSWl3aVlXeG5Jam9pVWxNeU5UWWlmUS5leUowYjJ0bGJsOWxibVJ3YjJsdWRGOWhkWFJvWDIxbGRHaHZaQ0k2SW01dmJtVWlMQ0p5WldScGNtVmpkRjkxY21seklqcGJJbWgwZEhBNkx5OXNiMk5oYkdodmMzUTZPREF3TUM5bWIzSmxjM1F2WVhWMGFHVnVkR2xqWVhScGIyNHZZMkZzYkdKaFkyc2lYU3dpY21WbmFYTjBjbUYwYVc5dVgyVnVaSEJ2YVc1MElqb2lhSFIwY0hNNkx5OWhjR2t1WkdWMlpXeHZjRzFsYm5RdVptOXlaWE4wWVdSdGFXNHVZMjl0TDI5cFpHTXZjbVZuSWl3aVlYQndiR2xqWVhScGIyNWZkSGx3WlNJNkluZGxZaUlzSW1keVlXNTBYM1I1Y0dWeklqcGJJbUYxZEdodmNtbDZZWFJwYjI1ZlkyOWtaU0pkTENKeVpYTndiMjV6WlY5MGVYQmxjeUk2V3lKamIyUmxJbDBzSW1WdWRtbHliMjV0Wlc1MFgybGtJam94TURFc0ltbHpjeUk2SWtaUFVrVlRWRjlCVlZSSVJVNVVTVU5CVkVsUFRsOVRXVk5VUlUwaUxDSnBZWFFpT2pFMk1qTTBNamM1TlRWOS5QX21DOGVDcjM2UnFSeWU4WUk1elVTR3VxNEdtcEZmOFJMdnpRbW5WTWsySFhxelFUb1Bhb19SQXl2R3BZQzRKVWpGbXVUZEdJNlNTZzlKVkdJek5vZDJBWEZBeHA4cW1LOGF4X1RCS1VsZ19GX216cnpPeEVPYWlGa2lDUUFoYXZsQmhOQ3g1Nl9DUkJteXRfNVV2NkwtRTRfZXpHMEExa2FjUGZPUFphQk5TajhGcUNSeHJzblZaVnE2MFJtWTd0UmwwRFg1MFpVdVNFdmgwenpaTHdheUJ1VFlneExMZGc2RXZSNTJkc0pIbHYwS2dObG5ISndLQjc0Y1NBbDlDTTNQVkh5bTlFZzNWM0JfQmFBYnUwZUlLbXF0SjdfMWgxdzMtWXNINGpBQy1jelFOZ3pnTzc5SWlZMnMwdFRSRWU0dnYtUC1fX0JKOGxJeUZ4Y2d6dVEiLCJpc3MiOiJodHRwczovL2FwaS5kZXZlbG9wbWVudC5mb3Jlc3RhZG1pbi5jb20iLCJpYXQiOjE2MjM0Mjc5NjksImV4cCI6MTYyMzQzMTU2OX0.tqBAbP41a9U-XpX8Q_w3dRgVDqDtInTAGlzpwUvrS-49Mp7YSkB_eGypuYR_Kk7VGfjibCZflR6EXvbzg_5CrOKcpr-b44xi1k9zQntBtc7YPNJV30O0mPZW3ZAAWiZww-8LA8F2YyDK7l7VyoPO6oygTRtM6eJH91HQV9dE2sPILwm5jO-OutuwA0ZXGbUDL7OJ9if-V26IAKlurfqaUtL__RRs9s4uvRgvJzGEWGdImQYjzGtHDwEAQnMr8g3fwQWOlHa4xNbh3GWzkCiR_Tkh8d1zmXEWqx60Bv_IW9m3Db8ZR4_h8vG_7rbGlhVu1YeQjJ6jwk3kgeNq-KYIVA',
    'access_token': 'eyJraWQiOiI2eWthczh5SVMxdHM3dmZZY3JJRTd3aG1Wc2hwbHVKLUlDbU1pRWszYWJ3IiwiYWxnIjoiUlMyNTYifQ.eyJkYXRhIjp7ImRhdGEiOnsidHlwZSI6InVzZXJzIiwiaWQiOiI1IiwiYXR0cmlidXRlcyI6eyJmaXJzdF9uYW1lIjoiR3VpbGxhdW1lIiwibGFzdF9uYW1lIjoiQ2lzY28iLCJlbWFpbCI6Imd1aWxsYXVtZWNAZm9yZXN0YWRtaW4uY29tIn19fSwic2NvcGUiOiJvcGVuaWQgZW1haWwgcHJvZmlsZSIsImF1ZCI6IkZPUkVTVF9VU0VSUyIsImlzcyI6IkZPUkVTVF9BVVRIRU5USUNBVElPTl9TWVNURU0iLCJpYXQiOjE2MjM0Mjc5NjksImV4cCI6MTYyMzQzMTU2OX0.moA3J5u0JmbEhXgrWFP-w4dyIQdoSGIzKIK7fifZctF00EA_B_aeWnQWSfUY-Bc9czSm6wg9bzNQ5d1brhcvMzrnG4OSYm3g40Nq0WQktysIvnyIuVPgN_iUjVu4cai71ndwhHOKBSHsJRZ7-nQdluk9nQQ23BH6QmMZsRJnmtolzi8tHp3Rfozb8lO9cwY1bZzaAqzrj0MQxMgr1j7eReRGl4-v2W8WCMcaFdtcVMC6Rr98rhnIrbCJtWedJIqrkkpV_vFbCOJXMwFKZ3-VBu13MGvGu033BlbAOuw-cBHsXi3AKf3PkJ0aFXXrcFf_3AyEWqfoSE8uyjF66gCTFA',
    'expires_in': 36000000000,
    'scope': 'openid email profile',
    'token_type': 'Bearer'
}

mocked_jwks = {
    'keys': [
        {
            'e': 'AQAB',
            'n': 'z6Jiw8wmc5PEnYMoRNogKkqLi-nmoNY5dlYR0vb5Mhs5uLjgiZ0hkDKSTvTVHvLR6Yy9r7q7KI7A1cyhnhffK8J30plETLFbve5lVfGgYfEtYdMvJPmQznrMnfAJp6w_WDK8rqfR6N2hgFAQmkekf-ROC6Mj7XKtA4hDIGLsG_sv7ai_NcHNNVe5DkbSn3NjHpw0iIaPpjrAUmm9Npr6K45UreHd_6TCd9ddbUEgCFe6WtpboGyPOC18Sa6tSp-34-NCFefA7krnbYBBPRCy3szGxlTcx_JsljC_amRCNFraeBpswVzE5-Hq7-bpCX9crmOTZLWp8PG5d70AfixCEQ',
            'kty': 'RSA',
            'kid': '6ykas8yIS1ts7vfYcrIE7whmVshpluJ-ICmMiEk3abw',
            'alg': 'RS256',
            'use': 'sig'
        }
    ]
}

mocked_user = {
    'data': {
        'type': 'users',
        'id': '5',
        'attributes': {
            'first_name': 'Guillaume', 'last_name': 'Cisco',
            'email': 'guillaumec@forestadmin.com',
            'teams': ['Operations'],
            'two_factor_authentication_enabled': False,
            'two_factor_authentication_active': False,
            'two_factor_authentication_secret': None
        }
    }
}


def mocked_requests_get(value, **args):
    if value == 'https://api.development.forestadmin.com/oidc/jwks':
        return mocked_requests(mocked_jwks, 200)
    elif value == 'https://api.test.forestadmin.com/liana/v2/renderings/1/authorization':
        return mocked_requests(mocked_user, 200)


def mocked_requests_get_error_authorization(value, **args):
    if value == 'https://api.development.forestadmin.com/oidc/jwks':
        return mocked_requests(mocked_jwks, 200)
    elif value == 'https://api.test.forestadmin.com/liana/v2/renderings/1/authorization':
        raise requests.exceptions.RequestException('Authorization error')


def mocked_requests_get_not_found(value, **args):
    if value == 'https://api.development.forestadmin.com/oidc/jwks':
        return mocked_requests(mocked_jwks, 200)
    elif value == 'https://api.test.forestadmin.com/liana/v2/renderings/1/authorization':
        return mocked_requests({}, 404)


def mocked_requests_get_422(value, **args):
    if value == 'https://api.development.forestadmin.com/oidc/jwks':
        return mocked_requests(mocked_jwks, 200)
    elif value == 'https://api.test.forestadmin.com/liana/v2/renderings/1/authorization':
        return mocked_requests({}, 422)


def mocked_requests_get_bad_response_2fa(value, **args):
    if value == 'https://api.development.forestadmin.com/oidc/jwks':
        return mocked_requests(mocked_jwks, 200)
    elif value == 'https://api.test.forestadmin.com/liana/v2/renderings/1/authorization':
        return mocked_requests({'errors': [{'name': 'TwoFactorAuthenticationRequiredForbiddenError'}]}, 500)


def mocked_requests_get_bad_response(value, **args):
    if value == 'https://api.development.forestadmin.com/oidc/jwks':
        return mocked_requests(mocked_jwks, 200)
    elif value == 'https://api.test.forestadmin.com/liana/v2/renderings/1/authorization':
        return mocked_requests({'errors': [{'name': 'error'}]}, 500)


class AuthenticationCallbackViewTests(TestCase):

    def setUp(self):
        self.retrieve_patcher = mock.patch('django_forest.authentication.oidc.client_manager.retrieve',
                                           return_value=mocked_config)
        self.register_patcher = mock.patch('django_forest.authentication.oidc.client_manager.register',
                                           return_value=mocked_client_credentials)
        self.mocked_retrieve = self.retrieve_patcher.start()
        self.mocked_register = self.register_patcher.start()
        callback_url = 'http://localhost:8000/authentication/callback'
        self.oidc_client = OidcClientManager.get_client()
        self.oidc_client.redirect_uris = ['http://localhost:8000/forest/authentication/callback']

        url = reverse('django_forest:authentication:callback')
        query = {
            'code': 'eslqHqk8Luo_3CIf5SanmXBpq_7ytlTV8HgoVFNPwUvmWKDiwnf9XV6Bo04zRon8',
            'state': '{"renderingId": 1}'
        }
        self.url = f'{url}?{urlencode(query)}'

    def tearDown(self):
        OidcClientManager.client = None
        self.oidc_client = None
        self.retrieve_patcher.stop()
        self.register_patcher.stop()

    @mock.patch('oic.utils.time_util.utc_time_sans_frac', return_value=1623431559)
    @mock.patch('requests.request', return_value=mocked_requests(mocked_token_response, 200))
    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_get(self, mocked_requests_get, mocked_requests_request, mocked_utc_time_sans_frac):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        r = response.json()
        self.assertTrue('token' in r)
        self.assertTrue('tokenData' in r)
        self.assertEqual(r['tokenData']['id'], '5')
        self.assertEqual(r['tokenData']['email'], 'guillaumec@forestadmin.com')
        self.assertEqual(r['tokenData']['first_name'], 'Guillaume')
        self.assertEqual(r['tokenData']['last_name'], 'Cisco')
        self.assertEqual(r['tokenData']['team'], 'Operations')
        self.assertEqual(r['tokenData']['rendering_id'], 1)

    @mock.patch('oic.utils.time_util.utc_time_sans_frac', return_value=1623431559)
    @mock.patch('requests.request', return_value=mocked_requests(mocked_token_response, 200))
    @mock.patch('requests.get', side_effect=mocked_requests_get_not_found)
    def test_get_not_found(self, mocked_requests_get, mocked_requests_request, mocked_utc_time_sans_frac):
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 503)
        r = r.json()
        self.assertEqual(r, {
            'errors': [
                {
                    'detail': 'Cannot retrieve the data from the Forest server. Can you check that you properly copied the Forest envSecret in your settings?'
                }
            ]
        })

    @mock.patch('oic.utils.time_util.utc_time_sans_frac', return_value=1623431559)
    @mock.patch('requests.request', return_value=mocked_requests(mocked_token_response, 200))
    @mock.patch('requests.get', side_effect=mocked_requests_get_422)
    def test_get_422(self, mocked_requests_get, mocked_requests_request, mocked_utc_time_sans_frac):
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 503)
        r = r.json()
        self.assertEqual(r, {
            'errors': [
                {
                    'detail': 'Cannot retrieve the project you\'re trying to unlock. The envSecret and renderingId seems to be missing or inconsistent.'
                }
            ]
        })

    @mock.patch('oic.utils.time_util.utc_time_sans_frac', return_value=1623431559)
    @mock.patch('requests.request', return_value=mocked_requests(mocked_token_response, 200))
    @mock.patch('requests.get', side_effect=mocked_requests_get_bad_response_2fa)
    def test_get_bad_response_2fa(self, mocked_requests_get, mocked_requests_request, mocked_utc_time_sans_frac):
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 503)
        r = r.json()
        self.assertEqual(r, {
            'errors': [
                {
                    'detail': 'Two factor authentication required'
                }
            ]
        })

    @mock.patch('oic.utils.time_util.utc_time_sans_frac', return_value=1623431559)
    @mock.patch('requests.request', return_value=mocked_requests(mocked_token_response, 200))
    @mock.patch('requests.get', side_effect=mocked_requests_get_bad_response)
    def test_get_bad_response(self, mocked_requests_get, mocked_requests_request, mocked_utc_time_sans_frac):
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 503)
        r = r.json()
        self.assertEqual(r, {
            'errors': [
                {
                    'detail': 'Error while authorizing the user on Forest Admin'
                }
            ]
        })

    @mock.patch('oic.utils.time_util.utc_time_sans_frac', return_value=1623431559)
    @mock.patch('requests.request', return_value=mocked_requests(mocked_token_response, 200))
    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_get_state_missing(self, mocked_requests_get, mocked_requests_request, mocked_utc_time_sans_frac):
        url = reverse('django_forest:authentication:callback')
        query = {
            'code': 'eslqHqk8Luo_3CIf5SanmXBpq_7ytlTV8HgoVFNPwUvmWKDiwnf9XV6Bo04zRon8',
        }
        url = f'{url}?{urlencode(query)}'
        r = self.client.get(url)
        self.assertEqual(r.status_code, 401)
        r = r.json()
        self.assertEqual(r, {
            'errors': [
                {
                    'detail': 'Invalid response from the authentication server: the state parameter is missing'
                }
            ]
        })

    @mock.patch('oic.utils.time_util.utc_time_sans_frac', return_value=1623431559)
    @mock.patch('requests.request', return_value=mocked_requests(mocked_token_response, 200))
    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_get_no_rendering_id(self, mocked_requests_get, mocked_requests_request, mocked_utc_time_sans_frac):
        url = reverse('django_forest:authentication:callback')
        query = {
            'code': 'eslqHqk8Luo_3CIf5SanmXBpq_7ytlTV8HgoVFNPwUvmWKDiwnf9XV6Bo04zRon8',
            'state': '{"foo": 1}'
        }
        url = f'{url}?{urlencode(query)}'
        r = self.client.get(url)
        self.assertEqual(r.status_code, 401)
        r = r.json()
        self.assertEqual(r, {
            'errors': [
                {
                    'detail': 'Invalid response from the authentication server: the state does not contain a renderingId'
                }
            ]
        })

    @mock.patch('oic.utils.time_util.utc_time_sans_frac', return_value=1623431559)
    @mock.patch('requests.request', return_value=mocked_requests(mocked_token_response, 200))
    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_get_invalid_state(self, mocked_requests_get, mocked_requests_request, mocked_utc_time_sans_frac):
        url = reverse('django_forest:authentication:callback')
        query = {
            'code': 'eslqHqk8Luo_3CIf5SanmXBpq_7ytlTV8HgoVFNPwUvmWKDiwnf9XV6Bo04zRon8',
            'state': '{"renderingId": error}'
        }
        url = f'{url}?{urlencode(query)}'
        r = self.client.get(url)
        self.assertEqual(r.status_code, 401)
        r = r.json()
        self.assertEqual(r, {
            'errors': [
                {
                    'detail': 'Invalid response from the authentication server: the state parameter is not at the right format'
                }
            ]
        })

    @mock.patch('oic.utils.time_util.utc_time_sans_frac', return_value=1623427968)
    @mock.patch('requests.request', return_value=mocked_requests(mocked_token_response, 200))
    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_iat_issued_in_future_within_allowed_skew(self, mocked_requests_get, mocked_requests_request, mocked_utc_time_sans_frac):
        """
        Given an id_token that has an iat timestamp 1 second ahead of the current time,
        assert authentication is still successful.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    @mock.patch('oic.utils.time_util.utc_time_sans_frac', return_value=1623427963)
    @mock.patch('requests.request', return_value=mocked_requests(mocked_token_response, 200))
    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_iat_issued_in_future_outside_allowed_skew(self, mocked_requests_get, mocked_requests_request, mocked_utc_time_sans_frac):
        """
        Given an id_token that has an iat timestamp 11 second ahead of the current time,
        assert authentication is not successful.
        """
        with self.assertRaises(IATError):
            self.client.get(self.url)
