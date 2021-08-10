import copy
from django.test import TestCase

from django_forest.tests.fixtures.schema import test_schema

from django_forest.utils.collection import Collection
from django_forest.tests.models import Question
from django_forest.utils.schema import Schema
from django_forest.utils.scope import ScopeManager


class QuestionForest(Collection):
    def load(self):
        self.fields = [
            {
                'field': 'foo',
                'type': 'String',
                'get': self.get_foo,
                'set': self.set_foo,
            },
            {
                'field': 'question_text',  # override existing field
                'type': 'String',
            }
        ]
        self.segments = [
            {
                'name': 'Best questions',
                'where': self.best_questions
            }
        ]

        self.actions = [
            {
                'name': 'Mark as Live',
            },
            {
                'name': 'Upload Legal Docs',
                'endpoint': '/foo/upload_legal_docs',
                'http_method': 'GET',
                'download': True,
                'type': 'single',
                'fields': [
                    {
                        'field': 'Certificate of Incorporation',
                        'description': 'The legal document relating to the formation of a company or corporation.',
                        'type': 'File',
                        'isRequired': True
                    }, {
                        'field': 'Proof of address',
                        'description': '(Electricity, Gas, Water, Internet, Landline & Mobile Phone Invoice / Payment Schedule) no older than 3 months of the legal representative of your company',
                        'type': 'File',
                        'isRequired': True
                    }, {
                        'field': 'Company bank statement',
                        'description': 'PDF including company name as well as IBAN',
                        'type': 'File',
                        'isRequired': True
                    }, {
                        'field': 'Valid proof of ID',
                        'description': 'ID card or passport if the document has been issued in the EU, EFTA, or EEA / ID card or passport + resident permit or driving licence if the document has been issued outside the EU, EFTA, or EEA of the legal representative of your company',
                        'type': 'File',
                        'isRequired': True
                    }
                ]
            },
            {
                'name': 'Send invoice',
                'type': 'single',
                'fields': [
                    {
                        'field': 'country',
                        'type': 'Enum',
                        'enums': ['FR', 'US']
                    },
                    {
                        'field': 'city',
                        'type': 'String',
                        'hook': 'cityChange'
                    },
                    {
                        'field': 'zip code',
                        'type': 'String',
                        'hook': 'zipCodeChange'
                    },
                ],
                'hooks': {
                    'load': self.invoice_load,
                    'change': {
                        'cityChange': self.invoice_change_city,
                        'zipCodeChange': self.invoice_change_zip_code,
                    },
                },
            }
        ]

    def get_foo(self, obj):
        return obj.question_text + 'foo'

    def set_foo(self, obj, value):
        obj.question_text = f'{value}-foo'
        return obj

    def best_questions(self, obj):
        questions = Question.objects.raw('''SELECT tests_question.id, COUNT(tests_choices.*)
            FROM tests_question
            JOIN tests_choices ON tests_choices.question_id = question.id
            GROUP BY question.id
            ORDER BY count DESC
            LIMIT 5;''')
        return {'id__in': [question.id for question in questions]}

    def invoice_load(self, fields, request, *args, **kwargs):
        country = next((x for x in fields if x['field'] == 'country'), None)
        country['value'] = 'FR'
        return fields

    def invoice_change_city(self, fields, request, changed_field, *args, **kwargs):
        zip_code = next((x for x in fields if x['field'] == 'zip code'), None)
        zip_code['value'] = '83'
        return fields

    def invoice_change_zip_code(self, fields, request, changed_field, *args, **kwargs):
        return fields


class CustomNameForest(Collection):
    name = 'custom'


