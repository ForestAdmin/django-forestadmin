import copy
from datetime import datetime
from unittest import mock

import pytz
from django.test import TransactionTestCase
from django.urls import reverse

from django_forest.tests.fixtures.schema import test_schema
from django_forest.utils.schema import Schema
from django_forest.utils.schema.json_api_schema import JsonApiSchema
from django_forest.utils.scope import ScopeManager


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
                'fetched_at': datetime(2021, 7, 8, 9, 20, 22, 582772, tzinfo=pytz.UTC)
            }
        }

    def tearDown(self):
        # reset _registry after each test
        JsonApiSchema._registry = {}
        ScopeManager.cache = {}

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @mock.patch('django_forest.utils.scope.datetime')
    def test_get(self, mocked_datetime, mocked_decode):
        mocked_datetime.now.return_value = datetime(2021, 7, 8, 9, 20, 23, 582772, tzinfo=pytz.UTC)
        url = reverse('django_forest:resources:count', kwargs={'resource': 'tests_question'})
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {'count': 3})

    @mock.patch('jose.jwt.decode', return_value={'id': 1})
    @mock.patch('django_forest.utils.scope.datetime')
    def test_get_invalid_token(self, mocked_datetime, mocked_decode):
        mocked_datetime.now.return_value = datetime(2021, 7, 8, 9, 20, 23, 582772, tzinfo=pytz.UTC)
        url = reverse('django_forest:resources:count', kwargs={'resource': 'tests_question'})
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {'errors': [{'detail': 'Missing required rendering_id'}]})

    def test_get_no_model(self):
        url = reverse('django_forest:resources:count', kwargs={'resource': 'Foo'})
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {'errors': [{'detail': 'no model found for resource Foo'}]})
