from unittest import mock

from django.test import TestCase

from django_forest.authentication.oidc.dynamic_client_registrator import register
from django_forest.tests.utils.test_forest_api_requester import mocked_requests

mocked_client_credentials = {
    'token_endpoint_auth_method': 'none',
    'redirect_uris': ['http://localhost:8000/forest/authentication/callback'],
    'registration_endpoint': 'https://api.development.forestadmin.com/oidc/reg',
    'application_type': 'web',
    'grant_types': ['authorization_code'],
    'response_types': ['code'],
    'environment_id': 101,
    'client_id': 'eyJraWQiOiI2eWthczh5SVMxdHM3dmZZY3JJRTd3aG1Wc2hwbHVKLUlDbU1pRWszYWJ3IiwiYWxnIjoiUlMyNTYifQ.eyJ0b2tlbl9lbmRwb2ludF9hdXRoX21ldGhvZCI6Im5vbmUiLCJyZWRpcmVjdF91cmlzIjpbImh0dHA6Ly9sb2NhbGhvc3Q6ODAwMC9mb3Jlc3QvYXV0aGVudGljYXRpb24vY2FsbGJhY2siXSwicmVnaXN0cmF0aW9uX2VuZHBvaW50IjoiaHR0cHM6Ly9hcGkuZGV2ZWxvcG1lbnQuZm9yZXN0YWRtaW4uY29tL29pZGMvcmVnIiwiYXBwbGljYXRpb25fdHlwZSI6IndlYiIsImdyYW50X3R5cGVzIjpbImF1dGhvcml6YXRpb25fY29kZSJdLCJyZXNwb25zZV90eXBlcyI6WyJjb2RlIl0sImVudmlyb25tZW50X2lkIjoxMDEsImlzcyI6IkZPUkVTVF9BVVRIRU5USUNBVElPTl9TWVNURU0iLCJpYXQiOjE2MjM0Mjc5NTV9.P_mC8eCr36RqRye8YI5zUSGuq4GmpFf8RLvzQmnVMk2HXqzQToPao_RAyvGpYC4JUjFmuTdGI6SSg9JVGIzNod2AXFAxp8qmK8ax_TBKUlg_F_mzrzOxEOaiFkiCQAhavlBhNCx56_CRBmyt_5Uv6L-E4_ezG0A1kacPfOPZaBNSj8FqCRxrsnVZVq60RmY7tRl0DX50ZUuSEvh0zzZLwayBuTYgxLLdg6EvR52dsJHlv0KgNlnHJwKB74cSAl9CM3PVHym9Eg3V3B_BaAbu0eIKmqtJ7_1h1w3-YsH4jAC-czQNgzgO79IiY2s0tTREe4vv-P-__BJ8lIyFxcgzuQ'
}


class AuthenticationOidcDynamicClientRegistratorTests(TestCase):

    def setUp(self):
        self.metadata = {
            'token_endpoint_auth_method': 'none',
            'redirect_uris': ['http://localhost:8000/authentication/callback'],
            'registration_endpoint': 'https://api.development.forestadmin.com/oidc/reg'
        }

    @mock.patch('requests.post', return_value=mocked_requests(mocked_client_credentials, 201))
    def test_register(self, mocked_requests_post):
        client_credentials = register(self.metadata)
        self.assertEqual(client_credentials, mocked_client_credentials)

    @mock.patch('requests.post', return_value=mocked_requests({'foo': 'bar'}, 400))
    def test_register_exception(self, mocked_requests_post):
        with self.assertRaises(Exception) as cm:
            register(self.metadata)
        self.assertEqual(cm.exception.args[0],'The registration to the authentication API failed, response: {"foo": "bar"}')

    @mock.patch('requests.post', return_value=mocked_requests({'error': 'foo'}, 400))
    def test_register_error(self, mocked_requests_post):
        with self.assertRaises(Exception) as cm:
            register(self.metadata)
        self.assertEqual(cm.exception.args[0], {'error': 'foo'})
