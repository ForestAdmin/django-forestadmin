import copy
from datetime import datetime
from unittest import mock

import pytest
import pytz
from django.test import TransactionTestCase
from django.urls import reverse

from django_forest.tests.fixtures.schema import test_schema
from django_forest.utils.schema import Schema
from django_forest.utils.schema.json_api_schema import JsonApiSchema
from django_forest.utils.scope import ScopeManager


@mock.patch('django_forest.utils.scope.ScopeManager._has_cache_expired', return_value=False)
class ResourceListFilterViewTests(TransactionTestCase):
    fixtures = ['question.json', 'choice.json']

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, django_assert_num_queries):
        self._django_assert_num_queries = django_assert_num_queries

    def setUp(self):
        Schema.schema = copy.deepcopy(test_schema)
        Schema.handle_json_api_schema()
        self.url = reverse('django_forest:resources:list', kwargs={'resource': 'tests_question'})
        self.reverse_url = reverse('django_forest:resources:list', kwargs={'resource': 'tests_choice'})
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

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    def test_is(self, mocked_datetime, *args, **kwargs):
        response = self.client.get(self.url, {
            'fields[tests_question]': 'id,topic,question_text,pub_date',
            'fields[topic]': 'name',
            'filters': '{"field":"question_text","operator":"equal","value":"what is your favorite color?"}',
            'timezone': 'Europe/Paris',
            'page[number]': '1',
            'page[size]': '15'
        })
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {
            'data': [
                {
                    'type': 'tests_question',
                    'id': 1,
                    'attributes': {
                        'pub_date': '2021-06-02T13:52:53.528000+00:00',
                        'question_text': 'what is your favorite color?'
                    },
                    'links': {
                        'self': '/forest/tests_question/1'
                    },
                    'relationships': {
                        'topic': {
                            'data': None,
                            'links': {
                                'related': '/forest/tests_question/1/relationships/topic'
                            }
                        }
                    },
                }
            ]
        })

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    def test_startswith(self, mocked_datetime, *args, **kwargs):
        response = self.client.get(self.url, {
            'fields[tests_question]': 'id,topic,question_text,pub_date',
            'fields[topic]': 'name',
            'filters': '{"field":"question_text","operator":"starts_with","value":"What is your favorite color?"}',
            'timezone': 'Europe/Paris',
            'page[number]': '1',
            'page[size]': '15'
        })
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {
            'data': [
                {
                    'type': 'tests_question',
                    'id': 1,
                    'attributes': {
                        'pub_date': '2021-06-02T13:52:53.528000+00:00',
                        'question_text': 'what is your favorite color?'
                    },
                    'links': {
                        'self': '/forest/tests_question/1'
                    },
                    'relationships': {
                        'topic': {
                            'data': None,
                            'links': {
                                'related': '/forest/tests_question/1/relationships/topic'
                            }
                        }
                    },
                }
            ]
        })

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    def test_contains(self, mocked_datetime, *args, **kwargs):
        response = self.client.get(self.url, {
            'fields[tests_question]': 'id,topic,question_text,pub_date',
            'fields[topic]': 'name',
            'filters': '{"field":"question_text","operator":"contains","value":"WHAT is your Favorite color?"}',
            'timezone': 'Europe/Paris',
            'page[number]': '1',
            'page[size]': '15'
        })
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {
            'data': [
                {
                    'type': 'tests_question',
                    'id': 1,
                    'attributes': {
                        'pub_date': '2021-06-02T13:52:53.528000+00:00',
                        'question_text': 'what is your favorite color?'
                    },
                    'links': {
                        'self': '/forest/tests_question/1'
                    },
                    'relationships': {
                        'topic': {
                            'data': None,
                            'links': {
                                'related': '/forest/tests_question/1/relationships/topic'
                            }
                        }
                    },
                }
            ]
        })

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    def test_aggregator(self, *args, **kwargs):
        response = self.client.get(self.url, {
            'fields[tests_question]': 'id,topic,question_text,pub_date',
            'fields[topic]': 'name',
            'filters': '{"aggregator":"and","conditions":[{"field":"question_text","operator":"equal","value":"what is your favorite color?"},{"field":"id","operator":"equal","value":1}]}',
            'timezone': 'Europe/Paris',
            'page[number]': '1',
            'page[size]': '15'
        })
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {
            'data': [
                {
                    'type': 'tests_question',
                    'id': 1,
                    'attributes': {
                        'pub_date': '2021-06-02T13:52:53.528000+00:00',
                        'question_text': 'what is your favorite color?'
                    },
                    'links': {
                        'self': '/forest/tests_question/1'
                    },
                    'relationships': {
                        'topic': {
                            'data': None,
                            'links': {
                                'related': '/forest/tests_question/1/relationships/topic'
                            }
                        }
                    },
                }
            ]
        })

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    def test_nested_aggregator(self, *args, **kwargs):
        response = self.client.get(self.url, {
            'fields[tests_question]': 'id,topic,question_text,pub_date',
            'fields[topic]': 'name',
            'filters': '{"aggregator":"and","conditions":[{"field":"question_text","operator":"equal","value":"what is your favorite color?"},{"aggregator":"and","conditions":[{"field":"id","operator":"equal","value":1}, {"field": "id", "operator": "present", "value":null}]}]}',
            'timezone': 'Europe/Paris',
            'page[number]': '1',
            'page[size]': '15'
        })
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {
            'data': [
                {
                    'type': 'tests_question',
                    'id': 1,
                    'attributes': {
                        'pub_date': '2021-06-02T13:52:53.528000+00:00',
                        'question_text': 'what is your favorite color?'
                    },
                    'links': {
                        'self': '/forest/tests_question/1'
                    },
                    'relationships': {
                        'topic': {
                            'data': None,
                            'links': {
                                'related': '/forest/tests_question/1/relationships/topic'
                            }
                        }
                    },
                }
            ]
        })

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    def test_aggregator_or(self, *args, **kwargs):
        response = self.client.get(self.url, {
            'fields[tests_question]': 'id,topic,question_text,pub_date',
            'fields[topic]': 'name',
            'filters': '{"aggregator":"or","conditions":[{"field":"id","operator":"equal","value":1},{"field":"id","operator":"equal","value":2}]}',
            'timezone': 'Europe/Paris',
            'page[number]': '1',
            'page[size]': '15'
        })
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {
            'data': [
                {
                    'type': 'tests_question',
                    'attributes': {
                        'pub_date': '2021-06-02T13:52:53.528000+00:00',
                        'question_text': 'what is your favorite color?'
                    },
                    'id': 1,
                    'links': {
                        'self': '/forest/tests_question/1'
                    },
                    'relationships': {
                        'topic': {
                            'data': None,
                            'links': {
                                'related': '/forest/tests_question/1/relationships/topic'
                            }
                        }
                    },
                },
                {
                    'type': 'tests_question',
                    'attributes': {
                        'pub_date': '2021-06-02T15:52:53.528000+00:00',
                        'question_text': 'do you like chocolate?'
                    },
                    'id': 2,
                    'links': {
                        'self': '/forest/tests_question/2'
                    },
                    'relationships': {
                        'topic': {
                            'data': None,
                            'links': {
                                'related': '/forest/tests_question/2/relationships/topic'
                            }
                        }
                    },
                }
            ]
        })

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    def test_is_not(self, *args, **kwargs):
        response = self.client.get(self.url, {
            'fields[tests_question]': 'id,topic,question_text,pub_date',
            'fields[topic]': 'name',
            'filters': '{"field":"question_text","operator":"not","value":"what is your favorite color?"}',
            'timezone': 'Europe/Paris',
            'page[number]': '1',
            'page[size]': '15'
        })
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {
            'data': [
                {
                    'type': 'tests_question',
                    'attributes': {
                        'pub_date': '2021-06-02T15:52:53.528000+00:00',
                        'question_text': 'do you like chocolate?'
                    },
                    'id': 2,
                    'links': {
                        'self': '/forest/tests_question/2'
                    },
                    'relationships': {
                        'topic': {
                            'data': None,
                            'links': {
                                'related': '/forest/tests_question/2/relationships/topic'
                            }
                        }
                    },
                },
                {
                    'type': 'tests_question',
                    'attributes': {
                        'pub_date': '2021-06-03T13:52:53.528000+00:00',
                        'question_text': 'who is your favorite singer?'
                    },
                    'id': 3,
                    'links': {
                        'self': '/forest/tests_question/3'
                    },
                    'relationships': {
                        'topic': {
                            'data': None,
                            'links': {
                                'related': '/forest/tests_question/3/relationships/topic'
                            }
                        }
                    },
                }
            ]
        })

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    def test_is_related_data(self, *args, **kwargs):
        response = self.client.get(self.reverse_url, {
            'fields[tests_choice]': 'id,choice_text,question',
            'fields[question]': 'question_text',
            'filters': '{"field":"question:question_text","operator":"contains","value":"color"}',
            'timezone': 'Europe/Paris',
            'page[number]': '1',
            'page[size]': '15'
        })
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {
            'data': [
                {
                    'type': 'tests_choice',
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
                    'attributes': {
                        'choice_text': 'yes'
                    },
                    'id': 1,
                    'links': {
                        'self': '/forest/tests_choice/1'
                    }
                },
                {
                    'type': 'tests_choice',
                    'relationships': {
                        'question': {
                            'links': {
                                'related': '/forest/tests_choice/2/relationships/question'
                            },
                            'data': {
                                'type': 'tests_question',
                                'id': '1'
                            }
                        }
                    },
                    'attributes': {
                        'choice_text': 'no'
                    },
                    'id': 2,
                    'links': {
                        'self': '/forest/tests_choice/2'
                    }
                }
            ],
            'included': [
                {
                    'type': 'tests_question',
                    'attributes': {
                        'question_text': 'what is your favorite color?'
                    },
                    'id': 1,
                    'links': {
                        'self': '/forest/tests_question/1'
                    }
                }
            ]
        })

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    def test_wrong_operator(self, *args, **kwargs):
        response = self.client.get(self.url, {
            'fields[tests_question]': 'id,question_text,pub_date',
            'filters': '{"field":"question_text","operator":"foo","value":"what is your favorite color?"}',
            'timezone': 'Europe/Paris',
            'page[number]': '1',
            'page[size]': '15'
        })
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {
            'errors': [
                {
                    'detail': 'Unknown provided operator foo'
                }
            ]
        })

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    def test_blank(self, *args, **kwargs):
        response = self.client.get(self.url, {
            'fields[tests_question]': 'id,question_text,pub_date',
            'filters': '{"field":"question_text","operator":"blank","value":null}',
            'timezone': 'Europe/Paris',
            'page[number]': '1',
            'page[size]': '15'
        })
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {'data': []})

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    def test_blank_date(self, *args, **kwargs):
        response = self.client.get(self.url, {
            'fields[tests_question]': 'id,question_text,pub_date',
            'filters': '{"field":"id","operator":"blank","value":null}',
            'timezone': 'Europe/Paris',
            'page[number]': '1',
            'page[size]': '15'
        })
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {'data': []})

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    def test_is_present(self, *args, **kwargs):
        response = self.client.get(self.url, {
            'fields[tests_question]': 'id,topic,question_text,pub_date',
            'fields[topic]': 'name',
            'filters': '{"field":"pub_date","operator":"present","value":null}',
            'timezone': 'Europe/Paris',
            'page[number]': '1',
            'page[size]': '15'
        })
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {
            'data': [
                {
                    'type': 'tests_question',
                    'id': 1,
                    'attributes': {
                        'pub_date': '2021-06-02T13:52:53.528000+00:00',
                        'question_text': 'what is your favorite color?'
                    },
                    'links': {
                        'self': '/forest/tests_question/1'
                    },
                    'relationships': {
                        'topic': {
                            'data': None,
                            'links': {
                                'related': '/forest/tests_question/1/relationships/topic'
                            }
                        }
                    },
                },
                {
                    'type': 'tests_question',
                    'id': 2,
                    'attributes': {
                        'pub_date': '2021-06-02T15:52:53.528000+00:00',
                        'question_text': 'do you like chocolate?'
                    },
                    'links': {
                        'self': '/forest/tests_question/2'
                    },
                    'relationships': {
                        'topic': {
                            'data': None,
                            'links': {
                                'related': '/forest/tests_question/2/relationships/topic'
                            }
                        }
                    },
                },
                {
                    'type': 'tests_question',
                    'id': 3,
                    'attributes': {
                        'pub_date': '2021-06-03T13:52:53.528000+00:00',
                        'question_text': 'who is your favorite singer?'
                    },
                    'links': {
                        'self': '/forest/tests_question/3'
                    },
                    'relationships': {
                        'topic': {
                            'data': None,
                            'links': {
                                'related': '/forest/tests_question/3/relationships/topic'
                            }
                        }
                    },
                }
            ]
        })
