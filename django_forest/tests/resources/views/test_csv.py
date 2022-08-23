import copy
import sys
from unittest import mock

import pytest
from django.test import TransactionTestCase
from django.urls import reverse

from django_forest.tests.fixtures.schema import test_schema
from django_forest.utils.schema import Schema
from django_forest.utils.schema.json_api_schema import JsonApiSchema


# reset forest config dir auto import
from django_forest.utils.scope import ScopeManager


@pytest.fixture()
def reset_config_dir_import():
    for key in list(sys.modules.keys()):
        if key.startswith('django_forest.tests.forest'):
            del sys.modules[key]


@mock.patch('django_forest.utils.scope.ScopeManager._has_cache_expired', return_value=False)
@mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})    
@pytest.mark.usefixtures('reset_config_dir_import')
class ResourceCsvViewTests(TransactionTestCase):
    fixtures = ['question.json', 'choice.json', ]

    def setUp(self):
        Schema.schema = copy.deepcopy(test_schema)
        Schema.add_smart_features()
        Schema.handle_json_api_schema()
        self.url = reverse('django_forest:resources:csv', kwargs={'resource': 'tests_question'})
        self.reverse_url = reverse('django_forest:resources:csv', kwargs={'resource': 'tests_choice'})
        self.client = self.client_class(
            HTTP_AUTHORIZATION='Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjUiLCJlbWFpbCI6Imd1aWxsYXVtZWNAZm9yZXN0YWRtaW4uY29tIiwiZmlyc3RfbmFtZSI6Ikd1aWxsYXVtZSIsImxhc3RfbmFtZSI6IkNpc2NvIiwidGVhbSI6Ik9wZXJhdGlvbnMiLCJyZW5kZXJpbmdfaWQiOjEsImV4cCI6MTYyNTY3OTYyNi44ODYwMTh9.mHjA05yvMr99gFMuFv0SnPDCeOd2ZyMSN868V7lsjnw')
        ScopeManager.cache = {
            '1': {
                'scopes': {},
                'fetched_at': 'useless-here'
            }
        }

    def tearDown(self):
        # reset _registry after each test
        JsonApiSchema._registry = {}
        ScopeManager.cache = {}

    def test_get(self, *args, **kwargs):
        response = self.client.get(self.url, {
            'fields[tests_question]': 'id,topic,question_text,pub_date,foo,bar',
            'fields[topic]': 'name',
            'search': '',
            'filters': '',
            'searchExtended': 0,
            'filename': 'questions',
            'header': 'id,topic,question text,pub date,foo,bar',
            'timezone': 'Europe/Paris',
            'page[number]': 10, # csv get should ignore these. If it doesn't we'll only receive the column names, but no rows
            'page[size]': 100
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'),
                         'id,topic,question text,pub date,foo,bar\r\n1,,what is your favorite color?,2021-06-02T13:52:53.528000+00:00,what is your favorite color?+foo,what is your favorite color?+bar\r\n2,,do you like chocolate?,2021-06-02T15:52:53.528000+00:00,do you like chocolate?+foo,do you like chocolate?+bar\r\n3,,who is your favorite singer?,2021-06-03T13:52:53.528000+00:00,who is your favorite singer?+foo,who is your favorite singer?+bar\r\n')

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @mock.patch('django_forest.utils.scope.ScopeManager._has_cache_expired', return_value=False)
    def test_get_related_data(self, *args, **kwargs):
        response = self.client.get(self.reverse_url, {
            'fields[tests_choice]': 'id,question,topic,choice_text',
            'fields[question]': 'question_text',
            'fields[topic]': 'name',
            'search': '',
            'filters': '',
            'searchExtended': 0,
            'filename': 'choices',
            'header': 'id,choice text',
            'timezone': 'Europe/Paris'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'),
                         'id,choice text,,\r\n1,what is your favorite color?,,yes\r\n2,what is your favorite color?,,no\r\n3,do you like chocolate?,,good\r\n')

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @mock.patch('django_forest.utils.scope.ScopeManager._has_cache_expired', return_value=False)
    def test_wrong_operator(self, *args, **kwargs):
        response = self.client.get(self.url, {
            'fields[tests_question]': 'id,question_text,pub_date,foo,bar',
            'search': '',
            'filters': '{"field":"question_text","operator":"foo","value":"what is your favorite color?"}',
            'searchExtended': 0,
            'filename': 'questions',
            'header': 'id,question text,pub date,foo,bar',
            'timezone': 'Europe/Paris'
        })
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {
            'errors': [
                {
                    'detail': 'Unknown provided operator foo'
                }
            ]
        })
