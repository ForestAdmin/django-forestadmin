import copy

from django.test import TestCase
from django.urls import reverse

from django_forest.tests.fixtures.schema import test_schema
from django_forest.utils.schema import Schema
from django_forest.utils.schema.json_api_schema import JsonApiSchema


class IndexViewTests(TestCase):
    fixtures = ['article.json', 'publication.json', 'session.json', 'question.json', 'choice.json']

    def setUp(self):
        Schema.schema = copy.deepcopy(test_schema)
        Schema.handle_json_api_serializer()

    def tearDown(self):
        # reset _registry after each test
        JsonApiSchema._registry = {}

    def test_get(self):
        response = self.client.get(reverse('resources:list', kwargs={'resource': 'Question'}))
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
