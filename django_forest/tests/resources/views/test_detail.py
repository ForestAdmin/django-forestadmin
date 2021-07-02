import copy
import json

from django.core.exceptions import ObjectDoesNotExist
from django.test import TransactionTestCase
from django.urls import reverse

from django_forest.tests.fixtures.schema import test_schema
from django_forest.tests.models import Question, Restaurant, Place
from django_forest.utils.schema import Schema
from django_forest.utils.schema.json_api_schema import JsonApiSchema


class ResourceDetailViewTests(TransactionTestCase):
    fixtures = ['article.json', 'publication.json',
                'session.json',
                'question.json', 'choice.json',
                'place.json', 'restaurant.json',
                ]

    def setUp(self):
        Schema.schema = copy.deepcopy(test_schema)
        Schema.handle_json_api_serializer()
        self.url = reverse('resources:detail', kwargs={'resource': 'Question', 'pk': '1'})
        self.reverse_url = reverse('resources:detail', kwargs={'resource': 'Choice', 'pk': '1'})
        self.one_to_one_url = reverse('resources:detail', kwargs={'resource': 'Restaurant', 'pk': '1'})
        self.bad_url = reverse('resources:detail', kwargs={'resource': 'Foo', 'pk': '1'})

    def tearDown(self):
        # reset _registry after each test
        JsonApiSchema._registry = {}

    def test_get(self):
        response = self.client.get(self.url)
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {
            'data': {
                'type': 'question',
                'attributes': {
                    'pub_date': '2021-06-02T13:52:53.528000+00:00',
                    'question_text': 'what is your favorite color?'
                },
                'relationships': {
                    'choice_set': {
                        'links': {
                            'related': '/forest/Question/1/relationships/choice_set'
                        }
                    }
                },
                'id': 1,
                'links': {
                    'self': '/forest/Question/1'
                }
            },
            'links': {
                'self': '/forest/Question/1'
            }
        })

    def test_get_no_model(self):
        response = self.client.get(self.bad_url)
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {'errors': [{'detail': 'no model found for resource Foo'}]})

    def test_put(self):
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
                'type': 'question',
                'attributes': {
                    'pub_date': '2021-06-02T13:52:53.528000+00:00',
                    'question_text': 'What is your favorite animal?'
                },
                'relationships': {
                    'choice_set': {
                        'links': {
                            'related': '/forest/Question/1/relationships/choice_set'
                        }
                    }
                },
                'id': 1,
                'links': {
                    'self': '/forest/Question/1'
                }
            },
            'links': {
                'self': '/forest/Question/1'
            }
        })

    def test_put_related_data(self):
        body = {
            'data': {
                'attributes': {
                    'serves_pizza': False,
                },
                'relationships': {
                    'place': {
                        'data': {
                            'type': 'Places',
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
                'type': 'restaurant',
                'attributes': {
                    'serves_pizza': False,
                    'serves_hot_dogs': True
                },
                'relationships': {
                    'place': {
                        'links': {
                            'related': '/forest/Restaurant/2/relationships/place'
                        }
                    },
                    'waiter_set': {
                        'links': {
                            'related': '/forest/Restaurant/2/relationships/waiter_set'
                        }
                    }
                },
                'id': 2,
                'links': {
                    'self': '/forest/Restaurant/2'
                }
            },
            'links': {
                'self': '/forest/Restaurant/2'
            }
        })
        self.assertEqual(Restaurant.objects.count(), 1)
        self.assertEqual(Place.objects.count(), 2)

    def test_put_related_data_none(self):
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
                        }
                    }},
                'links': {
                    'self': '/forest/Choice/1'
                }
            },
            'links': {
                'self': '/forest/Choice/1'
            }
        })

    def test_put_related_data_do_not_exist(self):
        body = {
            'data': {
                'attributes': {
                    'serves_hot_dogs': True,
                },
                'relationships': {
                    'place': {
                        'data': {
                            'type': 'Places',
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
                    'detail': 'Instance Place with pk 3 does not exists'
                }
            ]
        })
        self.assertEqual(Question.objects.count(), 2)

    def test_put_no_model(self):
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
        self.assertEqual(data, {'errors': [{'detail': 'no model found for resource Foo'}]})

    def test_delete(self):
        self.assertEqual(Question.objects.count(), 2)
        self.assertTrue(Question.objects.get(pk=1))
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Question.objects.count(), 1)
        with self.assertRaises(ObjectDoesNotExist):
            Question.objects.get(pk=1)

    def test_delete_no_model(self):
        response = self.client.delete(self.bad_url)
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {'errors': [{'detail': 'no model found for resource Foo'}]})
