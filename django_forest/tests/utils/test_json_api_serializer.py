import copy

from django.test import TestCase

from django_forest.tests.fixtures.schema import test_schema
from django_forest.tests.models import Article, Session, Question, Choice

from django_forest.utils.collection import Collection
from django_forest.utils.schema.json_api_schema import JsonApiSchema
from django_forest.utils.schema import Schema


class UtilsJsonApiSerializerTests(TestCase):
    fixtures = ['article.json', 'publication.json', 'session.json', 'question.json', 'choice.json']

    def setUp(self):
        Schema.schema = copy.deepcopy(test_schema)

    def tearDown(self):
        # reset _registry after each test
        Collection._registry = {}
        JsonApiSchema._registry = {}

    def test_handle_json_api_serializer(self):
        Schema.handle_json_api_serializer()
        self.assertEqual(len(JsonApiSchema._registry), 17)

    def test_json_api_serializer(self):
        Schema.handle_json_api_serializer()
        schema = JsonApiSchema._registry['QuestionSchema']
        question = Question.objects.get(pk=1)
        data = schema().dump(question)
        self.assertEqual(data, {
            'data': {
                'type': 'question',
                'id': 1,
                'relationships': {
                    'choice_set': {
                        'links': {
                            'related': '/forest/Question/1/relationships/choice_set'
                        }
                    }
                },
                'attributes': {
                    'pub_date': '2021-06-02T13:52:53.528000+00:00',
                    'question_text': 'what is your favorite color?'
                },
                'links': {
                    'self': '/forest/Question/1'
                }
            },
            'links': {
                'self': '/forest/Question/1'
            }
        })

    def test_json_api_serializer_many(self):
        Schema.handle_json_api_serializer()
        schema = JsonApiSchema._registry['QuestionSchema']
        queryset = Question.objects.all()
        data = schema().dump(queryset, many=True)
        self.assertEqual(data, {
            'data': [
                {
                    'type': 'question',
                    'id': 1,
                    'relationships': {
                        'choice_set': {
                            'links': {
                                'related': '/forest/Question/1/relationships/choice_set'
                            }
                        }
                    },
                    'attributes': {
                        'pub_date': '2021-06-02T13:52:53.528000+00:00',
                        'question_text': 'what is your favorite color?'
                    },
                    'links': {
                        'self': '/forest/Question/1'
                    }
                },
                {
                    'type': 'question',
                    'id': 2,
                    'relationships': {
                        'choice_set': {
                            'links': {
                                'related': '/forest/Question/2/relationships/choice_set'
                            }
                        }
                    },
                    'attributes': {
                        'pub_date': '2021-06-02T15:52:53.528000+00:00',
                        'question_text': 'do you like chocolate?'
                    },
                    'links': {
                        'self': '/forest/Question/2'
                    }
                }
            ]
        })

    def test_json_api_serializer_foreign_key(self):
        Schema.handle_json_api_serializer()
        schema = JsonApiSchema._registry['ChoiceSchema']
        choice = Choice.objects.get(pk=1)
        data = schema(include_data=['question']).dump(choice)
        self.assertEqual(data, {
            'data': {
                'type': 'choice',
                'attributes': {
                    'choice_text': 'yes',
                    'votes': 0
                },
                'id': 1,
                'relationships': {
                    'question': {
                        'links': {
                            'related': '/forest/Choice/1/relationships/question'
                        },
                        'data': {
                            'type': 'question',
                            'id': '1'
                        }
                    }
                },
                'links': {
                    'self': '/forest/Choice/1'
                }
            },
            'links': {
                'self': '/forest/Choice/1'
            },
            'included': [
                {
                    'type': 'question',
                    'id': 1,
                    'relationships': {
                        'choice_set': {
                            'links': {
                                'related': '/forest/Question/1/relationships/choice_set'
                            }
                        }
                    },
                    'attributes': {
                        'pub_date': '2021-06-02T13:52:53.528000+00:00',
                        'question_text': 'what is your favorite color?'
                    },
                    'links': {
                        'self': '/forest/Question/1'
                    }
                }
            ]
        })

    def test_json_api_serializer_pk_is_not_id(self):
        Schema.handle_json_api_serializer()
        schema = JsonApiSchema._registry['SessionSchema']
        session = Session.objects.get(pk='foobar1234')
        data = schema().dump(session)
        self.assertEqual(data, {
            'data': {
                'type': 'session',
                'attributes': {
                    'session_key': 'foobar1234',
                    'expire_date': '2021-06-02T13:48:36.039000+00:00',
                    'session_data': 'foo',
                },
                'id': 'foobar1234',
                'links': {
                    'self': '/forest/Session/foobar1234'
                },
            },
            'links': {
                'self': '/forest/Session/foobar1234'
            },
        })

    def test_json_api_serializer_many_to_many(self):
        Schema.handle_json_api_serializer()
        schema = JsonApiSchema._registry['ArticleSchema']
        article = Article.objects.get(pk=1)
        data = schema(include_data=['publications']).dump(article)
        self.assertEqual(data, {
            'data': {
                'type': 'article',
                'relationships': {
                    'publications': {
                        'links': {
                            'related': '/forest/Article/1/relationships/publications'
                        },
                        'data': [
                            {
                                'type': 'publication',
                                'id': '1'
                            }
                        ]
                    }
                },
                'id': 1,
                'attributes': {
                    'headline': 'Django lets you build Web apps easily'
                },
                'links': {
                    'self': '/forest/Article/1'
                }
            },
            'links': {
                'self': '/forest/Article/1'
            },
            'included': [
                {
                    'type': 'publication',
                    'relationships': {
                        'article_set': {
                            'links': {
                                'related': '/forest/Publication/1/relationships/article_set'
                            }
                        }
                    },
                    'id': 1,
                    'attributes': {
                        'title': 'The Python Journal'
                    },
                    'links': {
                        'self': '/forest/Publication/1'
                    }
                }
            ]
        })
