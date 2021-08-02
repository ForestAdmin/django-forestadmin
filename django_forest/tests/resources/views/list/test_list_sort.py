import copy

import pytest
from django.test import TransactionTestCase
from django.urls import reverse

from django_forest.tests.fixtures.schema import test_schema
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
        Schema.handle_json_api_schema()
        self.url = reverse('django_forest:resources:list', kwargs={'resource': 'Question'})
        self.reverse_url = reverse('django_forest:resources:list', kwargs={'resource': 'Choice'})
        self.no_data_url = reverse('django_forest:resources:list', kwargs={'resource': 'Waiter'})
        self.enum_url = reverse('django_forest:resources:list', kwargs={'resource': 'Student'})
        self.uuid_url = reverse('django_forest:resources:list', kwargs={'resource': 'Serial'})
        self.one_to_one_url = reverse('django_forest:resources:list', kwargs={'resource': 'Restaurant'})
        self.bad_url = reverse('django_forest:resources:list', kwargs={'resource': 'Foo'})

    def tearDown(self):
        # reset _registry after each test
        JsonApiSchema._registry = {}

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
                        'pub_date': '2021-06-03T13:52:53.528000+00:00',
                        'question_text': 'who is your favorite singer?'
                    },
                    'id': 3,
                    'links': {
                        'self': '/forest/Question/3'
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
                },
            ]
        })

    def test_get_sort_related_data(self):
        with self._django_assert_num_queries(4) as captured:
            response = self.client.get(self.reverse_url, {
                'fields[Choice]': 'id,question,choice_text',
                'fields[question]': 'question_text',
                'page[number]': 1,
                'page[size]': 15,
                'sort': 'question.question_text',
                'searchExtended': 0
            })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(captured.captured_queries[0]['sql'],
                         ' '.join('''SELECT "tests_choice"."id", "tests_choice"."question_id", "tests_choice"."choice_text"
                          FROM "tests_choice"
                           LEFT OUTER JOIN "tests_question" ON ("tests_choice"."question_id" = "tests_question"."id")
                          ORDER BY "tests_question"."question_text"
                          ASC
                          LIMIT 15'''.replace('\n', ' ').split()))
