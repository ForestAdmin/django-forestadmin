import copy

from django.test import TransactionTestCase
from django.urls import reverse

from django_forest.tests.fixtures.schema import test_schema
from django_forest.utils.schema import Schema
from django_forest.utils.schema.json_api_schema import JsonApiSchema


class ResourceCountViewTests(TransactionTestCase):
    fixtures = ['article.json', 'publication.json', 'session.json', 'question.json', 'choice.json']

    def setUp(self):
        Schema.schema = copy.deepcopy(test_schema)
        Schema.handle_json_api_schema()

    def tearDown(self):
        # reset _registry after each test
        JsonApiSchema._registry = {}

    def test_get(self):
        url = reverse('django_forest:resources:count', kwargs={'resource': 'Question'})
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {'count': 3})

    def test_get_no_model(self):
        url = reverse('django_forest:resources:count', kwargs={'resource': 'Foo'})
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {'errors': [{'detail': 'no model found for resource Foo'}]})
