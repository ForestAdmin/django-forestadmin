from unittest import mock

from django.test import TestCase
from oic.oic import Client

from django_forest.tests.authentication.oidc.test_configuration_retriever import mocked_config
from django_forest.tests.authentication.oidc.test_dynamic_client_registrator import mocked_client_credentials
from django_forest.authentication.oidc.client_manager import OidcClientManager


class AuthenticationOidcClientManagerTests(TestCase):

    def setUp(self):
        self.callback_url = 'http://localhost:8000/authentication/callback'

    def tearDown(self):
        OidcClientManager.client = None

    @mock.patch('django_forest.authentication.oidc.client_manager.retrieve', return_value=mocked_config)
    @mock.patch('django_forest.authentication.oidc.client_manager.register', return_value=mocked_client_credentials)
    def test_client_manager(self, mocked_register, mocked_retrieve):
        client = OidcClientManager.get_client_for_callback_url(self.callback_url)
        self.assertTrue(mocked_retrieve.called)
        self.assertTrue(mocked_register.called)
        self.assertTrue(isinstance(client, Client))
        self.assertEqual(client.client_id, 'eyJraWQiOiI2eWthczh5SVMxdHM3dmZZY3JJRTd3aG1Wc2hwbHVKLUlDbU1pRWszYWJ3IiwiYWxnIjoiUlMyNTYifQ.eyJ0b2tlbl9lbmRwb2ludF9hdXRoX21ldGhvZCI6Im5vbmUiLCJyZWRpcmVjdF91cmlzIjpbImh0dHA6Ly9sb2NhbGhvc3Q6ODAwMC9mb3Jlc3QvYXV0aGVudGljYXRpb24vY2FsbGJhY2siXSwicmVnaXN0cmF0aW9uX2VuZHBvaW50IjoiaHR0cHM6Ly9hcGkuZGV2ZWxvcG1lbnQuZm9yZXN0YWRtaW4uY29tL29pZGMvcmVnIiwiYXBwbGljYXRpb25fdHlwZSI6IndlYiIsImdyYW50X3R5cGVzIjpbImF1dGhvcml6YXRpb25fY29kZSJdLCJyZXNwb25zZV90eXBlcyI6WyJjb2RlIl0sImVudmlyb25tZW50X2lkIjoxMDEsImlzcyI6IkZPUkVTVF9BVVRIRU5USUNBVElPTl9TWVNURU0iLCJpYXQiOjE2MjM0MDg2OTZ9.u3uCPv4kjPHOr3BlTSwDx5AXYFTN1ntQ-_N4CkAQSfrfWWNzDnMuN6UjnGX8tNPzehUtOu5dtkIFKMeGBA3CXRUQvkddnmZn2vktqPTufF4T16IvbQW_4ef_Qca09MqLSHh16lksXmQ3HoaqAEBm528qN8HgXSv261CxzISrrz5suIo7b7J-TNSpKDa6YpH1wi2cUs6Pg15dr_kAxaDGr5I6iCIBQHVnnwxSjBnpv0OAbT8khJLF3QR1oX_d1y5AlYgoopTG70YWuO1P6EeoTWsEn0g4Ji8Cqw61Lm4l2M_rjKZDvopqzqhjD59ob4XU8tdX3kShYTyNa_gwT_WgcQ')
        self.assertEqual(client.redirect_uris, [])
        self.assertEqual(client.issuer, 'https://api.development.forestadmin.com')
        self.assertEqual(client.authorization_endpoint, 'https://api.development.forestadmin.com/oidc/auth')
        self.assertEqual(client.token_endpoint, 'https://api.development.forestadmin.com/oidc/token')
        self.assertEqual(client.keyjar.issuer_keys['https://api.development.forestadmin.com'][0].source, 'https://api.development.forestadmin.com/oidc/jwks')

    @mock.patch('django_forest.authentication.oidc.client_manager.retrieve')
    @mock.patch('django_forest.authentication.oidc.client_manager.register')
    def test_client_manager_memo(self, mocked_register, mocked_retrieve):
        OidcClientManager.client = 'foo'
        client = OidcClientManager.get_client_for_callback_url(self.callback_url)
        self.assertEqual(client, 'foo')
        self.assertFalse(mocked_retrieve.called)
        self.assertFalse(mocked_register.called)

    @mock.patch('django_forest.authentication.oidc.client_manager.retrieve', side_effect=Exception('foo'))
    def test_client_manager_exception(self, mocked_retrieve):
        with self.assertRaises(Exception) as cm:
            OidcClientManager.get_client_for_callback_url(self.callback_url)
        self.assertEqual(cm.exception.args[0], 'foo')

