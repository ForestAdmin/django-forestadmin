import copy
from unittest import mock

from django.test import TransactionTestCase
from django.urls import reverse
from django.conf import settings
from django_forest.middleware.deactivate_count import DeactivateCountMiddleware

from django_forest.tests.fixtures.schema import test_schema
from django_forest.utils.schema import Schema
from django_forest.utils.schema.json_api_schema import JsonApiSchema
from django_forest.utils.scope import ScopeManager


class CustomDeactivateCountMiddleware(DeactivateCountMiddleware):

    def is_deactivated(self, request, view_func, *args, **kwargs):
        is_deactivated = super().is_deactivated(request,view_func, *args, **kwargs)
        return is_deactivated and 'search' in request.GET


@mock.patch('django_forest.utils.scope.ScopeManager._has_cache_expired', return_value=False)
class ResourceCountViewTests(TransactionTestCase):
    fixtures = ['article.json', 'publication.json', 'session.json', 'question.json', 'choice.json']


    def setUp(self):
        Schema.schema = copy.deepcopy(test_schema)
        Schema.handle_json_api_schema()
        self.client = self.client_class(
            HTTP_AUTHORIZATION='Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjUiLCJlbWFpbCI6Imd1aWxsYXVtZWNAZm9yZXN0YWRtaW4uY29tIiwiZmlyc3RfbmFtZSI6Ikd1aWxsYXVtZSIsImxhc3RfbmFtZSI6IkNpc2NvIiwidGVhbSI6Ik9wZXJhdGlvbnMiLCJyZW5kZXJpbmdfaWQiOjEsImV4cCI6MTYyNTY3OTYyNi44ODYwMTh9.mHjA05yvMr99gFMuFv0SnPDCeOd2ZyMSN868V7lsjnw')
        ScopeManager.cache = {
            '1': {
                'scopes': {},
                'fetched_at': 'useless_here'
            }
        }

    def tearDown(self):
        # reset _registry after each test
        JsonApiSchema._registry = {}
        ScopeManager.cache = {}

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    def test_get(self, *args, **kwargs):
        url = reverse('django_forest:resources:count', kwargs={'resource': 'tests_question'})
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {'count': 3})
    
    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    def test_deactivate(self, *args, **kwargs):
        settings.MIDDLEWARE.insert(0, 'django_forest.middleware.DeactivateCountMiddleware')
        settings.FOREST['DEACTIVATED_COUNT'] = ['tests_question']
        url = reverse('django_forest:resources:count', kwargs={'resource': 'tests_question'})
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {'meta': {'count': 'deactivated'}})
        
        settings.FOREST['DEACTIVATED_COUNT'] = ['tests_fake']
        url = reverse('django_forest:resources:count', kwargs={'resource': 'tests_question'})
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {'count': 3})
        
        settings.FOREST['DEACTIVATED_COUNT'] = {}
        del settings.MIDDLEWARE[0]
        print(settings.MIDDLEWARE)

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    def test_custom_deactivate(self, *args, **kwargs):
        del settings.MIDDLEWARE[0]
        settings.MIDDLEWARE.insert(0, 'django_forest.tests.resources.views.test_count.CustomDeactivateCountMiddleware')
        print(settings.MIDDLEWARE)
        settings.FOREST['DEACTIVATED_COUNT'] = ['tests_question']
        url = reverse('django_forest:resources:count', kwargs={'resource': 'tests_question'})
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {'count': 3})

        url = reverse('django_forest:resources:count', kwargs={'resource': 'tests_question'})
        response = self.client.get(url, {
            'search': 'yes',
        })
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {'meta': {'count': 'deactivated'}})
        del settings.MIDDLEWARE[0]

    @mock.patch('jose.jwt.decode', return_value={'id': 1})
    def test_get_invalid_token(self, *args, **kwargs):
        url = reverse('django_forest:resources:count', kwargs={'resource': 'tests_question'})
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {'errors': [{'detail': 'Missing required rendering_id'}]})

    def test_get_no_model(self, *args, **kwargs):
        url = reverse('django_forest:resources:count', kwargs={'resource': 'Foo'})
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {'errors': [{'detail': 'no model found for resource Foo'}]})
