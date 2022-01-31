import copy
from datetime import datetime
from unittest import mock

import pytest
from django.test import TransactionTestCase
from django.urls import reverse
from freezegun import freeze_time

from django_forest.tests.fixtures.schema import test_schema
from django_forest.utils.schema import Schema
from django_forest.utils.schema.json_api_schema import JsonApiSchema
from django_forest.utils.scope import ScopeManager
from django_forest.utils.date import get_timezone


@mock.patch('django_forest.utils.scope.ScopeManager._has_cache_expired', return_value=False)
@mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})    
class ResourceListFilterDateViewTests(TransactionTestCase):
    fixtures = ['question.json']

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, django_assert_num_queries):
        self._django_assert_num_queries = django_assert_num_queries

    def setUp(self):
        Schema.schema = copy.deepcopy(test_schema)
        Schema.handle_json_api_schema()
        self.url = reverse('django_forest:resources:list', kwargs={'resource': 'tests_question'})
        self.client = self.client_class(
            HTTP_AUTHORIZATION='Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjUiLCJlbWFpbCI6Imd1aWxsYXVtZWNAZm9yZXN0YWRtaW4uY29tIiwiZmlyc3RfbmFtZSI6Ikd1aWxsYXVtZSIsImxhc3RfbmFtZSI6IkNpc2NvIiwidGVhbSI6Ik9wZXJhdGlvbnMiLCJyZW5kZXJpbmdfaWQiOjEsImV4cCI6MTYyNTY3OTYyNi44ODYwMTh9.mHjA05yvMr99gFMuFv0SnPDCeOd2ZyMSN868V7lsjnw')
        ScopeManager.cache = {
            '1': {
                'scopes': {},
                'fetched_at': 'useless-here'
            }
        }

    def tearDown(self):
        # reset _registry after each test
        JsonApiSchema._registry = {}
        ScopeManager.cache = {}

    @freeze_time(
        lambda: datetime(2021, 6, 2, 17, 0, 0, 0, tzinfo=get_timezone('Europe/Paris'))
    )
    def test_past(self, *args, **kwargs):
        response = self.client.get(self.url, {
            'fields[tests_question]': 'id,topic,question_text,pub_date',
            'fields[topic]': 'name',
            'filters': '{"field":"pub_date","operator":"past","value":null}',
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


    @freeze_time(
        lambda: datetime(2021, 6, 2, 17, 0, 0, 0, tzinfo=get_timezone('Europe/Paris')),
    )
    def test_future(self, *args, **kwargs):
        response = self.client.get(self.url, {
            'fields[tests_question]': 'id,topic,question_text,pub_date',
            'fields[topic]': 'name',
            'filters': '{"field":"pub_date","operator":"future","value":null}',
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

    @freeze_time(
        lambda: datetime(2021, 6, 2, 15, 0, 0, 0, tzinfo=get_timezone('Europe/Paris')),
    )
    def test_today(self, *args, **kwargs):
        response = self.client.get(self.url, {
            'fields[tests_question]': 'id,topic,question_text,pub_date',
            'filters': '{"field":"pub_date","operator":"today","value":null}',
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

    @freeze_time(
        lambda: datetime(2021, 6, 2, 17, 53, 0, 0, tzinfo=get_timezone('Europe/Paris')),
    )
    def test_before_x_hours_ago(self, *args, **kwargs):
        response = self.client.get(self.url, {
            'fields[tests_question]': 'id,topic,question_text,pub_date',
            'fields[topic]': 'name',
            'filters': '{"field":"pub_date","operator":"before_x_hours_ago","value":1}',
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

    @freeze_time(
        lambda: datetime(2021, 6, 2, 15, 53, 0, 0, tzinfo=get_timezone('Europe/Paris')),
    )
    def test_after_x_hours_ago(self, *args, **kwargs):
        response = self.client.get(self.url, {
            'fields[tests_question]': 'id,topic,question_text,pub_date',
            'fields[topic]': 'name',
            'filters': '{"field":"pub_date","operator":"after_x_hours_ago","value":1}',
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

    @freeze_time(
        lambda: datetime(2021, 7, 1, 0, 0, 0, 0, tzinfo=get_timezone('Europe/Paris')),
    )
    def test_previous_quarter(self, *args, **kwargs):
        response = self.client.get(self.url, {
            'fields[tests_question]': 'id,topic,question_text,pub_date',
            'fields[topic]': 'name',
            'filters': '{"field":"pub_date","operator":"previous_quarter","value":null}',
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

    @freeze_time(
        lambda: datetime(2021, 6, 30, 23, 59, 59, 999999, tzinfo=get_timezone('Europe/Paris')),
    )
    def test_previous_quarter_to_date(self, *args, **kwargs):
        response = self.client.get(self.url, {
            'fields[tests_question]': 'id,topic,question_text,pub_date',
            'fields[topic]': 'name',
            'filters': '{"field":"pub_date","operator":"previous_quarter_to_date","value":null}',
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
