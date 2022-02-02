import copy
from marshmallow_jsonapi import fields

from django.test import TestCase

from django_forest.tests.fixtures.schema import test_schema
from django_forest.tests.models import Article, Session, Question, Choice

from django_forest.utils.collection import Collection
from django_forest.utils.schema.json_api_schema import JsonApiSchema, DjangoSchema
from django_forest.utils.schema import Schema
from django_forest.utils.scope import ScopeManager


class UtilsJsonApiSchemaTests(TestCase):
    fixtures = ['article.json', 'publication.json', 'session.json', 'question.json', 'choice.json']

    def setUp(self):
        Schema.schema = copy.deepcopy(test_schema)

    def tearDown(self):
        # reset _registry after each test
        Collection._registry = {}
        JsonApiSchema._registry = {}
        ScopeManager.cache = {}

    def test_json_api_schema_bad_name(self):
        Schema.handle_json_api_schema()
        with self.assertRaises(Exception) as cm:
            JsonApiSchema.get('Foo')
        self.assertEqual(cm.exception.args[0], 'The FooSchema does not exist in the JsonApiSchema. Make sure you correctly set it.')

    def test_json_api_schema(self):
        Schema.handle_json_api_schema()
        schema = JsonApiSchema.get('tests_question')
        question = Question.objects.get(pk=1)
        data = schema().dump(question)
        self.assertEqual(data, {
            'data': {
                'type': 'tests_question',
                'id': 1,
                'relationships': {
                    'choice_set': {
                        'links': {
                            'related': '/forest/tests_question/1/relationships/choice_set'
                        }
                    },
                    'topic': {'links': {'related': '/forest/tests_question/1/relationships/topic'}}
                },
                'attributes': {
                    'pub_date': '2021-06-02T13:52:53.528000+00:00',
                    'question_text': 'what is your favorite color?'
                },
                'links': {
                    'self': '/forest/tests_question/1'
                }
            },
            'links': {
                'self': '/forest/tests_question/1'
            }
        })

    def test_json_api_schema_many(self):
        Schema.handle_json_api_schema()
        schema = JsonApiSchema.get('tests_question')
        queryset = Question.objects.all()
        data = schema().dump(queryset, many=True)
        self.assertEqual(data, {
            'data': [
                {
                    'type': 'tests_question',
                    'id': 1,
                    'relationships': {
                        'choice_set': {
                            'links': {
                                'related': '/forest/tests_question/1/relationships/choice_set'
                            }
                        },
                        'topic': {'links': {'related': '/forest/tests_question/1/relationships/topic'}}
                    },
                    'attributes': {
                        'pub_date': '2021-06-02T13:52:53.528000+00:00',
                        'question_text': 'what is your favorite color?'
                    },
                    'links': {
                        'self': '/forest/tests_question/1'
                    }
                },
                {
                    'type': 'tests_question',
                    'id': 2,
                    'relationships': {
                        'choice_set': {
                            'links': {
                                'related': '/forest/tests_question/2/relationships/choice_set'
                            }
                        },
                        'topic': {'links': {'related': '/forest/tests_question/2/relationships/topic'}}
                    },
                    'attributes': {
                        'pub_date': '2021-06-02T15:52:53.528000+00:00',
                        'question_text': 'do you like chocolate?'
                    },
                    'links': {
                        'self': '/forest/tests_question/2'
                    }
                },
                {
                    'type': 'tests_question',
                    'id': 3,
                    'relationships': {
                        'choice_set': {
                            'links': {
                                'related': '/forest/tests_question/3/relationships/choice_set'
                            }
                        },
                        'topic': {'links': {'related': '/forest/tests_question/3/relationships/topic'}}
                    },
                    'attributes': {
                        'pub_date': '2021-06-03T13:52:53.528000+00:00',
                        'question_text': 'who is your favorite singer?'
                    },
                    'links': {
                        'self': '/forest/tests_question/3'
                    }
                }
            ]
        })

    def test_json_api_schema_foreign_key(self):
        Schema.handle_json_api_schema()
        schema = JsonApiSchema.get('tests_choice')
        choice = Choice.objects.get(pk=1)
        data = schema(include_data=['question']).dump(choice)
        self.assertEqual(data, {
            'data': {
                'type': 'tests_choice',
                'attributes': {
                    'choice_text': 'yes',
                    'votes': 0
                },
                'id': 1,
                'relationships': {
                    'question': {
                        'links': {
                            'related': '/forest/tests_choice/1/relationships/question'
                        },
                        'data': {
                            'type': 'tests_question',
                            'id': '1'
                        }
                    }
                },
                'links': {
                    'self': '/forest/tests_choice/1'
                }
            },
            'links': {
                'self': '/forest/tests_choice/1'
            },
            'included': [
                {
                    'type': 'tests_question',
                    'id': 1,
                    'relationships': {
                        'choice_set': {
                            'links': {
                                'related': '/forest/tests_question/1/relationships/choice_set'
                            }
                        },
                        'topic': {'links': {'related': '/forest/tests_question/1/relationships/topic'}}
                    },
                    'attributes': {
                        'pub_date': '2021-06-02T13:52:53.528000+00:00',
                        'question_text': 'what is your favorite color?'
                    },
                    'links': {
                        'self': '/forest/tests_question/1'
                    }
                }
            ]
        })

    def test_json_api_schema_pk_is_not_id(self):
        Schema.handle_json_api_schema()
        schema = JsonApiSchema.get('tests_session')
        session = Session.objects.get(pk='foobar1234')
        data = schema().dump(session)
        self.assertEqual(data, {
            'data': {
                'type': 'tests_session',
                'attributes': {
                    'session_key': 'foobar1234',
                    'expire_date': '2021-06-02T13:48:36.039000+00:00',
                    'session_data': 'foo',
                },
                'id': 'foobar1234',
                'links': {
                    'self': '/forest/tests_session/foobar1234'
                },
            },
            'links': {
                'self': '/forest/tests_session/foobar1234'
            },
        })

    def test_json_api_schema_many_to_many(self):
        Schema.handle_json_api_schema()
        schema = JsonApiSchema.get('tests_article')
        article = Article.objects.get(pk=1)
        data = schema(include_data=['publications']).dump(article)
        self.assertEqual(data, {
            'data': {
                'type': 'tests_article',
                'relationships': {
                    'publications': {
                        'links': {
                            'related': '/forest/tests_article/1/relationships/publications'
                        },
                        'data': [
                            {
                                'type': 'tests_publication',
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
                    'self': '/forest/tests_article/1'
                }
            },
            'links': {
                'self': '/forest/tests_article/1'
            },
            'included': [
                {
                    'type': 'tests_publication',
                    'relationships': {
                        'article_set': {
                            'links': {
                                'related': '/forest/tests_publication/1/relationships/article_set'
                            }
                        }
                    },
                    'id': 1,
                    'attributes': {
                        'title': 'The Python Journal'
                    },
                    'links': {
                        'self': '/forest/tests_publication/1'
                    }
                }
            ]
        })

    # These are dumb tests for having 100% covering
    # This is just some redefinition of Marshmallow Json Api for handling django
    def test_django_schema(self):
        with self.assertRaises(Exception) as cm:
            DjangoSchema()
        self.assertEqual(cm.exception.args[0], 'Must specify type_ class Meta option')

    def test_django_schema_no_url(self):
        with self.assertRaises(Exception) as cm:
            class FooSchema(DjangoSchema):
                class Meta:
                    type_ = 'foo'
                    self_url_kwargs = {'foo_id': f'<id>'}
            FooSchema()

        self.assertEqual(cm.exception.args[0], 'Must specify `self_url` Meta option when `self_url_kwargs` is specified')

    def test_django_schema_format_item_none(self):
        class FooSchema(DjangoSchema):
            class Meta:
                type_ = 'foo'

        schema = FooSchema()
        self.assertEqual(schema.format_item(None), None)
