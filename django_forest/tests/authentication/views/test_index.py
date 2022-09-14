from unittest import mock

from django.test import TestCase
from django.urls import reverse

from django_forest.authentication.oidc.client_manager import OidcClientManager
from django_forest.tests.authentication.oidc.test_configuration_retriever import mocked_config
from django_forest.tests.authentication.oidc.test_dynamic_client_registrator import mocked_client_credentials


class AuthenticationIndexViewTests(TestCase):

    def setUp(self):
        self.retrieve_patcher = mock.patch('django_forest.authentication.oidc.client_manager.retrieve',
                                           return_value=mocked_config)
        self.register_patcher = mock.patch('django_forest.authentication.oidc.client_manager.register',
                                           return_value=mocked_client_credentials)
        self.mocked_retrieve = self.retrieve_patcher.start()
        self.mocked_register = self.register_patcher.start()
        self.oidc_client = OidcClientManager.get_client()

    def tearDown(self):
        OidcClientManager.client = None
        self.oidc_client = None
        self.retrieve_patcher.stop()
        self.register_patcher.stop()

    def test_post(self):
        response = self.client.post(reverse('django_forest:authentication:index'),
                                    {'renderingId': '1'},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        r = response.json()
        self.assertEqual(r, {
            'authorizationUrl': 'https://api.development.forestadmin.com/oidc/auth?client_id=eyJraWQiOiI2eWthczh5SVMxdHM3dmZZY3JJRTd3aG1Wc2hwbHVKLUlDbU1pRWszYWJ3IiwiYWxnIjoiUlMyNTYifQ.eyJ0b2tlbl9lbmRwb2ludF9hdXRoX21ldGhvZCI6Im5vbmUiLCJyZWRpcmVjdF91cmlzIjpbImh0dHA6Ly9sb2NhbGhvc3Q6ODAwMC9mb3Jlc3QvYXV0aGVudGljYXRpb24vY2FsbGJhY2siXSwicmVnaXN0cmF0aW9uX2VuZHBvaW50IjoiaHR0cHM6Ly9hcGkuZGV2ZWxvcG1lbnQuZm9yZXN0YWRtaW4uY29tL29pZGMvcmVnIiwiYXBwbGljYXRpb25fdHlwZSI6IndlYiIsImdyYW50X3R5cGVzIjpbImF1dGhvcml6YXRpb25fY29kZSJdLCJyZXNwb25zZV90eXBlcyI6WyJjb2RlIl0sImVudmlyb25tZW50X2lkIjoxMDEsImlzcyI6IkZPUkVTVF9BVVRIRU5USUNBVElPTl9TWVNURU0iLCJpYXQiOjE2MjM0Mjc5NTV9.P_mC8eCr36RqRye8YI5zUSGuq4GmpFf8RLvzQmnVMk2HXqzQToPao_RAyvGpYC4JUjFmuTdGI6SSg9JVGIzNod2AXFAxp8qmK8ax_TBKUlg_F_mzrzOxEOaiFkiCQAhavlBhNCx56_CRBmyt_5Uv6L-E4_ezG0A1kacPfOPZaBNSj8FqCRxrsnVZVq60RmY7tRl0DX50ZUuSEvh0zzZLwayBuTYgxLLdg6EvR52dsJHlv0KgNlnHJwKB74cSAl9CM3PVHym9Eg3V3B_BaAbu0eIKmqtJ7_1h1w3-YsH4jAC-czQNgzgO79IiY2s0tTREe4vv-P-__BJ8lIyFxcgzuQ&response_type=code&scope=openid+email+profile&state=%7B%22renderingId%22%3A+1%7D&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fforest%2Fauthentication%2Fcallback'
        })

    def test_post_no_rendering(self):
        response = self.client.post(reverse('django_forest:authentication:index'),
                                    {'foo': '1'},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 401)
        r = response.json()
        self.assertEqual(r,
                         {'errors': [{'detail': 'Authentication request must contain a renderingId'}]})

    def test_post_bad_rendering(self):
        response = self.client.post(reverse('django_forest:authentication:index'),
                                    {'renderingId': ['foo']},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 401)
        r = response.json()
        self.assertEqual(r,
                         {'errors': [{'detail': 'The parameter renderingId is not valid'}]})
