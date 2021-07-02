import copy
import json
import sys

import pytest
from django.test import TransactionTestCase
from django.urls import reverse

from django_forest.tests.fixtures.schema import test_schema
from django_forest.tests.models import Question, Restaurant
from django_forest.utils.schema import Schema
from django_forest.utils.schema.json_api_schema import JsonApiSchema


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
        Schema.handle_json_api_serializer()
        self.url = reverse('resources:list', kwargs={'resource': 'Question'})
        self.reverse_url = reverse('resources:list', kwargs={'resource': 'Choice'})
        self.no_data_url = reverse('resources:list', kwargs={'resource': 'Waiter'})
        self.enum_url = reverse('resources:list', kwargs={'resource': 'Student'})
        self.uuid_url = reverse('resources:list', kwargs={'resource': 'Serial'})
        self.one_to_one_url = reverse('resources:list', kwargs={'resource': 'Restaurant'})
        self.bad_url = reverse('resources:list', kwargs={'resource': 'Foo'})

    def tearDown(self):
        # reset _registry after each test
        JsonApiSchema._registry = {}

    def test_get(self):
        response = self.client.get(self.url, {'page[number]': '1', 'page[size]': '15'})
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {
            'data': [
                {
                    'type': 'question',
                    'relationships': {
                        'choice_set': {
                            'links': {
                                'related': '/forest/Question/1/relationships/choice_set'
                            }
                        }
                    },
                    'attributes': {
                        'question_text': 'what is your favorite color?',
                        'pub_date': '2021-06-02T13:52:53.528000+00:00'},
                    'id': 1,
                    'links': {
                        'self': '/forest/Question/1'
                    }
                }, {
                    'type': 'question',
                    'relationships': {
                        'choice_set': {
                            'links': {
                                'related': '/forest/Question/2/relationships/choice_set'
                            }
                        }
                    },
                    'attributes': {
                        'question_text': 'do you like chocolate?',
                        'pub_date': '2021-06-02T15:52:53.528000+00:00'
                    },
                    'id': 2, 'links': {
                        'self': '/forest/Question/2'
                    }
                }
            ]
        })

    def test_get_no_data(self):
        response = self.client.get(self.no_data_url)
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {'data': []})

    def test_get_no_model(self):
        response = self.client.get(self.bad_url, {'page[number]': '1', 'page[size]': '15'})
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {'errors': [{'detail': 'no model found for resource Foo'}]})

    def test_get_search_to_edit(self):
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
                    }
                },
                    'links': {
                        'self': '/forest/Question/1'
                    }
                }
            ]
        })

    def test_get_search_pk_no_id(self):
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

    def test_get_search_number(self):
        with self._django_assert_num_queries(1) as captured:
            response = self.client.get(self.url, {
                'fields[Question]': 'id,question_text,pub_date',
                'page[number]': 1,
                'page[size]': 15,
                'search': 1,
                'searchExtended': 0
            })
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(captured.captured_queries[0]['sql'],
                         ' '.join('''SELECT "tests_question"."id", "tests_question"."question_text", "tests_question"."pub_date"
                                  FROM "tests_question"
                                   WHERE ("tests_question"."id" = 1
                                    OR "tests_question"."question_text"::text LIKE \'%1%\')
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
                    }
                }
            ]
        })

    def test_get_search_number_max_size(self):
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
                            OR "tests_question"."question_text"::text LIKE '%9223372036854775808%')
                          LIMIT 15'''.replace('\n', ' ').split()))
        self.assertEqual(data, {
            'data': []
        })

    def test_get_search_enum(self):
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
            ]
        })

    def test_get_search_uuid(self):
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
            ]
        })

    def test_get_extended_search(self):
        with self._django_assert_num_queries(1) as captured:
            response = self.client.get(self.url, {
                'fields[Question]': 'id,question_text,pub_date',
                'page[number]': 1,
                'page[size]': 15,
                'search': 'yes',
                'searchExtended': 1
            })
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(captured.captured_queries[0]['sql'],
                         ' '.join('''SELECT "tests_question"."id", "tests_question"."question_text", "tests_question"."pub_date"
                          FROM "tests_question"
                           LEFT OUTER JOIN "tests_choice" ON ("tests_question"."id" = "tests_choice"."question_id")
                            WHERE ("tests_question"."question_text"::text LIKE '%yes%' 
                            OR "tests_choice"."choice_text"::text LIKE '%yes%')
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
                    }
                }
            ]
        })

    def test_get_sort(self):
        with self._django_assert_num_queries(1) as captured:
            response = self.client.get(self.url, {
                'fields[Question]': 'id,question_text,pub_date',
                'page[number]': 1,
                'page[size]': 15,
                'sort': '-id',
                'searchExtended': 0
            })
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(captured.captured_queries[0]['sql'],
                         ' '.join('''SELECT "tests_question"."id", "tests_question"."question_text", "tests_question"."pub_date"
                          FROM "tests_question"
                           ORDER BY "tests_question"."id"
                           DESC
                           LIMIT 15'''.replace('\n', ' ').split()))
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
                        'pub_date': '2021-06-02T13:52:53.528000+00:00',
                        'question_text': 'what is your favorite color?'
                    },
                    'id': 1,
                    'links': {
                        'self': '/forest/Question/1'
                    }
                }
            ]
        })

    def test_get_sort_related_data(self):
        with self._django_assert_num_queries(3) as captured:
            response = self.client.get(self.reverse_url, {
                'fields[Choice]': 'id,question,choice_text',
                'fields[question]': 'question_text',
                'page[number]': 1,
                'page[size]': 15,
                'sort': 'question.question_text',
                'searchExtended': 0
            })
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(captured.captured_queries[0]['sql'],
                         ' '.join('''SELECT "tests_choice"."id", "tests_choice"."question_id", "tests_choice"."choice_text"
                          FROM "tests_choice"
                           LEFT OUTER JOIN "tests_question" ON ("tests_choice"."question_id" = "tests_question"."id")
                          ORDER BY "tests_question"."question_text"
                          ASC
                          LIMIT 15'''.replace('\n', ' ').split()))
        self.assertEqual(data, {
            'data': [
                {
                    'type': 'choice',
                    'attributes': {
                        'choice_text': 'yes'
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
                {
                    'type': 'choice',
                    'attributes': {
                        'choice_text': 'no'
                    },
                    'id': 2,
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

    def test_post(self):
        body = {
            'data': {
                'attributes': {
                    'question_text': 'What is your favorite color',
                    'pub_date': '2021-06-21T09:46:39.000Z'
                }
            }
        }
        self.assertEqual(Question.objects.count(), 2)
        response = self.client.post(self.url,
                                    json.dumps(body),
                                    content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {
            'data': {
                'type': 'question',
                'relationships': {
                    'choice_set': {
                        'links': {
                            'related': '/forest/Question/3/relationships/choice_set'
                        }
                    }
                },
                'attributes': {
                    'pub_date': '2021-06-21T09:46:39+00:00',
                    'question_text': 'What is your favorite color'
                },
                'id': 3,
                'links': {
                    'self': '/forest/Question/3'
                }
            },
            'links': {
                'self': '/forest/Question/3'
            }
        })
        self.assertEqual(Question.objects.count(), 3)

    def test_post_no_model(self):
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
        self.assertEqual(data, {'errors': [{'detail': 'no model found for resource Foo'}]})

    def test_post_related_data(self):
        body = {
            'data': {
                'attributes': {
                    'serves_hot_dogs': False,
                    'serves_pizzas': False
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
        response = self.client.post(self.one_to_one_url,
                                    json.dumps(body),
                                    content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {
            'data': {
                'type': 'restaurant',
                'relationships': {
                    'waiter_set': {
                        'links': {
                            'related': '/forest/Restaurant/2/relationships/waiter_set'
                        }
                    },
                    'place': {
                        'links': {
                            'related': '/forest/Restaurant/2/relationships/place'
                        }
                    }
                },
                'attributes': {
                    'serves_hot_dogs': False,
                    'serves_pizza': False
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
        self.assertEqual(Restaurant.objects.count(), 2)

    def test_post_related_data_do_not_exist(self):
        body = {
            'data': {
                'attributes': {
                    'serves_hot_dogs': False,
                    'serves_pizzas': False
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
        response = self.client.post(self.one_to_one_url,
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

    def test_post_error(self):
        url = reverse('resources:list', kwargs={'resource': 'Question'})
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
        self.assertEqual(Question.objects.count(), 2)
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
        self.assertEqual(Question.objects.count(), 2)

    def test_delete(self):
        data = {
            'data': {
                'attributes': {
                    'ids': ['1'],
                }
            }
        }
        self.assertEqual(Question.objects.count(), 2)
        response = self.client.delete(self.url,
                                      json.dumps(data),
                                      content_type='application/json')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Question.objects.count(), 1)

    def test_delete_no_model(self):
        data = {
            'data': {
                'attributes': {
                    'ids': ['1'],
                }
            }
        }
        self.assertEqual(Question.objects.count(), 2)
        response = self.client.delete(self.bad_url,
                                      json.dumps(data),
                                      content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {'errors': [{'detail': 'no model found for resource Foo'}]})
