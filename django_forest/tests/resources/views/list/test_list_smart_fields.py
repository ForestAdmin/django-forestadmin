import copy
import sys
from datetime import datetime
from unittest import mock

import pytest
import pytz
from django.test import TransactionTestCase
from django.urls import reverse
from freezegun import freeze_time

from django_forest.resources.utils.smart_field import SmartFieldMixin
from django_forest.tests.fixtures.schema import test_schema
from django_forest.utils.collection import Collection
from django_forest.utils.schema import Schema
from django_forest.utils.schema.json_api_schema import JsonApiSchema
from django_forest.utils.date import get_timezone


# reset forest config dir auto import
from django_forest.utils.scope import ScopeManager


@pytest.fixture()
def reset_config_dir_import():
    for key in list(sys.modules.keys()):
        if key.startswith('django_forest.tests.forest'):
            del sys.modules[key]


@pytest.mark.usefixtures('reset_config_dir_import')
class ResourceListSmartFieldsViewTests(TransactionTestCase):
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
        Schema.schema = copy.deepcopy(test_schema)
        Schema.add_smart_features()
        Schema.handle_json_api_schema()
        self.url = reverse('django_forest:resources:list', kwargs={'resource': 'tests_question'})
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
    @freeze_time(
        lambda: datetime(2021, 7, 8, 9, 20, 23, 582772, tzinfo=get_timezone('UTC'))
    )
    def test_get(self, mocked_decode):
        response = self.client.get(self.url, {
            'fields[tests_question]': 'id,topic,question_text,pub_date,foo,bar',
            'fields[topic]': 'name',
            'page[number]': '1',
            'page[size]': '15'
        })
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {
            'data': [
                {
                    'type': 'tests_question',
                    'attributes': {
                        'pub_date': '2021-06-02T13:52:53.528000+00:00',
                        'question_text': 'what is your favorite color?',
                        'foo': 'what is your favorite color?+foo',
                        'bar': 'what is your favorite color?+bar'
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
                {
                    'type': 'tests_question',
                    'attributes': {
                        'pub_date': '2021-06-02T15:52:53.528000+00:00',
                        'question_text': 'do you like chocolate?',
                        'foo': 'do you like chocolate?+foo',
                        'bar': 'do you like chocolate?+bar'
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
                        'pub_date': '2021-06-03T13:52:53.528000+00:00',
                        'question_text': 'who is your favorite singer?',
                        'foo': 'who is your favorite singer?+foo',
                        'bar': 'who is your favorite singer?+bar'
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
                }
            ]
        })

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @freeze_time(
        lambda: datetime(2021, 7, 8, 9, 20, 23, 582772, tzinfo=get_timezone('UTC'))
    )
    def test_get_filter_callable(self, mocked_decode):
        response = self.client.get(self.url, {
            'fields[tests_question]': 'id,topic,question_text,pub_date,foo,bar',
            'fields[topic]': 'name',
            'filters': '{"field":"foo","operator":"contains","value":"favorite"}',
            'page[number]': '1',
            'page[size]': '15'
        })
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {
            'data': [
                {
                    'type': 'tests_question',
                    'attributes': {
                        'question_text': 'what is your favorite color?',
                        'pub_date': '2021-06-02T13:52:53.528000+00:00',
                        'foo': 'what is your favorite color?+foo',
                        'bar': 'what is your favorite color?+bar'
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
                {
                    'type': 'tests_question',
                    'attributes': {
                        'question_text': 'who is your favorite singer?',
                        'pub_date': '2021-06-03T13:52:53.528000+00:00',
                        'foo': 'who is your favorite singer?+foo',
                        'bar': 'who is your favorite singer?+bar'},
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
                }
            ]
        })

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @freeze_time(
        lambda: datetime(2021, 7, 8, 9, 20, 23, 582772, tzinfo=get_timezone('UTC'))
    )
    def test_get_filter_string(self, mocked_decode):
        response = self.client.get(self.url, {
            'fields[tests_question]': 'id,topic,question_text,pub_date,foo,bar',
            'fields[topic]': 'name',
            'filters': '{"field":"bar","operator":"contains","value":"favorite"}',
            'page[number]': '1',
            'page[size]': '15'
        })
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {
            'data': [
                {
                    'type': 'tests_question',
                    'attributes': {
                        'question_text': 'what is your favorite color?',
                        'pub_date': '2021-06-02T13:52:53.528000+00:00',
                        'foo': 'what is your favorite color?+foo',
                        'bar': 'what is your favorite color?+bar'
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
                {
                    'type': 'tests_question',
                    'attributes': {
                        'question_text': 'who is your favorite singer?',
                        'pub_date': '2021-06-03T13:52:53.528000+00:00',
                        'foo': 'who is your favorite singer?+foo',
                        'bar': 'who is your favorite singer?+bar'},
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
                }
            ]
        })

    @mock.patch.object(SmartFieldMixin, "_add_smart_fields")
    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @freeze_time(
        lambda: datetime(2021, 7, 8, 9, 20, 23, 582772, tzinfo=get_timezone('UTC'))
    )
    def test_smart_fields_not_requested_not_calculated(self, _, _add_smart_fields):
        """
        Given
            - A collection is queried, where the smart fields are not
              part of the query parameters
        Then
            - The smart fields should not be fetched at all.
        """

        response = self.client.get(self.url, {
            'fields[tests_question]': 'id,topic,question_text,pub_date',
            'page[number]': '1',
            'page[size]': '15'
        })

        self.assertEqual(response.status_code, 200)

        # The thing we really care about in this integration
        # test is not adding *any* smart fields to the request
        _add_smart_fields.assert_not_called()
