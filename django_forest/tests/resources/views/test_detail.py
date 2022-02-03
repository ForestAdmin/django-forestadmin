import json
from unittest import mock

import sys

import pytest
from django.core.exceptions import ObjectDoesNotExist
from django.test import TransactionTestCase
from django.urls import reverse

from django_forest.tests.models import Question, Restaurant, Place
from django_forest.tests.resources.views.list.test_list_scope import mocked_scope
from django_forest.utils.schema import Schema
from django_forest.utils.schema.json_api_schema import JsonApiSchema
from django_forest.utils.scope import ScopeManager


# reset forest config dir auto import
@pytest.fixture()
def reset_config_dir_import():
    for key in list(sys.modules.keys()):
        if key.startswith('django_forest.tests.forest'):
            del sys.modules[key]

@mock.patch('django_forest.utils.scope.ScopeManager._has_cache_expired', return_value=False)
@pytest.mark.usefixtures('reset_config_dir_import')
class ResourceDetailViewTests(TransactionTestCase):
    fixtures = ['article.json', 'publication.json',
                'session.json',
                'question.json', 'choice.json',
                'place.json', 'restaurant.json',
                ]

    def setUp(self, *args, **kwargs):
        Schema.build_schema()
        Schema.add_smart_features()
        Schema.handle_json_api_schema()
        self.url = reverse('django_forest:resources:detail', kwargs={'resource': 'tests_question', 'pk': '1'})
        self.reverse_url = reverse('django_forest:resources:detail', kwargs={'resource': 'tests_choice', 'pk': '1'})
        self.one_to_one_url = reverse('django_forest:resources:detail', kwargs={'resource': 'tests_restaurant', 'pk': '1'})
        self.bad_url = reverse('django_forest:resources:detail', kwargs={'resource': 'tests_foo', 'pk': '1'})
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

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    def test_get(self, *args, **kwargs):
        response = self.client.get(self.url)
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {
            'data': {
                'type': 'tests_question',
                'attributes': {
                    'bar': 'what is your favorite color?+bar',
                    'foo': 'what is your favorite color?+foo',
                    'pub_date': '2021-06-02T13:52:53.528000+00:00',
                    'question_text': 'what is your favorite color?'
                },
                'relationships': {
                    'choice_set': {
                        'links': {
                            'related': '/forest/tests_question/1/relationships/choice_set'
                        }
                    },
                    'topic': {
                        'data': None,
                        'links': {'related': '/forest/tests_question/1/relationships/topic'}
                    }
                },
                'id': 1,
                'links': {
                    'self': '/forest/tests_question/1'
                }
            },
            'links': {
                'self': '/forest/tests_question/1'
            }
        })

    @mock.patch('jose.jwt.decode', return_value={'id': 1})
    def test_get_invalid_token(self, *args, **kwargs):
        response = self.client.get(self.url)
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {'errors': [{'detail': 'Missing required rendering_id'}]})

    def test_get_no_model(self, *args, **kwargs):
        response = self.client.get(self.bad_url)
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {'errors': [{'detail': 'no model found for resource tests_foo'}]})

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    def test_get_scope(self, *args, **kwargs):
        ScopeManager.cache = {
            '1': {
                'scopes': mocked_scope,
                'fetched_at': 'useless-here'
            }
        }
        response = self.client.get(self.url, {
            'timezone': 'Europe/Paris',
        })
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {
            'data': {
                'type': 'tests_question',
                'attributes': {
                    'bar': 'what is your favorite color?+bar',
                    'foo': 'what is your favorite color?+foo',
                    'pub_date': '2021-06-02T13:52:53.528000+00:00',
                    'question_text': 'what is your favorite color?'
                },
                'relationships': {
                    'choice_set': {
                        'links': {
                            'related': '/forest/tests_question/1/relationships/choice_set'
                        }
                    },
                    'topic': {'data': None,
                              'links': {'related': '/forest/tests_question/1/relationships/topic'}}
                },
                'id': 1,
                'links': {
                    'self': '/forest/tests_question/1'
                }
            },
            'links': {
                'self': '/forest/tests_question/1'
            }
        })

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    def test_get_scope_no_record(self, *args, **kwargs):
        ScopeManager.cache = {
            '1': {
                'scopes': {
                    'tests_question': {
                        'scope': {
                            'filter': {
                                'aggregator': 'and',
                                'conditions': [
                                    {
                                        'field': 'question_text',
                                        'operator': 'equal',
                                        'value': 'color'
                                    },
                                ]
                            },
                            'dynamicScopesValues': {}
                        }
                    }
                },
                'fetched_at': 'useless-here'
            }
        }
        response = self.client.get(self.url, {
            'timezone': 'Europe/Paris',
        })
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {'errors': [{'detail': "Record does not exist or you don't have the right to query it"}]})

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    def test_put(self, *args, **kwargs):
        body = {
            'data': {
                'attributes': {
                    'question_text': 'What is your favorite animal?',
                }
            }
        }
        response = self.client.put(self.url,
                                   json.dumps(body),
                                   content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {
            'data': {
                'type': 'tests_question',
                'attributes': {
                    'pub_date': '2021-06-02T13:52:53.528000+00:00',
                    'question_text': 'What is your favorite animal?',
                    'bar': 'what is your favorite color?+bar',
                    'foo': 'what is your favorite color?+foo',
                },
                'relationships': {
                    'choice_set': {
                        'links': {
                            'related': '/forest/tests_question/1/relationships/choice_set'
                        }
                    },
                    'topic': {'links': {'related': '/forest/tests_question/1/relationships/topic'}}
                },
                'id': 1,
                'links': {
                    'self': '/forest/tests_question/1'
                }
            },
            'links': {
                'self': '/forest/tests_question/1'
            }
        })

    @mock.patch('jose.jwt.decode', return_value={'id': 1})
    def test_put_invalid_token(self, *args, **kwargs):
        body = {
            'data': {
                'attributes': {
                    'question_text': 'What is your favorite animal?',
                }
            }
        }
        response = self.client.put(self.url,
                                   json.dumps(body),
                                   content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {'errors': [{'detail': 'Missing required rendering_id'}]})

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    def test_put_related_data(self, *args, **kwargs):
        body = {
            'data': {
                'attributes': {
                    'serves_pizza': False,
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
        self.assertEqual(Place.objects.count(), 2)
        response = self.client.put(self.one_to_one_url,
                                   json.dumps(body),
                                   content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {
            'data': {
                'type': 'tests_restaurant',
                'attributes': {
                    'serves_pizza': False,
                    'serves_hot_dogs': True
                },
                'relationships': {
                    'place': {
                        'links': {
                            'related': '/forest/tests_restaurant/2/relationships/place'
                        }
                    },
                    'waiter_set': {
                        'links': {
                            'related': '/forest/tests_restaurant/2/relationships/waiter_set'
                        }
                    }
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
        self.assertEqual(Restaurant.objects.count(), 1)
        self.assertEqual(Place.objects.count(), 2)

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    def test_put_related_data_none(self, *args, **kwargs):
        body = {
            'data': {
                'attributes': {},
                'relationships': {
                    'question': {
                        'data': None
                    },
                }
            }
        }
        response = self.client.put(self.reverse_url,
                                   json.dumps(body),
                                   content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {
            'data': {
                'type': 'tests_choice',
                'id': 1,
                'attributes': {
                    'choice_text': 'yes',
                    'votes': 0
                },
                'relationships': {
                    'question': {
                        'links': {
                            'related': '/forest/tests_choice/1/relationships/question'
                        }
                    },
                    'topic': {
                        'links': {
                            'related': '/forest/tests_choice/1/relationships/topic'
                        }
                    }
                },
                'links': {
                    'self': '/forest/tests_choice/1'
                }
            },
            'links': {
                'self': '/forest/tests_choice/1'
            }
        })

    def test_put_related_data_do_not_exist(self, *args, **kwargs):
        body = {
            'data': {
                'attributes': {
                    'serves_hot_dogs': True,
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
        response = self.client.put(self.one_to_one_url,
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

    def test_put_no_model(self, *args, **kwargs):
        body = {
            'data': {
                'attributes': {
                    'question_text': 'What is your favorite animal?',
                }
            }
        }
        response = self.client.put(self.bad_url,
                                   json.dumps(body),
                                   content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {'errors': [{'detail': 'no model found for resource tests_foo'}]})

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    def test_put_smart_field(self, *args, **kwargs):
        body = {
            'data': {
                'attributes': {
                    'foo': 'What is your favorite animal?',
                    'bar': 'What is your favorite animal?',
                }
            }
        }
        response = self.client.put(self.url,
                                   json.dumps(body),
                                   content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {
            'data': {
                'type': 'tests_question',
                'attributes': {
                    'pub_date': '2021-06-02T13:52:53.528000+00:00',
                    'question_text': 'bar+What is your favorite animal?',
                    'bar': 'what is your favorite color?+bar',
                    'foo': 'what is your favorite color?+foo',
                },
                'relationships': {
                    'choice_set': {
                        'links': {
                            'related': '/forest/tests_question/1/relationships/choice_set'
                        }
                    },
                    'topic': {'links': {'related': '/forest/tests_question/1/relationships/topic'}}
                },
                'id': 1,
                'links': {
                    'self': '/forest/tests_question/1'
                }
            },
            'links': {
                'self': '/forest/tests_question/1'
            }
        })


    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    def test_delete(self, *args, **kwargs):
        self.assertEqual(Question.objects.count(), 3)
        self.assertTrue(Question.objects.get(pk=1))
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Question.objects.count(), 2)
        with self.assertRaises(ObjectDoesNotExist):
            Question.objects.get(pk=1)

    @mock.patch('jose.jwt.decode', return_value={'id': 1})
    def test_delete_invalid_token(self, *args, **kwargs):
        response = self.client.delete(self.url)
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {'errors': [{'detail': 'Missing required rendering_id'}]})

    def test_delete_no_model(self, *args, **kwargs):
        response = self.client.delete(self.bad_url)
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {'errors': [{'detail': 'no model found for resource tests_foo'}]})
