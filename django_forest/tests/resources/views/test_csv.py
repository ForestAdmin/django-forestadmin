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
class ResourceCsvViewTests(TransactionTestCase):
    fixtures = ['question.json', 'choice.json',]

    def setUp(self):
        Schema.schema = copy.deepcopy(test_schema)
        Schema.add_smart_features()
        Schema.handle_json_api_schema()
        self.url = reverse('resources:csv', kwargs={'resource': 'Question'})
        self.reverse_url = reverse('resources:csv', kwargs={'resource': 'Choice'})

    def tearDown(self):
        # reset _registry after each test
        JsonApiSchema._registry = {}

    def test_get(self):
        response = self.client.get(self.url, {
            'fields[Question]': 'id,question_text,pub_date,foo,bar',
            'search': '',
            'filters': '',
            'searchExtended': 0,
            'filename': 'questions',
            'header': 'id,question text,pub date,foo,bar',
            'timezone': 'Europe/Paris'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'id,question text,pub date,foo,bar\r\n1,what is your favorite color?,2021-06-02T13:52:53.528000+00:00,what is your favorite color?+foo,what is your favorite color?+bar\r\n2,do you like chocolate?,2021-06-02T15:52:53.528000+00:00,do you like chocolate?+foo,do you like chocolate?+bar\r\n3,who is your favorite singer?,2021-06-03T13:52:53.528000+00:00,who is your favorite singer?+foo,who is your favorite singer?+bar\r\n')

    def test_get_related_data(self):
        response = self.client.get(self.reverse_url, {
            'fields[Choice]': 'id,question,choice_text',
            'fields[question]': 'question_text',
            'search': '',
            'filters': '',
            'searchExtended': 0,
            'filename': 'choices',
            'header': 'id,choice text',
            'timezone': 'Europe/Paris'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'id,choice text,\r\n1,what is your favorite color?,yes\r\n2,what is your favorite color?,no\r\n')

    def test_wrong_operator(self):
        response = self.client.get(self.url, {
            'fields[Question]': 'id,question_text,pub_date,foo,bar',
            'search': '',
            'filters': '{"field":"question_text","operator":"foo","value":"what is your favorite color?"}',
            'searchExtended': 0,
            'filename': 'questions',
            'header': 'id,question text,pub date,foo,bar',
            'timezone': 'Europe/Paris'
        })
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {
            'errors': [
                {
                    'detail': 'Unknown provided operator foo'
                }
            ]
        })
