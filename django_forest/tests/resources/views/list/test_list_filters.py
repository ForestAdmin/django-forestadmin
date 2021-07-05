import copy
import pytest
from django.test import TransactionTestCase
from django.urls import reverse

from django_forest.tests.fixtures.schema import test_schema
from django_forest.utils.schema import Schema
from django_forest.utils.schema.json_api_schema import JsonApiSchema


class ResourceListFilterViewTests(TransactionTestCase):
    fixtures = ['question.json', 'choice.json']

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, django_assert_num_queries):
        self._django_assert_num_queries = django_assert_num_queries

    def setUp(self):
        Schema.schema = copy.deepcopy(test_schema)
        Schema.handle_json_api_schema()
        self.url = reverse('resources:list', kwargs={'resource': 'Question'})
        self.reverse_url = reverse('resources:list', kwargs={'resource': 'Choice'})

    def tearDown(self):
        # reset _registry after each test
        JsonApiSchema._registry = {}

    def test_is(self):
        response = self.client.get(self.url, {
            'fields[Question]': 'id,question_text,pub_date',
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
                    'type': 'question',
                    'id': 1,
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

    def test_aggregator(self):
        response = self.client.get(self.url, {
            'fields[Question]': 'id,question_text,pub_date',
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
                    'type': 'question',
                    'id': 1,
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

    def test_aggregator_or(self):
        response = self.client.get(self.url, {
            'fields[Question]': 'id,question_text,pub_date',
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
                    'type': 'question',
                    'attributes': {
                        'pub_date': '2021-06-02T13:52:53.528000+00:00',
                        'question_text': 'what is your favorite color?'
                    },
                    'id': 1,
                    'links': {
                        'self': '/forest/Question/1'
                    }
                },
                {
                    'type': 'question',
                    'attributes': {
                        'pub_date': '2021-06-02T15:52:53.528000+00:00',
                        'question_text': 'do you like chocolate?'
                    },
                    'id': 2,
                    'links': {
                        'self': '/forest/Question/2'
                    }
                }
            ]
        })

    def test_is_not(self):
        response = self.client.get(self.url, {
            'fields[Question]': 'id,question_text,pub_date',
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
                    'type': 'question',
                    'attributes': {
                        'pub_date': '2021-06-02T15:52:53.528000+00:00',
                        'question_text': 'do you like chocolate?'
                    },
                    'id': 2,
                    'links': {
                        'self': '/forest/Question/2'
                    }
                },
                {
                    'type': 'question',
                    'attributes': {
                        'pub_date': '2021-06-03T13:52:53.528000+00:00',
                        'question_text': 'who is your favorite singer?'
                    },
                    'id': 3,
                    'links': {
                        'self': '/forest/Question/3'
                    }
                }
            ]
        })

    def test_is_realted_data(self):
        response = self.client.get(self.reverse_url, {
            'fields[Choice]': 'id,choice_text,question',
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
                    'type': 'choice',
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
                    'attributes': {
                        'choice_text': 'yes'
                    },
                    'id': 1,
                    'links': {
                        'self': '/forest/Choice/1'
                    }
                },
                {
                    'type': 'choice',
                    'relationships': {
                        'question': {
                            'links': {
                                'related': '/forest/Choice/2/relationships/question'
                            },
                            'data': {
                                'type': 'question',
                                'id': '1'
                            }
                        }
                    },
                    'attributes': {
                        'choice_text': 'no'
                    },
                    'id': 2,
                    'links': {
                        'self': '/forest/Choice/2'
                    }
                }
            ],
            'included': [
                {
                    'type': 'question',
                    'attributes': {
                        'question_text': 'what is your favorite color?'
                    },
                    'id': 1,
                    'links': {
                        'self': '/forest/Question/1'
                    }
                }
            ]
        })

    def test_wrong_operator(self):
        response = self.client.get(self.url, {
            'fields[Question]': 'id,question_text,pub_date',
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

    def test_blank(self):
        response = self.client.get(self.url, {
            'fields[Question]': 'id,question_text,pub_date',
            'filters': '{"field":"question_text","operator":"blank","value":null}',
            'timezone': 'Europe/Paris',
            'page[number]': '1',
            'page[size]': '15'
        })
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {'data': []})

    def test_blank_date(self):
        response = self.client.get(self.url, {
            'fields[Question]': 'id,question_text,pub_date',
            'filters': '{"field":"id","operator":"blank","value":null}',
            'timezone': 'Europe/Paris',
            'page[number]': '1',
            'page[size]': '15'
        })
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {'data': []})

    def test_is_present(self):
        response = self.client.get(self.url, {
            'fields[Question]': 'id,question_text,pub_date',
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
                    'type': 'question',
                    'id': 1,
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
                    'attributes': {
                        'pub_date': '2021-06-02T15:52:53.528000+00:00',
                        'question_text': 'do you like chocolate?'
                    },
                    'links': {
                        'self': '/forest/Question/2'
                    }
                },
                {
                    'type': 'question',
                    'id': 3,
                    'attributes': {
                        'pub_date': '2021-06-03T13:52:53.528000+00:00',
                        'question_text': 'who is your favorite singer?'
                    },
                    'links': {
                        'self': '/forest/Question/3'
                    }
                }
            ]
        })
