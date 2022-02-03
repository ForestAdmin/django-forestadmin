import copy
import json
from unittest import mock

from django.test import TransactionTestCase
from django.urls import reverse

from django_forest.tests.fixtures.schema import test_schema
from django_forest.tests.models import Restaurant, Publication, Article, Choice
from django_forest.utils.schema import Schema
from django_forest.utils.schema.json_api_schema import JsonApiSchema
from django_forest.utils.scope import ScopeManager


@mock.patch('django_forest.utils.scope.ScopeManager._has_cache_expired', return_value=False)
class ResourceAssociationListViewTests(TransactionTestCase):
    fixtures = ['article.json', 'publication.json',
                'session.json',
                'question.json', 'choice.json',
                'place.json', 'restaurant.json']

    def setUp(self):
        Schema.schema = copy.deepcopy(test_schema)
        Schema.handle_json_api_schema()
        self.url = reverse('django_forest:resources:associations:list',
                           kwargs={'resource': 'tests_question', 'pk': 1, 'association_resource': 'choice_set'})
        self.reverse_url = reverse('django_forest:resources:associations:list',
                                   kwargs={'resource': 'tests_choice', 'pk': 1, 'association_resource': 'question'})
        self.bad_url = reverse('django_forest:resources:associations:list',
                               kwargs={'resource': 'Foo', 'pk': 1, 'association_resource': 'choice_set'})
        self.bad_association_url = reverse('django_forest:resources:associations:list',
                                           kwargs={'resource': 'tests_question', 'pk': 1, 'association_resource': 'foo'})

        self.many_url = reverse('django_forest:resources:associations:list',
                                kwargs={'resource': 'tests_publication', 'pk': 2, 'association_resource': 'article_set'})
        self.many_reverse_url = reverse('django_forest:resources:associations:list',
                                        kwargs={'resource': 'tests_article', 'pk': 1, 'association_resource': 'publications'})
        self.many_bad_url = reverse('django_forest:resources:associations:list',
                                    kwargs={'resource': 'Foo', 'pk': 2, 'association_resource': 'article_set'})
        self.many_bad_association_url = reverse('django_forest:resources:associations:list',
                                                kwargs={'resource': 'tests_publication', 'pk': 2,
                                                        'association_resource': 'foo'})
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

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    def test_get(self, *args, **kwargs):
        response = self.client.get(self.url, {
            'page[number]': '1',
            'page[size]': '15',
            'fields[tests_choice]': 'id,question,choice_text',
            'fields[question]': 'question_text'
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
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
                    'id': 1,
                    'attributes': {
                        'choice_text': 'yes'
                    },
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
                    'id': 2,
                    'attributes': {
                        'choice_text': 'no'
                    },
                    'links': {
                        'self': '/forest/tests_choice/2'
                    }
                }
            ],
            'included': [
                {
                    'type': 'tests_question',
                    'id': 1,
                    'attributes': {
                        'question_text': 'what is your favorite color?'
                    },
                    'links': {
                        'self': '/forest/tests_question/1'
                    }
                }
            ]
        })

    def test_get_no_model(self, *args, **kwargs):
        response = self.client.get(self.bad_url, {
            'page[number]': '1',
            'page[size]': '15',
            'fields[tests_choice]': 'id,question,choice_text',
            'fields[question]': 'question_text'
        })
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {'errors': [{'detail': 'no model found for resource Foo'}]})

    def test_get_no_association(self, *args, **kwargs):
        response = self.client.get(self.bad_association_url, {
            'page[number]': '1',
            'page[size]': '15',
            'fields[tests_choice]': 'id,question,choice_text',
            'fields[question]': 'question_text'
        })
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {'errors': [{'detail': 'cannot find association resource foo for Model tests_question'}]})

    def test_post(self, *args, **kwargs):
        publication = Publication.objects.get(pk=2)
        body = {
            'data': [
                {
                    'id': '1',
                    'type': 'article'
                }
            ]
        }
        self.assertEqual(publication.article_set.count(), 1)
        response = self.client.post(self.many_url,
                                    json.dumps(body),
                                    content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {})
        self.assertEqual(publication.article_set.count(), 2)

    def test_post_reverse(self, *args, **kwargs):
        article = Article.objects.get(pk=1)
        body = {
            'data': [
                {
                    'id': '2',
                    'type': 'publication'
                }
            ]
        }
        self.assertEqual(article.publications.count(), 1)
        response = self.client.post(self.many_reverse_url,
                                    json.dumps(body),
                                    content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {})
        self.assertEqual(article.publications.count(), 2)

    def test_post_no_model(self, *args, **kwargs):
        body = {
            'data': [
                {
                    'id': '1',
                    'type': 'article'
                }
            ]
        }
        response = self.client.post(self.many_bad_url,
                                    json.dumps(body),
                                    content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {'errors': [{'detail': 'no model found for resource Foo'}]})

    def test_post_related_data_do_not_exist(self, *args, **kwargs):
        body = {
            'data': [
                {
                    'id': '1',
                    'type': 'article'
                }
            ]
        }
        self.assertEqual(Restaurant.objects.count(), 1)
        response = self.client.post(self.many_bad_association_url,
                                    json.dumps(body),
                                    content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {
            'errors': [
                {
                    'detail': 'cannot find association resource foo for Model tests_publication'
                }
            ]
        })
        self.assertEqual(Restaurant.objects.count(), 1)

    def test_put(self, *args, **kwargs):
        body = {
            'data': [
                {
                    'id': '1',
                    'type': 'article'
                }
            ]
        }
        response = self.client.put(self.many_url,
                                   json.dumps(body),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 204)

    def test_delete(self, *args, **kwargs):
        data = {
            'data': [
                {
                    'id': '2',
                    'type': 'article'
                }
            ]
        }
        self.assertEqual(Article.objects.count(), 2)
        response = self.client.delete(f'{self.many_url}?delete=true',
                                      json.dumps(data),
                                      content_type='application/json')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Article.objects.count(), 1)

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    def test_delete_all_records(self, *args, **kwargs):
        data = {
            'data': {
                'attributes': {
                    'ids': [
                        {
                            'id': '1',
                            'type': 'choice'
                        }
                    ],
                    'collection_name': 'tests_choice',
                    'parent_collection_name': 'tests_question',
                    'parent_collection_id': '1',
                    'parent_association_name': 'choice_set',
                    'all_records': True,
                    'all_records_subset_query': {
                        'page[number]': 1,
                        'page[size]': 15,
                        'fields[tests_choice]': 'id,question,choice_text,foo,bar'
                    },
                    'all_records_ids_excluded': ['2'],
                    'smart_action_id': None
                },
                'type': 'action-requests'
            }
        }
        self.assertEqual(Choice.objects.count(), 3)
        response = self.client.delete(f'{self.url}?delete=true',
                                      json.dumps(data),
                                      content_type='application/json')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Choice.objects.count(), 2)

    def test_delete_all_records_no_association(self, *args, **kwargs):
        data = {
            'data': {
                'attributes': {
                    'ids': [
                        {
                            'id': '1',
                            'type': 'choice'
                        }
                    ],
                    'collection_name': 'tests_choice',
                    'parent_collection_name': 'tests_question',
                    'parent_collection_id': '1',
                    'parent_association_name': 'foo',
                    'all_records': True,
                    'all_records_subset_query': {
                        'page[number]': 1,
                        'page[size]': 15,
                        'fields[tests_choice]': 'id,question,choice_text,foo,bar'
                    },
                    'all_records_ids_excluded': ['2'],
                    'smart_action_id': None
                },
                'type': 'action-requests'
            }
        }
        response = self.client.delete(f'{self.url}?delete=true',
                                      json.dumps(data),
                                      content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data, {'errors': [{'detail': 'cannot find association resource foo for Model tests_question'}]})

    def test_delete_no_model(self, *args, **kwargs):
        data = {
            'data': [
                {
                    'id': '2',
                    'type': 'article'
                }
            ]
        }
        response = self.client.delete(self.many_bad_url,
                                      json.dumps(data),
                                      content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {'errors': [{'detail': 'no model found for resource Foo'}]})

    def test_delete_no_association(self, *args, **kwargs):
        data = {
            'data': [
                {
                    'id': '2',
                    'type': 'article'
                }
            ]
        }
        response = self.client.delete(self.many_bad_association_url,
                                      json.dumps(data),
                                      content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {'errors': [{'detail': 'cannot find association resource foo for Model tests_publication'}]})

    def test_dissociate(self, *args, **kwargs):
        publication = Publication.objects.get(pk=2)
        data = {
            'data': [
                {
                    'id': '2',
                    'type': 'article'
                }
            ]
        }
        self.assertEqual(publication.article_set.count(), 1)
        self.assertEqual(Article.objects.count(), 2)
        response = self.client.delete(self.many_url,
                                      json.dumps(data),
                                      content_type='application/json')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(publication.article_set.count(), 0)
        self.assertEqual(Article.objects.count(), 2)
