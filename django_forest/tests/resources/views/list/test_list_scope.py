import copy
from datetime import datetime
from unittest import mock

import pytest
import pytz
from django.test import TransactionTestCase
from django.urls import reverse
from freezegun import freeze_time

from django_forest.tests.fixtures.schema import test_schema
from django_forest.tests.utils.test_forest_api_requester import mocked_requests
from django_forest.utils.schema import Schema
from django_forest.utils.schema.json_api_schema import JsonApiSchema
from django_forest.utils.scope import ScopeManager
from django_forest.utils.date import get_timezone

mocked_scope = {
    'tests_question': {
        'scope': {
            'filter': {
                'aggregator': 'and',
                'conditions': [
                    {
                        'field': 'question_text',
                        'operator': 'contains',
                        'value': 'color'
                    },
                ]
            },
            'dynamicScopesValues': {}
        }
    }
}

mocked_scope_dynamic_value = {
    'tests_question': {
        'scope': {
            'filter': {
                'aggregator': 'or',
                'conditions': [
                    {
                        'field': 'question_text',
                        'operator': 'contains',
                        'value': 'color'
                    },
                    {
                        'field': 'question_text',
                        'operator': 'contains',
                        'value': '$currentUser.name'
                    }
                ]
            },
            'dynamicScopesValues': {
                'users': {
                    '1': {
                        '$currentUser.name': 'singer'
                    }
                }
            }
        }
    }
}


def mocked_requests_scope(value, *args):
    def m(url, **kwargs):
        if url == 'https://api.test.forestadmin.com/liana/scopes':
            return mocked_requests(value['scope']['data'], value['scope']['status'])

    return m


class ResourceListScopeViewTests(TransactionTestCase):
    fixtures = ['question.json', 'choice.json']

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, django_assert_num_queries):
        self._django_assert_num_queries = django_assert_num_queries

    def setUp(self):
        Schema.schema = copy.deepcopy(test_schema)
        Schema.handle_json_api_schema()
        self.url = reverse('django_forest:resources:list', kwargs={'resource': 'tests_question'})
        self.reverse_url = reverse('django_forest:resources:list', kwargs={'resource': 'tests_choice'})
        self.client = self.client_class(
            HTTP_AUTHORIZATION='Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjUiLCJlbWFpbCI6Imd1aWxsYXVtZWNAZm9yZXN0YWRtaW4uY29tIiwiZmlyc3RfbmFtZSI6Ikd1aWxsYXVtZSIsImxhc3RfbmFtZSI6IkNpc2NvIiwidGVhbSI6Ik9wZXJhdGlvbnMiLCJyZW5kZXJpbmdfaWQiOjEsImV4cCI6MTYyNTY3OTYyNi44ODYwMTh9.mHjA05yvMr99gFMuFv0SnPDCeOd2ZyMSN868V7lsjnw')

    def tearDown(self):
        # reset _registry after each test
        JsonApiSchema._registry = {}
        ScopeManager.cache = {}

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @freeze_time(
        lambda: datetime(2021, 7, 8, 9, 20, 23, 582772, tzinfo=get_timezone('UTC'))
    )
    def test_scope_cached(self, mocked_decode):
        ScopeManager.cache = {
            '1': {
                'scopes': mocked_scope,
                'fetched_at': datetime(2021, 7, 8, 9, 20, 22, 582772, tzinfo=pytz.UTC)
            }
        }
        response = self.client.get(self.url, {
            'fields[tests_question]': 'id,topic,question_text,pub_date',
            'fields[topic]': 'name',
            'timezone': 'Europe/Paris',
            'page[number]': '1',
            'page[size]': '15'
        })
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {
            'data': [
                {
                    'type': 'tests_question',
                    'id': 1,
                    'attributes': {
                        'pub_date': '2021-06-02T13:52:53.528000+00:00',
                        'question_text': 'what is your favorite color?'
                    },
                    'links': {
                        'self': '/forest/tests_question/1'
                    },
                    'relationships': {'topic': {'data': None,
                                                'links': {'related': '/forest/tests_question/1/relationships/topic'}}},
                }
            ]
        })

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @mock.patch('requests.get', side_effect=mocked_requests_scope({
        'scope': {
            'data': mocked_scope,
            'status': 200
        }
    }))
    def test_scope_simple(self, mocked_requests, mocked_decode):
        response = self.client.get(self.url, {
            'fields[tests_question]': 'id,topic,question_text,pub_date',
            'fields[topic]': 'name',
            'timezone': 'Europe/Paris',
            'page[number]': '1',
            'page[size]': '15'
        })
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {
            'data': [
                {
                    'type': 'tests_question',
                    'id': 1,
                    'attributes': {
                        'pub_date': '2021-06-02T13:52:53.528000+00:00',
                        'question_text': 'what is your favorite color?'
                    },
                    'links': {
                        'self': '/forest/tests_question/1'
                    },
                    'relationships': {'topic': {'data': None,
                                                'links': {'related': '/forest/tests_question/1/relationships/topic'}}},
                }
            ]
        })

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1, 'name': 'singer'})
    @mock.patch('requests.get', side_effect=mocked_requests_scope({
        'scope': {
            'data': mocked_scope_dynamic_value,
            'status': 200
        }
    }))
    def test_scope_aggregator_dynamic_values(self, mocked_requests, mocked_decode):
        response = self.client.get(self.url, {
            'fields[tests_question]': 'id,topic,question_text,pub_date',
            'fields[topic]': 'name',
            'timezone': 'Europe/Paris',
            'page[number]': '1',
            'page[size]': '15'
        })
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {
            'data': [
                {
                    'type': 'tests_question',
                    'id': 1,
                    'attributes': {
                        'pub_date': '2021-06-02T13:52:53.528000+00:00',
                        'question_text': 'what is your favorite color?'
                    },
                    'links': {
                        'self': '/forest/tests_question/1'
                    },
                    'relationships': {'topic': {'data': None,
                                                'links': {'related': '/forest/tests_question/1/relationships/topic'}}},
                },
                {
                    'type': 'tests_question',
                    'id': 3,
                    'attributes': {
                        'pub_date': '2021-06-03T13:52:53.528000+00:00',
                        'question_text': 'who is your favorite singer?'
                    },
                    'links': {
                        'self': '/forest/tests_question/3'
                    },
                    'relationships': {'topic': {'data': None,
                                                'links': {'related': '/forest/tests_question/3/relationships/topic'}}},
                },
            ]
        })

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @mock.patch('requests.get', side_effect=mocked_requests_scope({
        'scope': {
            'data': {},
            'status': 400
        }
    }))
    def test_scope_no_response(self, mocked_requests, mocked_decode):
        response = self.client.get(self.url, {
            'fields[tests_question]': 'id,question_text,pub_date',
            'timezone': 'Europe/Paris',
            'page[number]': '1',
            'page[size]': '15'
        })
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {
            'errors': [
                {
                    'detail': 'Unable to fetch scopes'
                }
            ]
        })

    @mock.patch('jose.jwt.decode', return_value={'id': 1})
    def test_scope_bad_token(self, mocked_decode):
        response = self.client.get(self.url, {
            'fields[tests_question]': 'id,question_text,pub_date',
            'timezone': 'Europe/Paris',
            'page[number]': '1',
            'page[size]': '15'
        })
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {
            'errors': [
                {
                    'detail': 'Missing required rendering_id'
                }
            ]
        })
