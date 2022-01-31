import copy
import json
from datetime import datetime
from unittest import mock

from django.test import TransactionTestCase
from django.urls import reverse
from freezegun import freeze_time

from django_forest.tests.fixtures.schema import test_schema
from django_forest.utils.schema import Schema
from django_forest.utils.schema.json_api_schema import JsonApiSchema
from django_forest.utils.scope import ScopeManager
from django_forest.utils.date import get_timezone

@mock.patch('django_forest.utils.scope.ScopeManager._has_cache_expired', return_value=False)
@mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})    
class StatsStatsWithParametersViewTests(TransactionTestCase):
    fixtures = ['question.json', 'choice.json', ]

    def setUp(self):
        Schema.schema = copy.deepcopy(test_schema)
        Schema.handle_json_api_schema()
        self.url = f"{reverse('django_forest:stats:statsWithParameters', kwargs={'resource': 'tests_question'})}?timezone=Europe%2FParis"
        self.empty_url = f"{reverse('django_forest:stats:statsWithParameters', kwargs={'resource': 'tests_waiter'})}?timezone=Europe%2FParis"
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

    def test_get_value_count(self, *args, **kwargs):
        body = {
            'aggregate': 'Count',
            'collection': 'tests_question',
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

    def test_get_value_sum(self, *args, **kwargs):
        body = {
            'aggregate': 'Sum',
            'aggregate_field': 'id',
            'collection': 'tests_question',
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

    def test_get_value_sum_empty(self, *args, **kwargs):
        body = {
            'aggregate': 'Sum',
            'aggregate_field': 'id',
            'collection': 'tests_waiter',
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

    @freeze_time(
        lambda: datetime(2021, 6, 4, 9, 20, 22, 582772, tzinfo=get_timezone('UTC'))
    )
    def test_get_value_count_previous_yesterday(self, *args, **kwargs):
        body = {
            'aggregate': 'Count',
            'collection': 'tests_question',
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

    @freeze_time(
        lambda: datetime(2021, 6, 4, 9, 20, 22, 582772, tzinfo=get_timezone('UTC'))
    )
    def test_get_value_count_previous_yesterday_aggregator(self, *args, **kwargs):
        body = {
            'aggregate': 'Count',
            'collection': 'tests_question',
            'filters': "{\"aggregator\":\"and\",\"conditions\":[{\"field\":\"pub_date\",\"operator\":\"yesterday\",\"value\":null},{\"field\":\"pub_date\",\"operator\":\"present\",\"value\":null}]}",
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

    @freeze_time(
        lambda: datetime(2021, 7, 4, 9, 20, 22, 582772, tzinfo=get_timezone('UTC'))
    )
    def test_get_value_count_previous_month(self, *args, **kwargs):
        body = {
            'aggregate': 'Count',
            'collection': 'tests_question',
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

    @freeze_time(
        lambda: datetime(2021, 7, 4, 9, 20, 22, 582772, tzinfo=get_timezone('UTC'))
    )
    def test_get_value_count_previous_quarter(self, *args, **kwargs):
        body = {
            'aggregate': 'Count',
            'collection': 'tests_question',
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

    @freeze_time(
        lambda: datetime(2021, 7, 4, 9, 20, 22, 582772, tzinfo=get_timezone('UTC'))
    )
    def test_get_value_count_previous_quarter_to_date(self, *args, **kwargs):
        body = {
            'aggregate': 'Count',
            'collection': 'tests_question',
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

    @freeze_time(
        lambda: datetime(2022, 7, 4, 9, 20, 22, 582772, tzinfo=get_timezone('UTC'))
    )
    def test_get_value_count_previous_year(self, *args, **kwargs):
        body = {
            'aggregate': 'Count',
            'collection': 'tests_question',
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

    def test_get_objective_count(self, *args, **kwargs):
        body = {
            'aggregate': 'Count',
            'collection': 'tests_question',
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

    def test_get_pie_count(self, *args, **kwargs):
        body = {
            'aggregate': 'Count',
            'collection': 'tests_question',
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

    def test_get_pie_sum(self, *args, **kwargs):
        body = {
            'aggregate': 'Sum',
            'aggregate_field': 'id',
            'collection': 'tests_question',
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

    def test_get_line_count_day(self, *args, **kwargs):
        body = {
            'aggregate': 'Count',
            'collection': 'tests_question',
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

    def test_get_line_count_week(self, *args, **kwargs):
        body = {
            'aggregate': 'Count',
            'collection': 'tests_question',
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

    def test_get_line_count_month(self, *args, **kwargs):
        body = {
            'aggregate': 'Count',
            'collection': 'tests_question',
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

    def test_get_line_count_year(self, *args, **kwargs):
        body = {
            'aggregate': 'Count',
            'collection': 'tests_question',
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

    def test_get_line_count_empty(self, *args, **kwargs):
        body = {
            'aggregate': 'Count',
            'collection': 'tests_question',
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

    def test_get_leaderboard_count(self, *args, **kwargs):
        body = {
            'aggregate': 'Count',
            'collection': 'tests_question',
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
