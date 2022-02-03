import copy
import json
from unittest import mock

import pytest
from django.test import TransactionTestCase
from django.urls import reverse

from django_forest.tests.fixtures.schema import test_schema
from django_forest.tests.models import Question, Restaurant
from django_forest.tests.resources.views.list.test_list_scope import mocked_scope
from django_forest.utils.schema import Schema
from django_forest.utils.schema.json_api_schema import JsonApiSchema
from django_forest.utils.scope import ScopeManager


@mock.patch('django_forest.utils.scope.ScopeManager._has_cache_expired', return_value=False)
@mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})    
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

    def setUp(self, *args, **kwargs):
        Schema.schema = copy.deepcopy(test_schema)
        Schema.handle_json_api_schema()
        self.url = f"{reverse('django_forest:resources:list', kwargs={'resource': 'tests_question'})}?timezone=Europe%2FParis"
        self.reverse_url = reverse('django_forest:resources:list', kwargs={'resource': 'tests_choice'})
        self.no_data_url = reverse('django_forest:resources:list', kwargs={'resource': 'tests_waiter'})
        self.enum_url = reverse('django_forest:resources:list', kwargs={'resource': 'tests_student'})
        self.uuid_url = reverse('django_forest:resources:list', kwargs={'resource': 'tests_serial'})
        self.one_to_one_url = reverse('django_forest:resources:list', kwargs={'resource': 'tests_restaurant'})
        self.bad_url = reverse('django_forest:resources:list', kwargs={'resource': 'tests_foo'})
        self.client = self.client_class(
            HTTP_AUTHORIZATION='Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjUiLCJlbWFpbCI6Imd1aWxsYXVtZWNAZm9yZXN0YWRtaW4uY29tIiwiZmlyc3RfbmFtZSI6Ikd1aWxsYXVtZSIsImxhc3RfbmFtZSI6IkNpc2NvIiwidGVhbSI6Ik9wZXJhdGlvbnMiLCJyZW5kZXJpbmdfaWQiOjEsImV4cCI6MTYyNTY3OTYyNi44ODYwMTh9.mHjA05yvMr99gFMuFv0SnPDCeOd2ZyMSN868V7lsjnw')
        ScopeManager.cache = {
            '1': {
                'scopes': {},
                'fetched_at': 'useless-here'
            }
        }

    def tearDown(self, *args, **kwargs):
        # reset _registry after each test
        JsonApiSchema._registry = {}
        ScopeManager.cache = {}

    def test_get(self, *args, **kwargs):
        response = self.client.get(self.url, {'page[number]': '1', 'page[size]': '15'})
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {
            'data': [
                {
                    'type': 'tests_question',
                    'relationships': {
                        'choice_set': {
                            'links': {
                                'related': '/forest/tests_question/1/relationships/choice_set'
                            }
                        },
                        'topic': {'data': None, 'links': {'related': '/forest/tests_question/1/relationships/topic'}}
                    },
                    'attributes': {
                        'question_text': 'what is your favorite color?',
                        'pub_date': '2021-06-02T13:52:53.528000+00:00'},
                    'id': 1,
                    'links': {
                        'self': '/forest/tests_question/1'
                    }
                }, {
                    'type': 'tests_question',
                    'relationships': {
                        'choice_set': {
                            'links': {
                                'related': '/forest/tests_question/2/relationships/choice_set'
                            }
                        },
                        'topic': {'data': None, 'links': {'related': '/forest/tests_question/2/relationships/topic'}}
                    },
                    'attributes': {
                        'question_text': 'do you like chocolate?',
                        'pub_date': '2021-06-02T15:52:53.528000+00:00'
                    },
                    'id': 2, 'links': {
                        'self': '/forest/tests_question/2'
                    }
                },
                {
                    'type': 'tests_question',
                    'relationships': {
                        'choice_set': {
                            'links': {
                                'related': '/forest/tests_question/3/relationships/choice_set'
                            }
                        },
                        'topic': {'data': None, 'links': {'related': '/forest/tests_question/3/relationships/topic'}}
                    },
                    'attributes': {
                        'pub_date': '2021-06-03T13:52:53.528000+00:00',
                        'question_text': 'who is your favorite singer?'
                    },
                    'id': 3,
                    'links': {
                        'self': '/forest/tests_question/3'
                    }
                }
            ]
        })

    
    def test_get_no_data(self, *args, **kwargs):
        response = self.client.get(self.no_data_url)
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {'data': []})

    def test_get_no_model(self, *args, **kwargs):
        response = self.client.get(self.bad_url, {'page[number]': '1', 'page[size]': '15'})
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {'errors': [{'detail': 'no model found for resource tests_foo'}]})

    def test_post(self, *args, **kwargs):
        body = {
            'data': {
                'attributes': {
                    'question_text': 'What is your favorite color',
                    'pub_date': '2021-06-21T09:46:39.000Z'
                }
            }
        }
        self.assertEqual(Question.objects.count(), 3)
        response = self.client.post(self.url,
                                    json.dumps(body),
                                    content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {
            'data': {
                'type': 'tests_question',
                'relationships': {
                    'choice_set': {
                        'links': {
                            'related': '/forest/tests_question/4/relationships/choice_set'
                        }
                    },
                    'topic': {'links': {'related': '/forest/tests_question/4/relationships/topic'}}
                },
                'attributes': {
                    'pub_date': '2021-06-21T09:46:39+00:00',
                    'question_text': 'What is your favorite color'
                },
                'id': 4,
                'links': {
                    'self': '/forest/tests_question/4'
                }
            },
            'links': {
                'self': '/forest/tests_question/4'
            }
        })
        self.assertEqual(Question.objects.count(), 4)

    def test_post_no_model(self, *args, **kwargs):
        body = {
            'data': {
                'attributes': {
                    'question_text': 'What is your favorite color',
                    'pub_date': '2021-06-21T09:46:39.000Z'
                }
            }
        }
        response = self.client.post(self.bad_url,
                                    json.dumps(body),
                                    content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {'errors': [{'detail': 'no model found for resource tests_foo'}]})

    def test_post_related_data(self, *args, **kwargs):
        body = {
            'data': {
                'attributes': {
                    'serves_hot_dogs': False,
                    'serves_pizzas': False
                },
                'relationships': {
                    'place': {
                        'data': {
                            'type': 'tests_places',
                            'id': 2,
                        }
                    },
                }
            }
        }
        self.assertEqual(Restaurant.objects.count(), 1)
        response = self.client.post(self.one_to_one_url,
                                    json.dumps(body),
                                    content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {
            'data': {
                'type': 'tests_restaurant',
                'relationships': {
                    'waiter_set': {
                        'links': {
                            'related': '/forest/tests_restaurant/2/relationships/waiter_set'
                        }
                    },
                    'place': {
                        'links': {
                            'related': '/forest/tests_restaurant/2/relationships/place'
                        }
                    }
                },
                'attributes': {
                    'serves_hot_dogs': False,
                    'serves_pizza': False
                },
                'id': 2,
                'links': {
                    'self': '/forest/tests_restaurant/2'
                }
            },
            'links': {
                'self': '/forest/tests_restaurant/2'
            }
        })
        self.assertEqual(Restaurant.objects.count(), 2)

    def test_post_related_data_do_not_exist(self, *args, **kwargs):
        body = {
            'data': {
                'attributes': {
                    'serves_hot_dogs': False,
                    'serves_pizzas': False
                },
                'relationships': {
                    'place': {
                        'data': {
                            'type': 'tests_places',
                            'id': 3,
                        }
                    },
                }
            }
        }
        self.assertEqual(Restaurant.objects.count(), 1)
        response = self.client.post(self.one_to_one_url,
                                    json.dumps(body),
                                    content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {
            'errors': [
                {
                    'detail': 'Instance tests_place with pk 3 does not exists'
                }
            ]
        })
        self.assertEqual(Restaurant.objects.count(), 1)

    def test_post_error(self, *args, **kwargs):
        url = reverse('django_forest:resources:list', kwargs={'resource': 'tests_question'})
        data = {
            'data': {
                'attributes': {
                    'question_text': '''aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
                    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
                    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
                    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
                    a''',
                }
            }
        }
        self.assertEqual(Question.objects.count(), 3)
        response = self.client.post(url,
                                    json.dumps(data),
                                    content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {
            'errors': [
                {
                    'detail': 'value too long for type character varying(200)\n'
                }
            ]
        })
        self.assertEqual(Question.objects.count(), 3)

    def test_delete(self, *args, **kwargs):
        data = {
            'data': {
                'attributes': {
                    'ids': ['1'],
                }
            }
        }
        self.assertEqual(Question.objects.count(), 3)
        response = self.client.delete(self.url,
                                      json.dumps(data),
                                      content_type='application/json')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Question.objects.count(), 2)

    def test_delete_scope(self, *args, **kwargs):
        ScopeManager.cache = {
            '1': {
                'scopes': mocked_scope,
                'fetched_at': 'useless-here'
            }
        }
        data = {
            'data': {
                'attributes': {
                    'ids': ['2'],
                }
            }
        }
        self.assertEqual(Question.objects.count(), 3)
        response = self.client.delete(self.url,
                                      json.dumps(data),
                                      content_type='application/json')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Question.objects.count(), 3)

    def test_delete_all_records(self, *args, **kwargs):
        data = {
            'data': {
                'attributes': {
                    'ids': [
                        '1'
                    ],
                    'collection_name': 'tests_question',
                    'parent_collection_name': None,
                    'parent_collection_id': None,
                    'parent_association_name': None,
                    'all_records': True,
                    'all_records_subset_query': {
                        'fields[tests_question]': 'id,question_text,pub_date',
                        'fields[subject]': 'name',
                        'fields[subject2]': 'name',
                        'fields[topic]': 'name',
                        'page[number]': 1,
                        'page[size]': 15,
                        'sort': '-id',
                        'filters': '{\"field\":\"question_text\",\"operator\":\"equal\",\"value\":\"what is your favorite color?\"}',
                        "searchExtended": 0
                    },
                    'all_records_ids_excluded': [],
                    'smart_action_id': None
                },
                'type': 'action-requests'
            }
        }
        self.assertEqual(Question.objects.count(), 3)
        response = self.client.delete(self.url,
                                      json.dumps(data),
                                      content_type='application/json')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Question.objects.count(), 2)

    def test_delete_no_model(self, *args, **kwargs):
        data = {
            'data': {
                'attributes': {
                    'ids': ['1'],
                }
            }
        }
        self.assertEqual(Question.objects.count(), 3)
        response = self.client.delete(self.bad_url,
                                      json.dumps(data),
                                      content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {'errors': [{'detail': 'no model found for resource tests_foo'}]})
        self.assertEqual(Question.objects.count(), 3)
