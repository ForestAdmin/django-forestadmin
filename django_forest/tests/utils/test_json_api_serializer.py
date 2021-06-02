import copy

from django.test import TestCase

from django_forest.tests.fixtures.schema import test_schema
from django_forest.tests.models import Article, Session, Question

from django_forest.utils.collection import Collection
from django_forest.utils.json_api_serializer import JsonApiSchema
from django_forest.utils.schema import Schema


class UtilsJsonApiSerializerTests(TestCase):
    fixtures = ['article.json', 'publication.json', 'session.json', 'question.json']

    def setUp(self):
        Schema.schema = copy.deepcopy(test_schema)

    def tearDown(self):
        # reset _registry after each test
        Collection._registry = {}
        JsonApiSchema._registry = {}

    def test_handle_json_api_serializer(self):
        Schema.handle_json_api_serializer()
        self.assertEqual(len(JsonApiSchema._registry), 9)

    def test_json_api_serializer(self):
        Schema.handle_json_api_serializer()
        schema = JsonApiSchema._registry['QuestionSchema']
        question = Question.objects.get(pk=1)
        data = schema().dump([question], many=True)
        self.assertEqual(data, {
            'data': [
                {
                    'type': 'question',
                    'relationships': {
                        'choice': {
                            'links': {
                                'related': '/forest/Question/1/relationships/Choice'
                            }
                        }
                    },
                    'attributes': {
                        'question_text': 'what is your favorite color?',
                        'pub_date': '2021-06-02T13:52:53.528000+00:00',
                        'id': 1.0
                    },
                    'id': 1.0
                }
            ]
        })

    def test_json_api_serializer_pk_is_not_id(self):
        Schema.handle_json_api_serializer()
        schema = JsonApiSchema._registry['SessionSchema']
        session = Session.objects.get(pk='foobar1234')
        data = schema().dump([session], many=True)
        self.assertEqual(data, {
            'data': [
                {
                    'type': 'session',
                    'attributes': {
                        'session_key': 'foobar1234',
                        'expire_date': '2021-06-02T13:48:36.039000+00:00',
                        'session_data': 'foo',
                        'id': 'foobar1234'
                    },
                    'id': 'foobar1234'
                }
            ]
        })

    def test_json_api_serializer_many_to_many(self):
        Schema.handle_json_api_serializer()
        schema = JsonApiSchema._registry['ArticleSchema']
        article = Article.objects.get(pk=1)
        data = schema(include_data=['publications']).dump([article], many=True)
        self.assertEqual(data, {
            'data': [
                {
                    'type': 'article', 'id': 1.0,
                    'attributes': {
                        'headline': 'Django lets you build Web apps easily',
                        'id': 1.0
                    },
                    'relationships': {
                        'publications': {
                            'links': {
                                'related': '/forest/Article/1/relationships/Publication'
                            },
                            'data': [
                                {
                                    'type': 'publication',
                                    'id': '1'
                                }
                            ]
                        }
                    }
                }
            ],
            'included': [
                {
                    'type': 'publication',
                    'attributes': {
                        'title': 'The Python Journal',
                        'id': 1.0
                    },
                    'id': 1.0,
                    'relationships': {
                        'article': {
                            'links': {
                                'related': '/forest/Publication/1/relationships/Article'
                            }
                        }
                    }
                }
            ]
        })
