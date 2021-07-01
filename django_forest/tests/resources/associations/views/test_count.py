import copy

from django.test import TransactionTestCase
from django.urls import reverse

from django_forest.tests.fixtures.schema import test_schema
from django_forest.utils.schema import Schema
from django_forest.utils.schema.json_api_schema import JsonApiSchema


class ResourceAssociationCountViewTests(TransactionTestCase):
    fixtures = ['article.json', 'publication.json', 'session.json', 'question.json', 'choice.json']

    def setUp(self):
        Schema.schema = copy.deepcopy(test_schema)
        Schema.handle_json_api_serializer()

    def tearDown(self):
        # reset _registry after each test
        JsonApiSchema._registry = {}

    def test_get(self):
        url = reverse('resources:associations:count', kwargs={'resource': 'Question', 'pk': 1, 'association_resource': 'choice_set'})
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {'count': 2})

    def test_get_no_model(self):
        url = reverse('resources:associations:count', kwargs={'resource': 'Foo', 'pk': 1, 'association_resource': 'choice_set'})
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {'errors': [{'detail': 'no model found for resource Foo'}]})

    def test_get_no_association(self):
        url = reverse('resources:associations:count', kwargs={'resource': 'Question', 'pk': 1, 'association_resource': 'foo'})
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {'errors': [{'detail': 'cannot find association resource foo for Model Question'}]})