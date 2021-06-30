import copy
import json

from django.test import TransactionTestCase
from django.urls import reverse

from django_forest.tests.fixtures.schema import test_schema
from django_forest.tests.models import Question
from django_forest.utils.schema import Schema
from django_forest.utils.schema.json_api_schema import JsonApiSchema


class ResourceListViewTests(TransactionTestCase):
    fixtures = ['article.json', 'publication.json', 'session.json', 'question.json', 'choice.json']

    def setUp(self):
        Schema.schema = copy.deepcopy(test_schema)
        Schema.handle_json_api_serializer()
        self.url = reverse('resources:list', kwargs={'resource': 'Question'})
        self.bad_url = reverse('resources:list', kwargs={'resource': 'Foo'})

    def tearDown(self):
        # reset _registry after each test
        JsonApiSchema._registry = {}

    def test_get(self):
        response = self.client.get(self.url, {'page[number]': '1', 'page[size]': '15'})
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {
            'data': [
                {
                    'type': 'question',
                    'id': 1,
                    'links': {
                        'self': '/forest/Question/1'
                    }
                },
                {
                    'type': 'question',
                    'id': 2,
                    'links': {
                        'self': '/forest/Question/2'
                    }
                }
            ]
        })

    def test_get_no_model(self):
        response = self.client.get(self.bad_url, {'page[number]': '1', 'page[size]': '15'})
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {'errors': [{'detail': 'no model found for resource Foo'}]})

    def test_post(self):
        body = {
            'data': {
                'attributes': {
                    'question_text': 'What is your favorite color',
                    'pub_date': '2021-06-21T09:46:39.000Z'
                }
            }
        }
        self.assertEqual(Question.objects.count(), 2)
        response = self.client.post(self.url,
                                    json.dumps(body),
                                    content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {
            'data': {
                'type': 'question',
                'relationships': {
                    'choice_set': {
                        'links': {
                            'related': '/forest/Question/3/relationships/choice_set'
                        }
                    }
                },
                'attributes': {
                    'pub_date': '2021-06-21T09:46:39+00:00',
                    'question_text': 'What is your favorite color'
                },
                'id': 3,
                'links': {
                    'self': '/forest/Question/3'
                }
            },
            'links': {
                'self': '/forest/Question/3'
            }
        })
        self.assertEqual(Question.objects.count(), 3)

    def test_post_no_model(self):
        body = {
            'data': {
                'attributes': {
                    'question_text': 'What is your favorite color',
                    'pub_date': '2021-06-21T09:46:39.000Z'
                }
            }
        }
        response = self.client.post(self.bad_url,
                                    json.dumps(body),
                                    content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {'errors': [{'detail': 'no model found for resource Foo'}]})

    def test_post_error(self):
        url = reverse('resources:list', kwargs={'resource': 'Question'})
        data = {
            'data': {
                'attributes': {
                    'question_text': '''aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
                    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
                    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
                    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
                    a''',
                }
            }
        }
        self.assertEqual(Question.objects.count(), 2)
        response = self.client.post(url,
                                    json.dumps(data),
                                    content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {
            'errors': [
                {
                    'detail': 'value too long for type character varying(200)\n'
                }
            ]
        })
        self.assertEqual(Question.objects.count(), 2)

    def test_delete(self):
        data = {
            'data': {
                'attributes': {
                    'ids': ['1'],
                }
            }
        }
        self.assertEqual(Question.objects.count(), 2)
        response = self.client.delete(self.url,
                                      json.dumps(data),
                                      content_type='application/json')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Question.objects.count(), 1)

    def test_delete_no_model(self):
        data = {
            'data': {
                'attributes': {
                    'ids': ['1'],
                }
            }
        }
        self.assertEqual(Question.objects.count(), 2)
        response = self.client.delete(self.bad_url,
                                      json.dumps(data),
                                      content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {'errors': [{'detail': 'no model found for resource Foo'}]})