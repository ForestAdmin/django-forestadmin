import copy
import sys

import pytest
from django.test import TransactionTestCase
from django.urls import reverse

from django_forest.tests.fixtures.schema import test_schema
from django_forest.utils.schema import Schema
from django_forest.utils.schema.json_api_schema import JsonApiSchema


# reset forest config dir auto import
@pytest.fixture()
def reset_config_dir_import():
    for key in list(sys.modules.keys()):
        if key.startswith('django_forest.tests.forest'):
            del sys.modules[key]


@pytest.mark.usefixtures('reset_config_dir_import')
class ResourceAssociationCsvViewTests(TransactionTestCase):
    fixtures = ['question.json', 'choice.json']

    def setUp(self):
        Schema.schema = copy.deepcopy(test_schema)
        Schema.add_smart_features()
        Schema.handle_json_api_schema()
        self.url = reverse('django_forest:resources:associations:csv',
                           kwargs={'resource': 'Question', 'pk': 1, 'association_resource': 'choice_set'})
        self.reverse_url = reverse('django_forest:resources:associations:csv',
                                   kwargs={'resource': 'Choice', 'pk': 1, 'association_resource': 'question'})
        self.bad_association_url = reverse('django_forest:resources:associations:csv',
                                           kwargs={'resource': 'Question', 'pk': 1, 'association_resource': 'foo'})

    def tearDown(self):
        # reset _registry after each test
        JsonApiSchema._registry = {}

    def test_get(self):
        response = self.client.get(self.url, {
            'fields[Choice]': 'id,question,choice_text',
            'fields[question]': 'question_text',
            'search': '',
            'searchExtended': '',
            'filename': 'choices',
            'header': 'id,question,choice text',
            'timezone': 'Europe/Paris'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'id,question,choice text\r\n1,what is your favorite color?,yes\r\n2,what is your favorite color?,no\r\n')

    def test_get_no_association(self):
        response = self.client.get(self.bad_association_url, {
            'fields[Choice]': 'id,question,choice_text',
            'fields[question]': 'question_text',
            'search': '',
            'searchExtended': '',
            'filename': 'choices',
            'header': 'id,question,choice text',
            'timezone': 'Europe/Paris'
        })
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {'errors': [{'detail': 'cannot find association resource foo for Model Question'}]})
