import copy
import sys
from datetime import datetime
from unittest import mock

import pytest
import pytz
from django.test import TransactionTestCase
from django.urls import reverse

from django_forest.tests.fixtures.schema import test_schema
from django_forest.utils.collection import Collection
from django_forest.utils.schema import Schema
from django_forest.utils.schema.json_api_schema import JsonApiSchema


# reset forest config dir auto import
from django_forest.utils.scope import ScopeManager


@pytest.fixture()
def reset_config_dir_import():
    for key in list(sys.modules.keys()):
        if key.startswith('django_forest.tests.forest'):
            del sys.modules[key]


@pytest.mark.usefixtures('reset_config_dir_import')
class ResourceListViewTests(TransactionTestCase):
    fixtures = ['article.json', 'publication.json',
                'session.json',
                'question.json', 'choice.json',
                'place.json', 'restaurant.json',
                'student.json',
                'serial.json']

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, django_assert_num_queries):
        self._django_assert_num_queries = django_assert_num_queries

    def setUp(self):
        Schema.schema = copy.deepcopy(test_schema)
        Schema.add_smart_features()
        Schema.handle_json_api_schema()
        self.url = reverse('django_forest:resources:list', kwargs={'resource': 'Question'})
        self.reverse_url = reverse('django_forest:resources:list', kwargs={'resource': 'Choice'})
        self.no_data_url = reverse('django_forest:resources:list', kwargs={'resource': 'Waiter'})
        self.enum_url = reverse('django_forest:resources:list', kwargs={'resource': 'Student'})
        self.uuid_url = reverse('django_forest:resources:list', kwargs={'resource': 'Serial'})
        self.one_to_one_url = reverse('django_forest:resources:list', kwargs={'resource': 'Restaurant'})
        self.bad_url = reverse('django_forest:resources:list', kwargs={'resource': 'Foo'})
        self.client = self.client_class(
            HTTP_AUTHORIZATION='Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjUiLCJlbWFpbCI6Imd1aWxsYXVtZWNAZm9yZXN0YWRtaW4uY29tIiwiZmlyc3RfbmFtZSI6Ikd1aWxsYXVtZSIsImxhc3RfbmFtZSI6IkNpc2NvIiwidGVhbSI6Ik9wZXJhdGlvbnMiLCJyZW5kZXJpbmdfaWQiOjEsImV4cCI6MTYyNTY3OTYyNi44ODYwMTh9.mHjA05yvMr99gFMuFv0SnPDCeOd2ZyMSN868V7lsjnw')
        ScopeManager.cache = {
            '1': {
                'scopes': {},
                'fetched_at': datetime(2021, 7, 8, 9, 20, 22, 582772, tzinfo=pytz.UTC)
            }
        }

    def tearDown(self):
        # reset _registry after each test
        JsonApiSchema._registry = {}
        ScopeManager.cache = {}
        Collection._registry = {}

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @mock.patch('django_forest.utils.scope.datetime')
    def test_get_search_to_edit(self, mocked_datetime, mocked_decode):
        mocked_datetime.now.return_value = datetime(2021, 7, 8, 9, 20, 23, 582772, tzinfo=pytz.UTC)
        response = self.client.get(self.reverse_url, {
            'context[relationship]': 'HasMany',
            'context[field]': 'choice_set',
            'context[collection]': 'Question',
            'context[recordId]': '1',
            'search': 'yes',
            'searchToEdit': 'true'
        })
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {
            'data': [
                {
                    'type': 'choice',
                    'id': 1,
                    'attributes': {
                        'choice_text': 'yes',
                        'votes': 0
                    },
                    'relationships': {
                        'question': {
                            'links': {
                                'related': '/forest/Choice/1/relationships/question'
                            },
                            'data': {
                                'type': 'question',
                                'id': '1'
                            }
                        },
                        'topic': {
                            'data': None,
                            'links': {
                                'related': '/forest/Choice/1/relationships/topic'
                                }
                            }
                    },
                    'links': {
                        'self': '/forest/Choice/1'
                    }
                },
            ],
            'included': [
                {
                    'type': 'question',
                    'attributes': {
                        'question_text': 'what is your favorite color?',
                        'pub_date': '2021-06-02T13:52:53.528000+00:00'
                    },
                    'id': 1, 'relationships': {
                    'choice_set': {
                        'links': {
                            'related': '/forest/Question/1/relationships/choice_set'
                        }
                    },
                    'topic': {'links': {'related': '/forest/Question/1/relationships/topic'}}
                },
                    'links': {
                        'self': '/forest/Question/1'
                    }
                }
            ],
            'meta': {
                'decorators': [
                    {
                        'id': 1,
                        'search': ['choice_text']
                    }
                ]
            }
        })

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @mock.patch('django_forest.utils.scope.datetime')
    def test_get_search_pk_no_id(self, mocked_datetime, mocked_decode):
        mocked_datetime.now.return_value = datetime(2021, 7, 8, 9, 20, 23, 582772, tzinfo=pytz.UTC)
        response = self.client.get(self.one_to_one_url, {
            'context[relationship]': 'BelongsTo',
            'context[field]': 'restaurant',
            'context[collection]': 'Place',
            'context[recordId]': '1',
            'fields[Restaurant]': 'id',
            'search': '1',
            'searchToEdit': 'true'
        })
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {
            'data': [
                {
                    'type': 'restaurant',
                    'id': 1,
                    'attributes': {
                        'serves_hot_dogs': True,
                        'serves_pizza': True
                    },
                    'relationships': {
                        'place': {
                            'links': {
                                'related': '/forest/Restaurant/1/relationships/place'
                            },
                            'data': {
                                'type': 'place',
                                'id': '1'
                            }
                        }
                    },
                    'links': {
                        'self': '/forest/Restaurant/1'
                    }
                }
            ],
            'included': [
                {
                    'type': 'place',
                    'relationships': {
                        'restaurant': {
                            'links': {
                                'related': '/forest/Place/1/relationships/restaurant'
                            }
                        }
                    },
                    'attributes': {
                        'address': 'Venezia, Italia',
                        'name': 'San Marco'},
                    'id': 1,
                    'links': {
                        'self': '/forest/Place/1'
                    }
                }
            ]
        })

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @mock.patch('django_forest.utils.scope.datetime')
    def test_get_search_number(self, mocked_datetime, mocked_decode):
        mocked_datetime.now.return_value = datetime(2021, 7, 8, 9, 20, 23, 582772, tzinfo=pytz.UTC)
        with self._django_assert_num_queries(1) as captured:
            response = self.client.get(self.url, {
                'fields[Question]': 'id,topic,question_text,pub_date',
                'fields[topic]': 'name',
                'page[number]': 1,
                'page[size]': 15,
                'search': 1,
                'searchExtended': 0
            })
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(captured.captured_queries[0]['sql'],
                         ' '.join('''SELECT "tests_question"."id", "tests_question"."question_text", "tests_question"."pub_date", "tests_question"."topic_id"
                                  FROM "tests_question"
                                   WHERE ("tests_question"."id" = 1
                                    OR "tests_question"."question_text"::text LIKE \'%1%\'
                                    OR "tests_question"."question_text" = '1'
                                    OR "tests_question"."question_text" = '1')
                                  LIMIT 15'''.replace('\n', ' ').split()))
        self.assertEqual(data, {
            'data': [
                {
                    'type': 'question',
                    'id': 1,
                    'attributes': {
                        'pub_date': '2021-06-02T13:52:53.528000+00:00',
                        'question_text': 'what is your favorite color?'
                    },
                    'links': {
                        'self': '/forest/Question/1'
                    },
                    'relationships': {
                        'topic': {
                            'data': None,
                            'links': {
                                'related': '/forest/Question/1/relationships/topic'
                            }
                        }
                    },
                }
            ]
        })

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @mock.patch('django_forest.utils.scope.datetime')
    def test_get_search_number_max_size(self, mocked_datetime, mocked_decode):
        mocked_datetime.now.return_value = datetime(2021, 7, 8, 9, 20, 23, 582772, tzinfo=pytz.UTC)
        with self._django_assert_num_queries(1) as captured:
            response = self.client.get(self.url, {
                'fields[Question]': 'id,question_text,pub_date',
                'page[number]': 1,
                'page[size]': 15,
                'search': sys.maxsize + 1,
                'searchExtended': 0
            })
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(captured.captured_queries[0]['sql'],
                         ' '.join('''SELECT "tests_question"."id", "tests_question"."question_text", "tests_question"."pub_date"
                          FROM "tests_question"
                           WHERE ("tests_question"."id"::text LIKE '%9223372036854775808%'
                            OR "tests_question"."question_text"::text LIKE '%9223372036854775808%'
                            OR "tests_question"."question_text" = '9223372036854775808'
                            OR "tests_question"."question_text" = '9223372036854775808')
                          LIMIT 15'''.replace('\n', ' ').split()))
        self.assertEqual(data, {
            'data': []
        })

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @mock.patch('django_forest.utils.scope.datetime')
    def test_get_search_mutliple(self, mocked_datetime, mocked_decode):
        mocked_datetime.now.return_value = datetime(2021, 7, 8, 9, 20, 23, 582772, tzinfo=pytz.UTC)
        with self._django_assert_num_queries(1) as captured:
            response = self.client.get(self.url, {
                'fields[Question]': 'id,topic,question_text,pub_date,foo,bar',
                'fields[topic]': 'name',
                'page[number]': 1,
                'page[size]': 15,
                'search': 'favorite',
                'searchExtended': 0
            })
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(captured.captured_queries[0]['sql'],
                         ' '.join('''
                         SELECT "tests_question"."id", "tests_question"."question_text", "tests_question"."pub_date", "tests_question"."topic_id"
                          FROM "tests_question"
                           WHERE ("tests_question"."question_text"::text LIKE '%favorite%'
                           OR "tests_question"."question_text" = 'favorite'
                           OR "tests_question"."question_text" = 'favorite')
                            LIMIT 15'''.replace('\n', ' ').split()))
        self.assertEqual(data, {
            'data': [
                {
                    'type': 'question',
                    'attributes': {
                        'pub_date': '2021-06-02T13:52:53.528000+00:00',
                        'question_text': 'what is your favorite color?',
                        'foo': 'what is your favorite color?+foo',
                        'bar': 'what is your favorite color?+bar',
                    },
                    'id': 1,
                    'links': {
                        'self': '/forest/Question/1'
                    },
                    'relationships': {
                        'topic': {
                            'data': None,
                            'links': {
                                'related': '/forest/Question/1/relationships/topic'
                            }
                        }
                    },
                },
                {
                    'type': 'question',
                    'attributes': {
                        'pub_date': '2021-06-03T13:52:53.528000+00:00',
                        'question_text': 'who is your favorite singer?',
                        'foo': 'who is your favorite singer?+foo',
                        'bar': 'who is your favorite singer?+bar',
                    },
                    'id': 3,
                    'links': {
                        'self': '/forest/Question/3'
                    },
                    'relationships': {
                        'topic': {
                            'data': None,
                            'links': {
                                'related': '/forest/Question/3/relationships/topic'
                            }
                        }
                    },
                }
            ],
            'meta': {
                'decorators': [
                    {
                        'id': 1,
                        'search': ['question_text', 'foo', 'bar']
                    },
                    {
                        'id': 3,
                        'search': ['question_text', 'foo', 'bar']
                    }
                ]
            }
        })

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @mock.patch('django_forest.utils.scope.datetime')
    def test_get_search_enum(self, mocked_datetime, mocked_decode):
        mocked_datetime.now.return_value = datetime(2021, 7, 8, 9, 20, 23, 582772, tzinfo=pytz.UTC)
        with self._django_assert_num_queries(1) as captured:
            response = self.client.get(self.enum_url, {
                'fields[Student]': 'id,year_in_school',
                'page[number]': 1,
                'page[size]': 15,
                'search': 'FR',
                'searchExtended': 0
            })
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(captured.captured_queries[0]['sql'],
                         ' '.join('''SELECT "tests_student"."id", "tests_student"."year_in_school"
                          FROM "tests_student"
                           WHERE "tests_student"."year_in_school" = 'FR'
                          LIMIT 15'''.replace('\n', ' ').split()))
        self.assertEqual(data, {
            'data': [
                {
                    'type': 'student',
                    'attributes': {
                        'year_in_school': 'FR'
                    },
                    'id': 1,
                    'links': {
                        'self': '/forest/Student/1'
                    }
                }
            ],
            'meta': {
                'decorators': [
                    {
                        'id': 1,
                        'search': ['year_in_school']
                    }
                ]
            }
        })

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @mock.patch('django_forest.utils.scope.datetime')
    def test_get_search_uuid(self, mocked_datetime, mocked_decode):
        mocked_datetime.now.return_value = datetime(2021, 7, 8, 9, 20, 23, 582772, tzinfo=pytz.UTC)
        with self._django_assert_num_queries(1) as captured:
            response = self.client.get(self.uuid_url, {
                'fields[Serial]': 'uuid',
                'page[number]': 1,
                'page[size]': 15,
                'search': '4759e256-a27a-45e1-b248-09fb1523c978',
                'searchExtended': 0
            })
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(captured.captured_queries[0]['sql'],
                         ' '.join('''SELECT "tests_serial"."uuid"
                          FROM "tests_serial"
                           WHERE "tests_serial"."uuid" = '4759e256-a27a-45e1-b248-09fb1523c978'::uuid
                          LIMIT 15'''.replace('\n', ' ').split()))
        self.assertEqual(data, {
            'data': [
                {
                    'type': 'serial',
                    'attributes': {
                        'uuid': '4759e256-a27a-45e1-b248-09fb1523c978'
                    },
                    'id': '4759e256-a27a-45e1-b248-09fb1523c978',
                    'links': {
                        'self': '/forest/Serial/4759e256-a27a-45e1-b248-09fb1523c978'
                    }
                }
            ],
            'meta': {
                'decorators': [
                    {
                        'id': '4759e256-a27a-45e1-b248-09fb1523c978',
                        'search': ['uuid']
                    }
                ]}
        })

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @mock.patch('django_forest.utils.scope.datetime')
    def test_get_extended_search(self, mocked_datetime, mocked_decode):
        mocked_datetime.now.return_value = datetime(2021, 7, 8, 9, 20, 23, 582772, tzinfo=pytz.UTC)
        with self._django_assert_num_queries(1) as captured:
            response = self.client.get(self.url, {
                'fields[Question]': 'id,topic,question_text,pub_date',
                'fields[topic]': 'name',
                'page[number]': 1,
                'page[size]': 15,
                'search': 'yes',
                'searchExtended': 1
            })
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(captured.captured_queries[0]['sql'],
                         ' '.join('''SELECT "tests_question"."id", "tests_question"."question_text", "tests_question"."pub_date", "tests_question"."topic_id"
                          FROM "tests_question"
                           LEFT OUTER JOIN "tests_choice" ON ("tests_question"."id" = "tests_choice"."question_id")
                           LEFT OUTER JOIN "tests_topic" ON ("tests_question"."topic_id" = "tests_topic"."id")
                            WHERE ("tests_question"."question_text"::text LIKE '%yes%' 
                            OR "tests_question"."question_text" = 'yes'
                            OR "tests_question"."question_text" = 'yes'
                            OR "tests_choice"."choice_text"::text LIKE '%yes%'
                            OR "tests_topic"."name"::text LIKE '%yes%')
                          LIMIT 15'''.replace('\n', ' ').split()))
        self.assertEqual(data, {
            'data': [
                {
                    'type': 'question',
                    'attributes': {
                        'question_text': 'what is your favorite color?',
                        'pub_date': '2021-06-02T13:52:53.528000+00:00'},
                    'id': 1,
                    'links': {
                        'self': '/forest/Question/1'
                    },
                    'relationships': {
                        'topic': {
                            'data': None,
                            'links': {
                                'related': '/forest/Question/1/relationships/topic'
                            }
                        }
                    },
                }
            ]
        })
