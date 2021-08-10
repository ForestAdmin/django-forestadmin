import json
import sys
from unittest import mock

import pytest
from django.test import TransactionTestCase
from django.urls import reverse

from django_forest.utils.schema import Schema
from django_forest.utils.schema.json_api_schema import JsonApiSchema


# reset forest config dir auto import
@pytest.fixture()
def reset_config_dir_import():
    for key in list(sys.modules.keys()):
        if key.startswith('django_forest.tests.forest'):
            del sys.modules[key]


@pytest.mark.usefixtures('reset_config_dir_import')
class LoadHooksViewTests(TransactionTestCase):
    fixtures = ['question.json']

    def setUp(self):
        Schema.build_schema()
        Schema.add_smart_features()
        Schema.handle_json_api_schema()
        self.url = reverse('django_forest:actions:hooks:load', kwargs={'action_name': 'send-invoice'})
        self.not_exists_url = reverse('django_forest:actions:hooks:load', kwargs={'action_name': 'not-exists'})
        self.client = self.client_class(
            HTTP_AUTHORIZATION='Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjUiLCJlbWFpbCI6Imd1aWxsYXVtZWNAZm9yZXN0YWRtaW4uY29tIiwiZmlyc3RfbmFtZSI6Ikd1aWxsYXVtZSIsImxhc3RfbmFtZSI6IkNpc2NvIiwidGVhbSI6Ik9wZXJhdGlvbnMiLCJyZW5kZXJpbmdfaWQiOjEsImV4cCI6MTYyNTY3OTYyNi44ODYwMTh9.mHjA05yvMr99gFMuFv0SnPDCeOd2ZyMSN868V7lsjnw')

    def tearDown(self):
        # reset _registry after each test
        JsonApiSchema._registry = {}

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    def test_load(self, mocked_decode):
        body = {
            'recordIds': ['70'],
            'collectionName': 'tests_question'
        }
        response = self.client.post(self.url, json.dumps(body), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data, {
            'fields': [
                {'field': 'country', 'type': 'Enum', 'enums': ['FR', 'US'], 'isReadOnly': False, 'isRequired': False,
                 'defaultValue': None, 'integration': None, 'reference': None, 'description': None, 'widget': None,
                 'position': 0, 'value': None},
                {'field': 'phones', 'type': ['Enum'], 'enums': [['01', '02'], ['998', '999']], 'isReadOnly': False,
                 'isRequired': False, 'defaultValue': None, 'integration': None, 'reference': None, 'description': None,
                 'widget': None, 'position': 1, 'value': None},
                {'field': 'city', 'type': 'String', 'hook': 'cityChange', 'isReadOnly': False, 'isRequired': False,
                 'defaultValue': None, 'integration': None, 'reference': None, 'description': None, 'widget': None,
                 'position': 2}, {'field': 'zip code', 'type': 'String', 'hook': 'zipCodeChange', 'isReadOnly': False,
                                  'isRequired': False, 'defaultValue': None, 'integration': None, 'reference': None,
                                  'description': None, 'widget': None, 'position': 3}]})

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    def test_load_not_exists(self, mocked_decode):
        body = {
            'recordIds': ['70'],
            'collectionName': 'tests_question'
        }
        response = self.client.post(self.not_exists_url, json.dumps(body), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data, {'errors': [{'detail': 'action not found'}]})


@pytest.mark.usefixtures('reset_config_dir_import')
class LoadHooksViewNoTokenTests(TransactionTestCase):
    fixtures = ['question.json']

    def setUp(self):
        Schema.build_schema()
        Schema.add_smart_features()
        Schema.handle_json_api_schema()
        self.url = reverse('django_forest:actions:hooks:load', kwargs={'action_name': 'send-invoice'})

    def tearDown(self):
        # reset _registry after each test
        JsonApiSchema._registry = {}

    def test_load(self):
        body = {
            'recordIds': ['70'],
            'collectionName': 'tests_question'
        }
        response = self.client.post(self.url, json.dumps(body), content_type='application/json')
        self.assertEqual(response.status_code, 403)
