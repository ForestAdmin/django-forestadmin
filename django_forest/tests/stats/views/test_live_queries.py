import copy
import json

from django.test import TransactionTestCase
from django.urls import reverse

from django_forest.tests.fixtures.schema import test_schema
from django_forest.utils.schema import Schema
from django_forest.utils.schema.json_api_schema import JsonApiSchema
from django_forest.utils.scope import ScopeManager


class StatsLiveQueriesViewTests(TransactionTestCase):
    fixtures = ['question.json', 'choice.json',]

    def setUp(self):
        Schema.schema = copy.deepcopy(test_schema)
        Schema.handle_json_api_schema()
        self.url = f"{reverse('django_forest:stats:liveQueries')}?timezone=Europe%2FParis"

    def tearDown(self):
        # reset _registry after each test
        JsonApiSchema._registry = {}
        ScopeManager.cache = {}

    def test_get_value(self):
        body = {
            'query': '''SELECT COUNT(*) as value
                        FROM tests_question''',
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

    def test_get_value_wrong(self):
        body = {
            'query': '''SELECT COUNT(*) as id__count
                        FROM tests_question''',
            'type': 'Value'
        }

        response = self.client.post(self.url, json.dumps(body), content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {
            'errors': [
                {
                    'detail': "The result column must be named 'value' instead of 'id__count'."
                }
            ]
        })

    def test_get_value_wrong_parameters(self):
        body = {
            'query': '''SELECT COUNT(*) as key, 5 as value
                        FROM tests_question''',
            'type': 'Value'
        }

        response = self.client.post(self.url, json.dumps(body), content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {
            'errors': [
                {
                    'detail': "The result column must be named 'value'"
                }
            ]
        })

    def test_get_objective(self):
        body = {
            'query': '''SELECT COUNT(*) as value, 5 as objective
                        FROM tests_question''',
            'type': 'Objective'
        }

        response = self.client.post(self.url, json.dumps(body), content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['data']['attributes'], {
            'value': {
                'value': 3,
                'objective': 5
            }
        })
        self.assertEqual(data['data']['type'], 'stats')

    def test_get_objective_wrong(self):
        body = {
            'query': '''SELECT COUNT(*) as value
                        FROM tests_question''',
            'type': 'Objective'
        }

        response = self.client.post(self.url, json.dumps(body), content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {
            'errors': [
                {
                    'detail': "The result columns must be named 'value' and 'objective'."
                }
            ]
        })

    def test_get_objective_wrong_parameters(self):
        body = {
            'query': '''SELECT COUNT(*) as key, 5 as value
                        FROM tests_question''',
            'type': 'Objective'
        }

        response = self.client.post(self.url, json.dumps(body), content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {
            'errors': [
                {
                    'detail': "The result columns must be named 'value', 'objective' instead of 'key', 'value'."
                }
            ]
        })

    def test_get_pie(self):
        body = {
            'query': '''SELECT tests_question.question_text as key,
                          COUNT(tests_question.id) AS value
                          FROM tests_question
                          WHERE tests_question.pub_date IS NOT NULL
                          GROUP BY tests_question.question_text
                          ORDER BY tests_question.question_text ASC''',
            'type': 'Pie'
        }

        response = self.client.post(self.url, json.dumps(body), content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['data']['attributes'], {
            'value': [
                {
                    'key': 'do you like chocolate?',
                    'value': 1
                },
                {
                    'key': 'what is your favorite color?',
                    'value': 1
                },
                {
                    'key': 'who is your favorite singer?',
                    'value': 1
                }
            ]
        })
        self.assertEqual(data['data']['type'], 'stats')

    def test_get_line(self):
        body = {
            'query': '''SELECT tests_question.pub_date as key,
                        COUNT(tests_question.id) AS value
                        FROM tests_question
                        GROUP BY tests_question.pub_date 
                        ORDER BY tests_question.pub_date
                        ASC''',
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
                },
            ]
        })
        self.assertEqual(data['data']['type'], 'stats')

    def test_get_line_date(self):
        body = {
            'query': '''SELECT tests_question.pub_date as key,
                        COUNT(tests_question.id) AS value
                        FROM tests_question
                        GROUP BY tests_question.pub_date
                        ORDER BY tests_question.pub_date
                        ASC''',
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
                },
            ]
        })
        self.assertEqual(data['data']['type'], 'stats')

    def test_get_leaderboard(self):
        body = {
            'query': '''SELECT tests_question.question_text as key,
                        COUNT(tests_choice.id) AS value
                        FROM tests_question
                        LEFT OUTER JOIN tests_choice ON (tests_question.id = tests_choice.question_id)
                        GROUP BY tests_question.question_text
                        ORDER BY value
                        DESC LIMIT 5''',
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
