import copy
import json
from datetime import datetime
from unittest import mock

import pytz
from django.test import TransactionTestCase
from django.urls import reverse

from django_forest.tests.fixtures.schema import test_schema
from django_forest.utils.schema import Schema
from django_forest.utils.schema.json_api_schema import JsonApiSchema


class StatsStatsWithParametersViewTests(TransactionTestCase):
    fixtures = ['question.json', 'choice.json', ]

    def setUp(self):
        Schema.schema = copy.deepcopy(test_schema)
        Schema.handle_json_api_schema()
        self.url = f"{reverse('django_forest:stats:statsWithParameters', kwargs={'resource': 'Question'})}?timezone=Europe%2FParis"
        self.empty_url = f"{reverse('django_forest:stats:statsWithParameters', kwargs={'resource': 'Waiter'})}?timezone=Europe%2FParis"

    def tearDown(self):
        # reset _registry after each test
        JsonApiSchema._registry = {}

    def test_get_value_count(self):
        body = {
            'aggregate': 'Count',
            'collection': 'Question',
            'query': None,
            'time_range': None,
            'type': 'Value'
        }

        response = self.client.post(self.url, json.dumps(body), content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['data']['attributes'], {
            'value': {
                'countCurrent': 3
            }
        })
        self.assertEqual(data['data']['type'], 'stats')

    def test_get_value_sum(self):
        body = {
            'aggregate': 'Sum',
            'aggregate_field': 'id',
            'collection': 'Question',
            'query': None,
            'time_range': None,
            'type': 'Value'
        }

        response = self.client.post(self.url, json.dumps(body), content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['data']['attributes'], {
            'value': {
                'countCurrent': 6
            }
        })
        self.assertEqual(data['data']['type'], 'stats')

    def test_get_value_sum_empty(self):
        body = {
            'aggregate': 'Sum',
            'aggregate_field': 'id',
            'collection': 'Waiter',
            'query': None,
            'time_range': None,
            'type': 'Value'
        }

        response = self.client.post(self.empty_url, json.dumps(body), content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['data']['attributes'], {
            'value': {
                'countCurrent': 0
            }
        })
        self.assertEqual(data['data']['type'], 'stats')

    @mock.patch('django_forest.resources.utils.queryset.filters.date.datetime')
    def test_get_value_count_previous_yesterday(self, mocked_datetime):
        mocked_datetime.now.return_value = datetime(2021, 6, 4, 9, 20, 22, 582772, tzinfo=pytz.UTC)
        body = {
            'aggregate': 'Count',
            'collection': 'Question',
            'filters': "{\"field\":\"pub_date\",\"operator\":\"yesterday\",\"value\":null}",
            'query': None,
            'time_range': None,
            'type': 'Value'
        }

        response = self.client.post(self.url, json.dumps(body), content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['data']['attributes'], {
            'value': {
                'countCurrent': 1,
                'countPrevious': 2
            }
        })
        self.assertEqual(data['data']['type'], 'stats')

    @mock.patch('django_forest.resources.utils.queryset.filters.date.datetime')
    def test_get_value_count_previous_month(self, mocked_datetime):
        mocked_datetime.now.return_value = datetime(2021, 7, 4, 9, 20, 22, 582772, tzinfo=pytz.UTC)
        body = {
            'aggregate': 'Count',
            'collection': 'Question',
            'filters': "{\"field\":\"pub_date\",\"operator\":\"previous_month\",\"value\":null}",
            'query': None,
            'time_range': None,
            'type': 'Value'
        }

        response = self.client.post(self.url, json.dumps(body), content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['data']['attributes'], {
            'value': {
                'countCurrent': 3,
                'countPrevious': 0
            }
        })
        self.assertEqual(data['data']['type'], 'stats')

    @mock.patch('django_forest.resources.utils.queryset.filters.date.datetime')
    def test_get_value_count_previous_quarter(self, mocked_datetime):
        mocked_datetime.now.return_value = datetime(2021, 7, 4, 9, 20, 22, 582772, tzinfo=pytz.UTC)
        body = {
            'aggregate': 'Count',
            'collection': 'Question',
            'filters': "{\"field\":\"pub_date\",\"operator\":\"previous_quarter\",\"value\":null}",
            'query': None,
            'time_range': None,
            'type': 'Value'
        }

        response = self.client.post(self.url, json.dumps(body), content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['data']['attributes'], {
            'value': {
                'countCurrent': 3,
                'countPrevious': 0
            }
        })
        self.assertEqual(data['data']['type'], 'stats')

    @mock.patch('django_forest.resources.utils.queryset.filters.date.datetime')
    def test_get_value_count_previous_quarter_to_date(self, mocked_datetime):
        mocked_datetime.now.return_value = datetime(2021, 7, 4, 9, 20, 22, 582772, tzinfo=pytz.UTC)
        body = {
            'aggregate': 'Count',
            'collection': 'Question',
            'filters': "{\"field\":\"pub_date\",\"operator\":\"previous_quarter_to_date\",\"value\":null}",
            'query': None,
            'time_range': None,
            'type': 'Value'
        }

        response = self.client.post(self.url, json.dumps(body), content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['data']['attributes'], {
            'value': {
                'countCurrent': 0,
                'countPrevious': 3
            }
        })
        self.assertEqual(data['data']['type'], 'stats')

    @mock.patch('django_forest.resources.utils.queryset.filters.date.datetime')
    def test_get_value_count_previous_year(self, mocked_datetime):
        mocked_datetime.now.return_value = datetime(2022, 7, 4, 9, 20, 22, 582772, tzinfo=pytz.UTC)
        body = {
            'aggregate': 'Count',
            'collection': 'Question',
            'filters': "{\"field\":\"pub_date\",\"operator\":\"previous_year\",\"value\":null}",
            'query': None,
            'time_range': None,
            'type': 'Value'
        }

        response = self.client.post(self.url, json.dumps(body), content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['data']['attributes'], {
            'value': {
                'countCurrent': 3,
                'countPrevious': 0
            }
        })
        self.assertEqual(data['data']['type'], 'stats')

    def test_get_objective_count(self):
        body = {
            'aggregate': 'Count',
            'collection': 'Question',
            'query': None,
            'time_range': None,
            'type': 'Objective'
        }

        response = self.client.post(self.url, json.dumps(body), content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['data']['attributes'], {
            'value': {
                'value': 3
            }
        })
        self.assertEqual(data['data']['type'], 'stats')

    def test_get_pie_count(self):
        body = {
            'aggregate': 'Count',
            'collection': 'Question',
            'query': None,
            'group_by_field': 'pub_date',
            'type': 'Pie'
        }

        response = self.client.post(self.url, json.dumps(body), content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['data']['attributes'], {
            'value': [
                {
                    'key': '02/06/2021',
                    'value': 2
                },
                {
                    'key': '03/06/2021',
                    'value': 1
                }
            ]
        })
        self.assertEqual(data['data']['type'], 'stats')

    def test_get_pie_sum(self):
        body = {
            'aggregate': 'Sum',
            'aggregate_field': 'id',
            'collection': 'Question',
            'query': None,
            'group_by_field': 'pub_date',
            'type': 'Pie'
        }

        response = self.client.post(self.url, json.dumps(body), content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['data']['attributes'], {
            'value': [
                {
                    'key': '02/06/2021',
                    'value': 3
                },
                {
                    'key': '03/06/2021',
                    'value': 3
                }
            ]
        })
        self.assertEqual(data['data']['type'], 'stats')

    def test_get_line_count_day(self):
        body = {
            'aggregate': 'Count',
            'collection': 'Question',
            'time_range': 'Day',
            'group_by_date_field': 'pub_date',
            'type': 'Line'
        }

        response = self.client.post(self.url, json.dumps(body), content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['data']['attributes'], {
            'value': [
                {
                    'label': '02/06/2021',
                    'values': {
                        'value': 2
                    }
                },
                {
                    'label': '03/06/2021',
                    'values': {
                        'value': 1
                    }
                }
            ]
        })
        self.assertEqual(data['data']['type'], 'stats')

    def test_get_line_count_week(self):
        body = {
            'aggregate': 'Count',
            'collection': 'Question',
            'time_range': 'Week',
            'group_by_date_field': 'pub_date',
            'type': 'Line'
        }

        response = self.client.post(self.url, json.dumps(body), content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['data']['attributes'], {
            'value': [
                {
                    'label': 'W22-2021',
                    'values': {
                        'value': 3
                    }
                }
            ]
        })
        self.assertEqual(data['data']['type'], 'stats')

    def test_get_line_count_month(self):
        body = {
            'aggregate': 'Count',
            'collection': 'Question',
            'time_range': 'Month',
            'group_by_date_field': 'pub_date',
            'type': 'Line'
        }

        response = self.client.post(self.url, json.dumps(body), content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['data']['attributes'], {
            'value': [
                {
                    'label': 'Jun 21',
                    'values': {
                        'value': 3
                    }
                },
            ]
        })
        self.assertEqual(data['data']['type'], 'stats')

    def test_get_line_count_year(self):
        body = {
            'aggregate': 'Count',
            'collection': 'Question',
            'time_range': 'Year',
            'group_by_date_field': 'pub_date',
            'type': 'Line'
        }

        response = self.client.post(self.url, json.dumps(body), content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['data']['attributes'], {
            'value': [
                {
                    'label': '2021',
                    'values': {
                        'value': 3
                    }
                },
            ]
        })
        self.assertEqual(data['data']['type'], 'stats')

    def test_get_line_count_empty(self):
        body = {
            'aggregate': 'Count',
            'collection': 'Question',
            'filters': "{\"field\":\"id\",\"operator\":\"equal\",\"value\":0}",
            'time_range': 'Day',
            'group_by_date_field': 'pub_date',
            'type': 'Line'
        }

        response = self.client.post(self.url, json.dumps(body), content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['data']['attributes'], {
            'value': []
        })
        self.assertEqual(data['data']['type'], 'stats')

    def test_get_leaderboard_count(self):
        body = {
            'aggregate': 'Count',
            'collection': 'Question',
            'label_field': 'question_text',
            'limit': 5,
            'query': None,
            'time_range': None,
            'relationship_field': 'choice_set',
            'type': 'Leaderboard'
        }

        response = self.client.post(self.url, json.dumps(body), content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['data']['attributes'], {
            'value': [
                {
                    'key': 'what is your favorite color?',
                    'value': 2
                },
                {
                    'key': 'do you like chocolate?',
                    'value': 1
                },
                {
                    'key': 'who is your favorite singer?',
                    'value': 0
                }
            ]
        })
        self.assertEqual(data['data']['type'], 'stats')