class UtilsCollectionTests(TestCase):

    def setUp(self):
        Schema.schema = copy.deepcopy(test_schema)
        Collection._registry = {}

    def tearDown(self):
        # reset _registry after each test
        Collection._registry = {}
        ScopeManager.cache = {}

    def test_register(self):
        Collection.register(QuestionForest, Question)
        self.assertEqual(len(Collection._registry), 1)
        self.assertIsInstance(Collection._registry['tests_question'], Collection)

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
        collection = Schema.get_collection('tests_question')
        self.assertEqual(len(collection['fields']), 6)
        foo_smart_field = [f for f in collection['fields'] if f['field'] == 'foo'][0]
        self.assertTrue(foo_smart_field['is_virtual'])

    def test_register_smart_field_override(self):
        Collection.register(QuestionForest, Question)
        self.assertEqual(len(Collection._registry), 1)
        self.assertIsInstance(Collection._registry['tests_question'], Collection)
        collection = Schema.get_collection('tests_question')
        question_text_field = [f for f in collection['fields'] if f['field'] == 'question_text'][0]
        self.assertTrue(question_text_field['is_virtual'])

    def test_register_smart_segment(self):
        Collection.register(QuestionForest, Question)
        collection = Schema.get_collection('tests_question')
        self.assertEqual(len(collection['segments']), 1)
        self.assertEqual(collection['segments'][0], {'name': 'Best questions'})

    def test_register_smart_action(self):
        Collection.register(QuestionForest, Question)
        collection = Schema.get_collection('tests_question')
        self.assertEqual(len(collection['actions']), 3)
        self.assertEqual(collection['actions'][0], {
            'name': 'Mark as Live',
            'type': 'bulk',
            'baseUrl': None,
            'endpoint': '/forest/actions/mark-as-live',
            'http_method': 'POST',
            'redirect': None,
            'download': False,
            'fields': [],
            'hooks': {
                'load': False,
                'change': []
            }
        })
        self.assertEqual(collection['actions'][1], {
            'name': 'Upload Legal Docs',
            'type': 'single',
            'baseUrl': None,
            'endpoint': '/foo/upload_legal_docs',
            'http_method': 'GET',
            'redirect': None,
            'download': True,
            'fields': [
                {
                    'field': 'Certificate of Incorporation',
                    'description': 'The legal document relating to the formation of a company or corporation.',
                    'type': 'File',
                    'isRequired': True,
                    'isReadOnly': False,
                    'defaultValue': None,
                    'integration': None,
                    'reference': None,
                    'widget': None,
                    'position': 0
                },
                {
                    'field': 'Proof of address',
                    'description': '(Electricity, Gas, Water, Internet, Landline & Mobile Phone Invoice / Payment Schedule) no older than 3 months of the legal representative of your company',
                    'type': 'File',
                    'isRequired': True,
                    'isReadOnly': False,
                    'defaultValue': None,
                    'integration': None,
                    'reference': None,
                    'widget': None,
                    'position': 1
                },
                {
                    'field': 'Company bank statement',
                    'description': 'PDF including company name as well as IBAN',
                    'type': 'File',
                    'isRequired': True,
                    'isReadOnly': False,
                    'defaultValue': None,
                    'integration': None,
                    'reference': None,
                    'widget': None,
                    'position': 2
                },
                {
                    'field': 'Valid proof of ID',
                    'description': 'ID card or passport if the document has been issued in the EU, EFTA, or EEA / ID card or passport + resident permit or driving licence if the document has been issued outside the EU, EFTA, or EEA of the legal representative of your company',
                    'type': 'File',
                    'isRequired': True,
                    'isReadOnly': False,
                    'defaultValue': None,
                    'integration': None,
                    'reference': None,
                    'widget': None,
                    'position': 3
                }],
            'hooks': {
                'load': False,
                'change': []
            }
        })
        self.assertEqual(collection['actions'][2], {
            'name': 'Send invoice',
            'type': 'single',
            'baseUrl': None,
            'endpoint': '/forest/actions/send-invoice',
            'http_method': 'POST',
            'redirect': None,
            'download': False,
            'fields': [
                {
                    'field': 'country',
                    'type': 'Enum',
                    'enums': ['FR', 'US'],
                    'isReadOnly': False,
                    'isRequired': False,
                    'defaultValue': None,
                    'integration': None,
                    'reference': None,
                    'description': None,
                    'widget': None,
                    'position': 0
                },
                {
                    'field': 'city',
                    'type': 'String',
                    'isReadOnly': False,
                    'isRequired': False,
                    'defaultValue': None,
                    'integration': None,
                    'reference': None,
                    'description': None,
                    'widget': None,
                    'position': 1,
                    'hook': 'cityChange'
                }, {
                    'field': 'zip code',
                    'type': 'String',
                    'isReadOnly': False,
                    'isRequired': False,
                    'defaultValue': None,
                    'integration': None,
                    'reference': None,
                    'description': None,
                    'widget': None,
                    'position': 2,
                    'hook': 'zipCodeChange'
                }],
            'hooks': {
                'load': True,
                'change': ['cityChange', 'zipCodeChange']
            }
        })
