from datetime import datetime
from unittest import mock
import sys

import pytest
import pytz
from django.test import TransactionTestCase
from django.urls import reverse

from django_forest.utils.collection import Collection
from django_forest.utils.schema import Schema
from django_forest.utils.schema.json_api_schema import JsonApiSchema
from django_forest.utils.scope import ScopeManager


# reset forest config dir auto import
@pytest.fixture()
def reset_config_dir_import():
    for key in list(sys.modules.keys()):
        if key.startswith('django_forest.tests.forest'):
            del sys.modules[key]


@pytest.mark.usefixtures('reset_config_dir_import')
class ResourceListViewTests(TransactionTestCase):
    fixtures = ['article.json', 'publication.json',
                'session.json',
                'question.json', 'choice.json',
                'place.json', 'restaurant.json',
                'student.json',
                'serial.json']

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, django_assert_num_queries):
        self._django_assert_num_queries = django_assert_num_queries

    def setUp(self):
        Schema.build_schema()
        Schema.add_smart_features()
        Schema.handle_json_api_schema()
        self.url = reverse('django_forest:resources:list', kwargs={'resource': 'tests_question'})
        self.reverse_url = reverse('django_forest:resources:list', kwargs={'resource': 'tests_choice'})
        self.no_data_url = reverse('django_forest:resources:list', kwargs={'resource': 'tests_waiter'})
        self.enum_url = reverse('django_forest:resources:list', kwargs={'resource': 'tests_student'})
        self.uuid_url = reverse('django_forest:resources:list', kwargs={'resource': 'tests_serial'})
        self.one_to_one_url = reverse('django_forest:resources:list', kwargs={'resource': 'tests_restaurant'})
        self.bad_url = reverse('django_forest:resources:list', kwargs={'resource': 'tests_foo'})
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
        Collection._registry = {}

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @mock.patch('django_forest.utils.scope.ScopeManager._has_cache_expired', return_value=False)
    def test_get_sort(self, mocked_datetime, mocked_decode):
        with self._django_assert_num_queries(1) as captured:
            response = self.client.get(self.url, {
                'fields[tests_question]': 'id,topic,question_text,pub_date',
                'fields[topic]': 'name',
                'page[number]': 1,
                'page[size]': 15,
                'sort': '-id',
                'searchExtended': 0
            })
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(captured.captured_queries[0]['sql'],
                         ' '.join('''SELECT "tests_question"."id", "tests_question"."question_text", "tests_question"."pub_date", "tests_question"."topic_id"
                          FROM "tests_question"
                           ORDER BY "tests_question"."id"
                           DESC
                           LIMIT 15'''.replace('\n', ' ').split()))
        self.assertEqual(data, {
            'data': [
                {
                    'type': 'tests_question',
                    'attributes': {
                        'pub_date': '2021-06-03T13:52:53.528000+00:00',
                        'question_text': 'who is your favorite singer?'
                    },
                    'id': 3,
                    'links': {
                        'self': '/forest/tests_question/3'
                    },
                    'relationships': {
                        'topic': {
                            'data': None,
                            'links': {
                                'related': '/forest/tests_question/3/relationships/topic'
                            }
                        }
                    },
                },
                {
                    'type': 'tests_question',
                    'attributes': {
                        'pub_date': '2021-06-02T15:52:53.528000+00:00',
                        'question_text': 'do you like chocolate?'
                    },
                    'id': 2,
                    'links': {
                        'self': '/forest/tests_question/2'
                    },
                    'relationships': {
                        'topic': {
                            'data': None,
                            'links': {
                                'related': '/forest/tests_question/2/relationships/topic'
                            }
                        }
                    },
                },
                {
                    'type': 'tests_question',
                    'attributes': {
                        'pub_date': '2021-06-02T13:52:53.528000+00:00',
                        'question_text': 'what is your favorite color?'
                    },
                    'id': 1,
                    'links': {
                        'self': '/forest/tests_question/1'
                    },
                    'relationships': {
                        'topic': {
                            'data': None,
                            'links': {
                                'related': '/forest/tests_question/1/relationships/topic'
                            }
                        }
                    },
                },
            ]
        })

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @mock.patch('django_forest.utils.scope.ScopeManager._has_cache_expired', return_value=False)
    def test_get_sort_related_data(self, mocked_scope_has_expired, mocked_decode):
        with self._django_assert_num_queries(7) as captured:
            response = self.client.get(self.reverse_url, {
                'fields[tests_choice]': 'id,topic,question,choice_text',
                'fields[topic]': 'name',
                'fields[question]': 'question_text',
                'page[number]': 1,
                'page[size]': 15,
                'sort': 'question.question_text',
                'searchExtended': 0
            })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(captured.captured_queries[0]['sql'],
                         ' '.join('''SELECT "tests_choice"."id", "tests_choice"."question_id", "tests_choice"."choice_text"
                          FROM "tests_choice"
                           LEFT OUTER JOIN "tests_question" ON ("tests_choice"."question_id" = "tests_question"."id")
                          ORDER BY "tests_question"."question_text"
                          ASC
                          LIMIT 15'''.replace('\n', ' ').split()))
