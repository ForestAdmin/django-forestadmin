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
                        'is_required': True
                    }, {
                        'field': 'Proof of address',
                        'description': '(Electricity, Gas, Water, Internet, Landline & Mobile Phone Invoice / Payment Schedule) no older than 3 months of the legal representative of your company',
                        'type': 'File',
                        'is_required': True
                    }, {
                        'field': 'Company bank statement',
                        'description': 'PDF including company name as well as IBAN',
                        'type': 'File',
                        'is_required': True
                    }, {
                        'field': 'Valid proof of ID',
                        'description': 'ID card or passport if the document has been issued in the EU, EFTA, or EEA / ID card or passport + resident permit or driving licence if the document has been issued outside the EU, EFTA, or EEA of the legal representative of your company',
                        'type': 'File',
                        'is_required': True
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
                        'type': 'String'
                    },
                    {
                        'field': 'zip code',
                        'type': 'String'
                    },
                ],
                'hooks': {
                    'load': self.invoice_load,
                    'change': {
                        'city': self.invoice_change_city,
                        'zip code': self.invoice_change_zip_code,
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
        questions = Question.objects.raw('''SELECT question.id, COUNT(choices.*)
            FROM tests_question
            JOIN tests_choices ON tests_choices.question_id = question.id
            GROUP BY question.id
            ORDER BY count DESC
            LIMIT 5;''')
        return {'id__in': [question.id for question in questions]}

    def invoice_load(self, fields, records, *args, **kwargs):
        pass

    def invoice_change_city(self, fields, record, *args, **kwargs):
        pass

    def invoice_change_zip_code(self, fields, record, *args, **kwargs):
        pass


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

    def test_register_smart_segment(self):
        Collection.register(QuestionForest, Question)
        collection = Schema.get_collection('Question')
        self.assertEqual(len(collection['segments']), 1)
        self.assertEqual(collection['segments'][0], {'name': 'Best questions'})

    def test_register_smart_action(self):
        Collection.register(QuestionForest, Question)
        collection = Schema.get_collection('Question')
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
                    'is_required': True,
                    'is_read_only': False,
                    'default_value': None,
                    'integration': None,
                    'reference': None,
                    'widget': None,
                    'position': 0
                },
                {
                    'field': 'Proof of address',
                    'description': '(Electricity, Gas, Water, Internet, Landline & Mobile Phone Invoice / Payment Schedule) no older than 3 months of the legal representative of your company',
                    'type': 'File',
                    'is_required': True,
                    'is_read_only': False,
                    'default_value': None,
                    'integration': None,
                    'reference': None,
                    'widget': None,
                    'position': 1
                },
                {
                    'field': 'Company bank statement',
                    'description': 'PDF including company name as well as IBAN',
                    'type': 'File',
                    'is_required': True,
                    'is_read_only': False,
                    'default_value': None,
                    'integration': None,
                    'reference': None,
                    'widget': None,
                    'position': 2
                },
                {
                    'field': 'Valid proof of ID',
                    'description': 'ID card or passport if the document has been issued in the EU, EFTA, or EEA / ID card or passport + resident permit or driving licence if the document has been issued outside the EU, EFTA, or EEA of the legal representative of your company',
                    'type': 'File',
                    'is_required': True,
                    'is_read_only': False,
                    'default_value': None,
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
                    'is_read_only': False,
                    'is_required': False,
                    'default_value': None,
                    'integration': None,
                    'reference': None,
                    'description': None,
                    'widget': None,
                    'position': 0
                },
                {
                    'field': 'city',
                    'type': 'String',
                    'is_read_only': False,
                    'is_required': False,
                    'default_value': None,
                    'integration': None,
                    'reference': None,
                    'description': None,
                    'widget': None,
                    'position': 1
                }, {
                    'field': 'zip code',
                    'type': 'String',
                    'is_read_only': False,
                    'is_required': False,
                    'default_value': None,
                    'integration': None,
                    'reference': None,
                    'description': None,
                    'widget': None,
                    'position': 2
                }],
            'hooks': {
                'load': True,
                'change': ['city', 'zip code']
            }
        })
