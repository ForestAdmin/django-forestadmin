import copy
import json

from django.test import TransactionTestCase
from django.urls import reverse

from django_forest.tests.fixtures.schema import test_schema
from django_forest.tests.models import Question, Restaurant, Publication, Article
from django_forest.utils.schema import Schema
from django_forest.utils.schema.json_api_schema import JsonApiSchema


class ResourceAssociationListViewTests(TransactionTestCase):
    fixtures = ['article.json', 'publication.json',
                'session.json',
                'question.json', 'choice.json',
                'place.json', 'restaurant.json']

    def setUp(self):
        Schema.schema = copy.deepcopy(test_schema)
        Schema.handle_json_api_serializer()
        self.url = reverse('resources:associations:list',
                           kwargs={'resource': 'Question', 'pk': 1, 'association_resource': 'choice_set'})
        self.reverse_url = reverse('resources:associations:list',
                           kwargs={'resource': 'Choice', 'pk': 1, 'association_resource': 'question'})
        self.bad_url = reverse('resources:associations:list',
                               kwargs={'resource': 'Foo', 'pk': 1, 'association_resource': 'choice_set'})
        self.bad_association_url = reverse('resources:associations:list',
                                           kwargs={'resource': 'Question', 'pk': 1, 'association_resource': 'foo'})

        self.many_url = reverse('resources:associations:list',
                                kwargs={'resource': 'Publication', 'pk': 2, 'association_resource': 'article_set'})
        self.many_reverse_url = reverse('resources:associations:list',
                                        kwargs={'resource': 'Article', 'pk': 1, 'association_resource': 'publications'})
        self.many_bad_url = reverse('resources:associations:list',
                                    kwargs={'resource': 'Foo', 'pk': 2, 'association_resource': 'article_set'})
        self.many_bad_association_url = reverse('resources:associations:list',
                                                kwargs={'resource': 'Publication', 'pk': 2,
                                                        'association_resource': 'foo'})

    def tearDown(self):
        # reset _registry after each test
        JsonApiSchema._registry = {}

    def test_get(self):
        response = self.client.get(self.url, {
            'page[number]': '1',
            'page[size]': '15',
            'fields[Choice]': 'id,question,choice_text',
            'fields[question]': 'question_text'
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
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
                    'id': 1,
                    'attributes': {
                        'choice_text': 'yes'
                    },
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
                    'id': 2,
                    'attributes': {
                        'choice_text': 'no'
                    },
                    'links': {
                        'self': '/forest/Choice/2'
                    }
                }
            ],
            'included': [
                {
                    'type': 'question',
                    'id': 1,
                    'attributes': {
                        'question_text': 'what is your favorite color?'
                    },
                    'links': {
                        'self': '/forest/Question/1'
                    }
                }
            ]
        })

    def test_get_no_model(self):
        response = self.client.get(self.bad_url, {
            'page[number]': '1',
            'page[size]': '15',
            'fields[Choice]': 'id,question,choice_text',
            'fields[question]': 'question_text'
        })
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {'errors': [{'detail': 'no model found for resource Foo'}]})

    def test_get_no_association(self):
        response = self.client.get(self.bad_association_url, {
            'page[number]': '1',
            'page[size]': '15',
            'fields[Choice]': 'id,question,choice_text',
            'fields[question]': 'question_text'
        })
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {'errors': [{'detail': 'cannot find association resource foo for Model Question'}]})

    def test_post(self):
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

    def test_post_reverse(self):
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

    def test_post_no_model(self):
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

    def test_post_related_data_do_not_exist(self):
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
                    'detail': 'cannot find association resource foo for Model Publication'
                }
            ]
        })
        self.assertEqual(Question.objects.count(), 2)

    def test_put(self):
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

    def test_delete(self):
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

    def test_delete_no_model(self):
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

    def test_delete_no_association(self):
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
        self.assertEqual(data, {'errors': [{'detail': 'cannot find association resource foo for Model Publication'}]})

    def test_dissociate(self):
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
