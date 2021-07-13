import copy
from datetime import datetime
from unittest import mock

import pytest
from django.test import TransactionTestCase
from django.urls import reverse
from pytz import timezone

from django_forest.tests.fixtures.schema import test_schema
from django_forest.utils.schema import Schema
from django_forest.utils.schema.json_api_schema import JsonApiSchema


class ResourceListFilterDateViewTests(TransactionTestCase):
    fixtures = ['question.json']

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, django_assert_num_queries):
        self._django_assert_num_queries = django_assert_num_queries

    def setUp(self):
        Schema.schema = copy.deepcopy(test_schema)
        Schema.handle_json_api_schema()
        self.url = reverse('django_forest:resources:list', kwargs={'resource': 'Question'})

    def tearDown(self):
        # reset _registry after each test
        JsonApiSchema._registry = {}

    @mock.patch('django_forest.resources.utils.queryset.filters.date.datetime')
    def test_past(self, mocked_now):
        mocked_now.now.return_value = datetime(2021, 6, 2, 15, 0, 0, 0, tzinfo=timezone('Europe/Paris'))
        response = self.client.get(self.url, {
            'fields[Question]': 'id,question_text,pub_date',
            'filters': '{"field":"pub_date","operator":"past","value":null}',
            'timezone': 'Europe/Paris',
            'page[number]': '1',
            'page[size]': '15'
        })
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {
            'data': [
                {
                    'type': 'question',
                    'id': 1,
                    'attributes': {
                        'pub_date': '2021-06-02T13:52:53.528000+00:00',
                        'question_text': 'what is your favorite color?'
                    },
                    'links': {
                        'self': '/forest/Question/1'
                    }
                }
            ]
        })

    @mock.patch('django_forest.resources.utils.queryset.filters.date.datetime')
    def test_future(self, mocked_now):
        mocked_now.now.return_value = datetime(2021, 6, 2, 15, 0, 0, 0, tzinfo=timezone('Europe/Paris'))
        response = self.client.get(self.url, {
            'fields[Question]': 'id,question_text,pub_date',
            'filters': '{"field":"pub_date","operator":"future","value":null}',
            'timezone': 'Europe/Paris',
            'page[number]': '1',
            'page[size]': '15'
        })
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {
            'data': [
                {
                    'type': 'question',
                    'attributes': {
                        'pub_date': '2021-06-02T15:52:53.528000+00:00',
                        'question_text': 'do you like chocolate?'
                    },
                    'id': 2,
                    'links': {
                        'self': '/forest/Question/2'
                    }
                },
                {
                    'type': 'question',
                    'attributes': {
                        'pub_date': '2021-06-03T13:52:53.528000+00:00',
                        'question_text': 'who is your favorite singer?'
                    },
                    'id': 3,
                    'links': {
                        'self': '/forest/Question/3'
                    }
                }
            ]
        })

    @mock.patch('django_forest.resources.utils.queryset.filters.date.datetime')
    def test_today(self, mocked_now):
        mocked_now.now.return_value = datetime(2021, 6, 2, 15, 0, 0, 0, tzinfo=timezone('Europe/Paris'))
        response = self.client.get(self.url, {
            'fields[Question]': 'id,question_text,pub_date',
            'filters': '{"field":"pub_date","operator":"today","value":null}',
            'timezone': 'Europe/Paris',
            'page[number]': '1',
            'page[size]': '15'
        })
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {
            'data': [
                {
                    'type': 'question',
                    'id': 1,
                    'attributes': {
                        'pub_date': '2021-06-02T13:52:53.528000+00:00',
                        'question_text': 'what is your favorite color?'
                    },
                    'links': {
                        'self': '/forest/Question/1'
                    }
                },
                {
                    'type': 'question',
                    'attributes': {
                        'pub_date': '2021-06-02T15:52:53.528000+00:00',
                        'question_text': 'do you like chocolate?'
                    },
                    'id': 2,
                    'links': {
                        'self': '/forest/Question/2'
                    }
                }
            ]
        })

    @mock.patch('django_forest.resources.utils.queryset.filters.date.datetime')
    def test_before_x_hours_ago(self, mocked_now):
        mocked_now.now.return_value = datetime(2021, 6, 2, 15, 53, 0, 0, tzinfo=timezone('Europe/Paris'))
        response = self.client.get(self.url, {
            'fields[Question]': 'id,question_text,pub_date',
            'filters': '{"field":"pub_date","operator":"before_x_hours_ago","value":1}',
            'timezone': 'Europe/Paris',
            'page[number]': '1',
            'page[size]': '15'
        })
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {
            'data': [
                {
                    'type': 'question',
                    'id': 1,
                    'attributes': {
                        'pub_date': '2021-06-02T13:52:53.528000+00:00',
                        'question_text': 'what is your favorite color?'
                    },
                    'links': {
                        'self': '/forest/Question/1'
                    }
                }
            ]
        })

    @mock.patch('django_forest.resources.utils.queryset.filters.date.datetime')
    def test_after_x_hours_ago(self, mocked_now):
        mocked_now.now.return_value = datetime(2021, 6, 2, 15, 53, 0, 0, tzinfo=timezone('Europe/Paris'))
        response = self.client.get(self.url, {
            'fields[Question]': 'id,question_text,pub_date',
            'filters': '{"field":"pub_date","operator":"after_x_hours_ago","value":1}',
            'timezone': 'Europe/Paris',
            'page[number]': '1',
            'page[size]': '15'
        })
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {
            'data': [
                {
                    'type': 'question',
                    'attributes': {
                        'pub_date': '2021-06-02T15:52:53.528000+00:00',
                        'question_text': 'do you like chocolate?'
                    },
                    'id': 2,
                    'links': {
                        'self': '/forest/Question/2'
                    }
                },
                {
                    'type': 'question',
                    'attributes': {
                        'pub_date': '2021-06-03T13:52:53.528000+00:00',
                        'question_text': 'who is your favorite singer?'
                    },
                    'id': 3,
                    'links': {
                        'self': '/forest/Question/3'
                    }
                }
            ]
        })

    @mock.patch('django_forest.resources.utils.queryset.filters.date.datetime')
    def test_previous_quarter(self, mocked_now):
        mocked_now.now.return_value = datetime(2021, 7, 1, 0, 0, 0, 0, tzinfo=timezone('Europe/Paris'))
        response = self.client.get(self.url, {
            'fields[Question]': 'id,question_text,pub_date',
            'filters': '{"field":"pub_date","operator":"previous_quarter","value":null}',
            'timezone': 'Europe/Paris',
            'page[number]': '1',
            'page[size]': '15'
        })
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {
            'data': [
                {
                    'type': 'question',
                    'id': 1,
                    'attributes': {
                        'pub_date': '2021-06-02T13:52:53.528000+00:00',
                        'question_text': 'what is your favorite color?'
                    },
                    'links': {
                        'self': '/forest/Question/1'
                    }
                },
                {
                    'type': 'question',
                    'attributes': {
                        'pub_date': '2021-06-02T15:52:53.528000+00:00',
                        'question_text': 'do you like chocolate?'
                    },
                    'id': 2,
                    'links': {
                        'self': '/forest/Question/2'
                    }
                },
                {
                    'type': 'question',
                    'attributes': {
                        'pub_date': '2021-06-03T13:52:53.528000+00:00',
                        'question_text': 'who is your favorite singer?'
                    },
                    'id': 3,
                    'links': {
                        'self': '/forest/Question/3'
                    }
                }
            ]
        })

    @mock.patch('django_forest.resources.utils.queryset.filters.date.datetime')
    def test_previous_quarter_to_date(self, mocked_now):
        mocked_now.now.return_value = datetime(2021, 6, 30, 23, 59, 59, 999999, tzinfo=timezone('Europe/Paris'))
        response = self.client.get(self.url, {
            'fields[Question]': 'id,question_text,pub_date',
            'filters': '{"field":"pub_date","operator":"previous_quarter_to_date","value":null}',
            'timezone': 'Europe/Paris',
            'page[number]': '1',
            'page[size]': '15'
        })
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {
            'data': [
                {
                    'type': 'question',
                    'id': 1,
                    'attributes': {
                        'pub_date': '2021-06-02T13:52:53.528000+00:00',
                        'question_text': 'what is your favorite color?'
                    },
                    'links': {
                        'self': '/forest/Question/1'
                    }
                },
                {
                    'type': 'question',
                    'attributes': {
                        'pub_date': '2021-06-02T15:52:53.528000+00:00',
                        'question_text': 'do you like chocolate?'
                    },
                    'id': 2,
                    'links': {
                        'self': '/forest/Question/2'
                    }
                },
                {
                    'type': 'question',
                    'attributes': {
                        'pub_date': '2021-06-03T13:52:53.528000+00:00',
                        'question_text': 'who is your favorite singer?'
                    },
                    'id': 3,
                    'links': {
                        'self': '/forest/Question/3'
                    }
                }
            ]
        })
