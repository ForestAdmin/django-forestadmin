from unittest import mock

from django.test import TestCase

from django_forest.authentication.oidc.configuration_retriever import retrieve
from django_forest.tests.utils.test_forest_api_requester import mocked_requests

mocked_config = {
    'authorization_endpoint': 'https://api.development.forestadmin.com/oidc/auth',
    'device_authorization_endpoint': 'https://api.development.forestadmin.com/oidc/device/auth',
    'claims_parameter_supported': False,
    'claims_supported': ['sub', 'email', 'sid', 'auth_time', 'iss'],
    'code_challenge_methods_supported': ['S256'],
    'end_session_endpoint': 'https://api.development.forestadmin.com/oidc/session/end',
    'grant_types_supported': ['authorization_code', 'urn:ietf:params:oauth:grant-type:device_code'],
    'id_token_signing_alg_values_supported': ['HS256', 'RS256'],
    'issuer': 'https://api.development.forestadmin.com',
    'jwks_uri': 'https://api.development.forestadmin.com/oidc/jwks',
    'registration_endpoint': 'https://api.development.forestadmin.com/oidc/reg',
    'response_modes_supported': ['query'],
    'response_types_supported': ['code', 'none'],
    'scopes_supported': ['openid', 'email', 'profile'],
    'subject_types_supported': ['public'],
    'token_endpoint_auth_methods_supported': ['none'],
    'token_endpoint_auth_signing_alg_values_supported': [],
    'token_endpoint': 'https://api.development.forestadmin.com/oidc/token',
    'request_object_signing_alg_values_supported': ['HS256', 'RS256'],
    'request_parameter_supported': False,
    'request_uri_parameter_supported': True,
    'require_request_uri_registration': True,
    'claim_types_supported': ['normal']
}


class AuthenticationOidcConfigurationRetrieverTests(TestCase):

    @mock.patch('requests.get', return_value=mocked_requests(mocked_config, 200))
    def test_retrieve(self, mocked_requests_get):
        configuration = retrieve()
        self.assertEqual(configuration, mocked_config)

    @mock.patch('requests.get', return_value=mocked_requests({'error': 'error'}, 400))
    def test_retrieve_error(self, mocked_requests_get):
        with self.assertRaises(Exception) as cm:
            retrieve()

        self.assertEqual(cm.exception.args[0], 'Failed to retrieve the provider\'s configuration.')
