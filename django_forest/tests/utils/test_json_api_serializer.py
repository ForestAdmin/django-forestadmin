import copy

from django.test import TestCase
from django.utils.timezone import now

from django_forest.tests.fixtures.schema import test_schema

from django_forest.utils.collection import Collection
from django_forest.utils.json_api_serializer import JsonApiSchema
from django_forest.utils.schema import Schema


class UtilsJsonApiSerializerTests(TestCase):

    def setUp(self):
        Schema.schema = copy.deepcopy(test_schema)

    def tearDown(self):
        # reset _registry after each test
        Collection._registry = {}
        JsonApiSchema._registry = {}

    def test_handle_json_api_serializer(self):
        Schema.handle_json_api_serializer()
        self.assertEqual(len(JsonApiSchema._registry), 7)

    def test_json_api_serializer(self):
        Schema.handle_json_api_serializer()
        schema = JsonApiSchema._registry['QuestionSchema']
        n = now()
        data = schema().dump([{
            'id': 1,
            'question_text': 'what is your favorite color?',
            'pub_date': n,
        }], many=True)
        self.assertEqual(data, {
            'data': [
                {
                    'type': 'question',
                    'attributes': {
                        'question_text': 'what is your favorite color?',
                        'pub_date': n.isoformat(),
                        'id': 1.0
                    },
                    'relationships': {
                        'choice': {
                            'links': {
                                'related': '/forest/Question/1/relationships/Choice'
                            }
                        }
                    },
                    'id': 1.0
                }
            ]
        })

    def test_json_api_serializer_pk_is_not_id(self):
        Schema.handle_json_api_serializer()
        schema = JsonApiSchema._registry['SessionSchema']
        n = now()
        data = schema().dump([{
            'session_key': 'foobar1234',
            'session_data': 'foo',
            'expire_date': n,
        }], many=True)
        self.assertEqual(data, {
            'data': [
                {
                    'type': 'session',
                    'attributes': {
                        'expire_date': n.isoformat(),
                        'session_data': 'foo', 'session_key': 'foobar1234',
                        'id': 'foobar1234'
                    },
                    'id': 'foobar1234'
                }
            ]
        })
