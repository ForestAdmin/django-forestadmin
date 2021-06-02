import copy
from django.test import TestCase

from django_forest.tests.fixtures.schema import test_schema

from django_forest.utils.collection import Collection
from django_forest.tests.models import Question
from django_forest.utils.schema import Schema


class QuestionForest(Collection):
    def load(self):
        self.fields = [
            {
                'field': 'foo',
                'type': 'String'
            },
            {
                'field': 'question_text',  # override existing field
                'type': 'String',
            }
        ]


class CustomNameForest(Collection):
    name = 'custom'


class UtilsCollectionTests(TestCase):

    def setUp(self):
        Schema.schema = copy.deepcopy(test_schema)

    def tearDown(self):
        # reset _registry after each test
        Collection._registry = {}

    def test_register(self):
        Collection.register(QuestionForest, Question)
        self.assertEqual(len(Collection._registry), 1)
        self.assertIsInstance(Collection._registry['Question'], Collection)

    def test_register_smart_collection(self):
        Collection.register(QuestionForest)
        self.assertEqual(len(Collection._registry), 1)
        self.assertIsInstance(Collection._registry['QuestionForest'], Collection)
        collection = Schema.get_collection('QuestionForest')
        self.assertTrue(collection['is_virtual'])

    def test_register_smart_collection_custom_name(self):
        Collection.register(CustomNameForest)
        self.assertEqual(len(Collection._registry), 1)
        self.assertIsInstance(Collection._registry['custom'], Collection)

    def test_register_smart_field(self):
        Collection.register(QuestionForest, Question)
        collection = Schema.get_collection('Question')
        self.assertEqual(len(collection['fields']), 5)
        foo_smart_field = [f for f in collection['fields'] if f['field'] == 'foo'][0]
        self.assertTrue(foo_smart_field['is_virtual'])

    def test_register_smart_field_override(self):
        Collection.register(QuestionForest, Question)
        self.assertEqual(len(Collection._registry), 1)
        self.assertIsInstance(Collection._registry['Question'], Collection)
        collection = Schema.get_collection('Question')
        question_text_field = [f for f in collection['fields'] if f['field'] == 'question_text'][0]
        self.assertTrue(question_text_field['is_virtual'])
