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
class ChangeHooksViewTests(TransactionTestCase):
    fixtures = ['question.json', 'choice.json', ]

    def setUp(self):
        Schema.build_schema()
        Schema.add_smart_features()
        Schema.handle_json_api_schema()
        self.url = reverse('django_forest:actions:hooks:change', kwargs={'action_name': 'send-invoice'})
        self.client = self.client_class(
            HTTP_AUTHORIZATION='Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjUiLCJlbWFpbCI6Imd1aWxsYXVtZWNAZm9yZXN0YWRtaW4uY29tIiwiZmlyc3RfbmFtZSI6Ikd1aWxsYXVtZSIsImxhc3RfbmFtZSI6IkNpc2NvIiwidGVhbSI6Ik9wZXJhdGlvbnMiLCJyZW5kZXJpbmdfaWQiOjEsImV4cCI6MTYyNTY3OTYyNi44ODYwMTh9.mHjA05yvMr99gFMuFv0SnPDCeOd2ZyMSN868V7lsjnw')

    def tearDown(self):
        # reset _registry after each test
        JsonApiSchema._registry = {}

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    def test_change(self, mocked_decode):
        body = {
            'fields': [
                {
                    'field': 'country',
                    'type': 'Enum',
                    'reference': None,
                    'enums': [
                        'FR',
                        'US'
                    ],
                    'description': None,
                    'isRequired': None,
                    'value': 'FR',
                    'previousValue': 'FR',
                    'widgetEdit': {
                        'name': 'dropdown',
                        'parameters': {
                            'isSearchable': False
                        }
                    },
                    'isReadOnly': None
                },
                {
                    'field': 'city',
                    'type': 'String',
                    'reference': None,
                    'enums': None,
                    'description': None,
                    'isRequired': None,
                    'value': 'foo',
                    'previousValue': None,
                    'widgetEdit': {
                        'name': 'text editor',
                        'parameters': {}
                    },
                    'isReadOnly': None,
                    'hook': 'cityChange'
                },
                {
                    'field': 'zip code',
                    'type': 'String',
                    'reference': None,
                    'enums': None,
                    'description': None,
                    'isRequired': None,
                    'value': None,
                    'previousValue': None,
                    'widgetEdit': {
                        'name': 'text editor',
                        'parameters': {}
                    },
                    'isReadOnly': None,
                    'hook': 'zipCodeChange'
                }
            ],
            'recordIds': [
                '70'
            ],
            'collectionName': 'tests_question',
            'changedField': 'city'
        }
        response = self.client.post(self.url, json.dumps(body), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data, {
            'fields': [
                {'field': 'country', 'type': 'Enum', 'reference': None, 'enums': ['FR', 'US'], 'description': None,
                 'isRequired': None, 'value': 'FR', 'previousValue': 'FR',
                 'widgetEdit': {'name': 'dropdown', 'parameters': {'isSearchable': False}}, 'isReadOnly': None},
                {'field': 'city', 'type': 'String', 'reference': None, 'enums': None, 'description': None,
                 'isRequired': None, 'value': 'foo', 'previousValue': None,
                 'widgetEdit': {'name': 'text editor', 'parameters': {}}, 'isReadOnly': None, 'hook': 'cityChange'},
                {'field': 'zip code', 'type': 'String', 'reference': None, 'enums': None, 'description': None,
                 'isRequired': None, 'value': '83', 'previousValue': None,
                 'widgetEdit': {'name': 'text editor', 'parameters': {}}, 'isReadOnly': None,
                 'hook': 'zipCodeChange'}]
        })
