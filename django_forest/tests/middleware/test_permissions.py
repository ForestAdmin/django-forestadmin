import copy
import json
import sys

import pytest
import pytz

from datetime import datetime
from unittest import mock

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from django_forest.tests.fixtures.schema import test_schema
from django_forest.tests.middleware import mocked_permissions, mocked_config, \
    mocked_requests_permission
from django_forest.utils.middlewares import set_middlewares
from django_forest.utils.permissions import Permission
from django_forest.utils.schema import Schema
from django_forest.utils.schema.json_api_schema import JsonApiSchema
from django_forest.utils.scope import ScopeManager

mocked_permissions_scope = copy.deepcopy(mocked_permissions)
mocked_permissions_scope['data']['renderings']['1'] = {
    'tests_question': {
        'scope': {
            'filter': {
                'aggregator': 'and',
                'conditions': [
                    {
                        'field': 'question_text',
                        'operator': 'contains',
                        'value': 'what'
                    }
                ]},
            'dynamicScopesValues': {}
        }
    }
}

mocked_permissions_scope_dynamic = copy.deepcopy(mocked_permissions_scope)
mocked_permissions_scope_dynamic['data']['renderings']['1']['tests_question']['scope']['filter']['conditions'][0][
    'value'] = '$currentUser.firstName'
mocked_permissions_scope_dynamic['data']['renderings']['1']['tests_question']['scope']['dynamicScopesValues'] = {
    'users': {
        '1': {
            '$currentUser.firstName': 'Guillaume'
        }
    }
}

mocked_permissions_none = copy.deepcopy(mocked_permissions)
mocked_permissions_none['data']['collections']['tests_question']['collection']['browseEnabled'] = None

mocked_permissions_user = copy.deepcopy(mocked_permissions)
mocked_permissions_user['data']['collections']['tests_question']['collection']['browseEnabled'] = [1]

mocked_permissions_no_collection = copy.deepcopy(mocked_permissions)
del mocked_permissions_no_collection['data']['collections']['tests_question']

mocked_permissions_list_forbidden = copy.deepcopy(mocked_permissions)
mocked_permissions_list_forbidden['data']['collections']['tests_question']['collection']['browseEnabled'] = False

mocked_permissions_action = copy.deepcopy(mocked_permissions)
mocked_permissions_action['data']['collections']['tests_question']['actions'] = {
    'Send invoice': {
        'triggerEnabled': True
    }
}

mocked_permissions_stats = copy.deepcopy(mocked_permissions)
mocked_permissions_stats['stats'] = {
    'queries': ['SELECT COUNT(*) AS value, 5 as objective FROM tests_question',
                'SELECT SUM(tests_question.id) AS value FROM tests_question'],
    'leaderboards': [{'type': 'Leaderboard', 'limit': 5, 'aggregator': 'Count', 'labelFieldName': 'question_text',
                      'aggregateFieldName': None, 'sourceCollectionId': 'tests_question',
                      'relationshipFieldName': 'choice_set'}],
    'lines': [{'type': 'Line', 'filter': '{"field":"id","operator":"equal","value":0}', 'timeRange': 'Day',
               'aggregator': 'Count', 'groupByFieldName': 'pub_date', 'aggregateFieldName': None,
               'sourceCollectionId': 'tests_question'}],
    'objectives': [],
    'percentages': [{'type': 'Percentage', 'numeratorChartId': 'ffd97b70-e3b9-11eb-aaf7-0ffaf80df470',
                     'denominatorChartId': '49dd5600-e587-11eb-aaf6-e990d6816f15'}],
    'pies': [
        {'type': 'Pie', 'filter': None, 'aggregator': 'Sum', 'groupByFieldName': 'pub_date', 'aggregateFieldName': 'id',
         'sourceCollectionId': 'Question'}],
    'values': [{'type': 'Value', 'filter': '{"field":"pub_date","operator":"previous_month","value":null}',
                'aggregator': 'Sum', 'aggregateFieldName': 'id', 'sourceCollectionId': 'tests_question'}]
}

mocked_permissions_missing_stats = copy.deepcopy(mocked_permissions)
mocked_permissions_missing_stats['stats'] = {}

mocked_config_bad_request = copy.deepcopy(mocked_config)
mocked_config_bad_request['permissions'] = {
    'data': {},
    'status': 400
}
mocked_config_no_collection = copy.deepcopy(mocked_config)
mocked_config_no_collection['permissions']['data'] = mocked_permissions_no_collection
mocked_config_none = copy.deepcopy(mocked_config)
mocked_config_none['permissions']['data'] = mocked_permissions_none
mocked_config_user = copy.deepcopy(mocked_config)
mocked_config_user['permissions']['data'] = mocked_permissions_user
mocked_config_list_forbidden = copy.deepcopy(mocked_config)
mocked_config_list_forbidden['permissions']['data'] = mocked_permissions_list_forbidden
mocked_config_action = copy.deepcopy(mocked_config)
mocked_config_action['permissions']['data'] = mocked_permissions_action
mocked_config_stats = copy.deepcopy(mocked_config)
mocked_config_stats['permissions']['data'] = mocked_permissions_stats
mocked_config_missing_stats = copy.deepcopy(mocked_config)
mocked_config_missing_stats['permissions']['data'] = mocked_permissions_missing_stats


class MiddlewarePermissionsNoTokenTests(TestCase):

    def setUp(self):
        set_middlewares()
        Schema.schema = copy.deepcopy(test_schema)
        Schema.handle_json_api_schema()
        self.url = reverse('django_forest:resources:list', kwargs={'resource': 'tests_question'})

    def tearDown(self):
        # reset _registry after each test
        JsonApiSchema._registry = {}
        Permission.permissions_cached = {}
        Permission.renderings_cached = {}
        ScopeManager.cache = {}
        settings.MIDDLEWARE.remove('django_forest.middleware.PermissionMiddleware')
        settings.MIDDLEWARE.remove('django_forest.middleware.IpWhitelistMiddleware')

    def test_list(self):
        response = self.client.get(self.url, {
            'page[number]': '1',
            'page[size]': '15'
        })
        self.assertEqual(response.status_code, 403)


class MiddlewarePermissionsTests(TestCase):

    def setUp(self):
        set_middlewares()
        Schema.schema = copy.deepcopy(test_schema)
        Schema.handle_json_api_schema()
        self.url = reverse('django_forest:resources:list', kwargs={'resource': 'tests_question'})
        self.client = self.client_class(
            HTTP_AUTHORIZATION='Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjUiLCJlbWFpbCI6Imd1aWxsYXVtZWNAZm9yZXN0YWRtaW4uY29tIiwiZmlyc3RfbmFtZSI6Ikd1aWxsYXVtZSIsImxhc3RfbmFtZSI6IkNpc2NvIiwidGVhbSI6Ik9wZXJhdGlvbnMiLCJyZW5kZXJpbmdfaWQiOjEsImV4cCI6MTYyNTY3OTYyNi44ODYwMTh9.mHjA05yvMr99gFMuFv0SnPDCeOd2ZyMSN868V7lsjnw')

    def tearDown(self):
        # reset _registry after each test
        JsonApiSchema._registry = {}
        Permission.permissions_cached = {}
        Permission.renderings_cached = {}
        ScopeManager.cache = {}
        settings.MIDDLEWARE.remove('django_forest.middleware.PermissionMiddleware')
        settings.MIDDLEWARE.remove('django_forest.middleware.IpWhitelistMiddleware')

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @mock.patch('django_forest.utils.permissions.datetime')
    @mock.patch('requests.get', side_effect=mocked_requests_permission(mocked_config))
    def test_list(self, mocked_requests, mocked_datetime, mocked_decode):
        mocked_datetime.now.return_value = datetime(2021, 7, 8, 9, 20, 22, 582772, tzinfo=pytz.UTC)
        response = self.client.get(self.url, {
            'page[number]': '1',
            'page[size]': '15',
        })
        self.assertEqual(response.status_code, 200)

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @mock.patch('django_forest.utils.permissions.datetime')
    @mock.patch('requests.get', side_effect=mocked_requests_permission(mocked_config_bad_request))
    def test_list_error_server(self, mocked_requests, mocked_datetime, mocked_decode):
        mocked_datetime.now.return_value = datetime(2021, 7, 8, 9, 20, 22, 582772, tzinfo=pytz.UTC)
        response = self.client.get(self.url, {
            'page[number]': '1',
            'page[size]': '15',
        })
        self.assertEqual(response.status_code, 403)

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @mock.patch('django_forest.utils.permissions.datetime')
    @mock.patch('requests.get', side_effect=mocked_requests_permission(mocked_config_no_collection))
    def test_list_no_collection(self, mocked_requests, mocked_datetime, mocked_decode):
        mocked_datetime.now.return_value = datetime(2021, 7, 8, 9, 20, 22, 582772, tzinfo=pytz.UTC)
        response = self.client.get(self.url, {
            'page[number]': '1',
            'page[size]': '15'
        })
        self.assertEqual(response.status_code, 403)

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @mock.patch('django_forest.utils.permissions.datetime')
    @mock.patch('requests.get', side_effect=mocked_requests_permission(mocked_config_none))
    def test_list_none(self, mocked_requests, mocked_datetime, mocked_decode):
        mocked_datetime.now.return_value = datetime(2021, 7, 8, 9, 20, 22, 582772, tzinfo=pytz.UTC)
        response = self.client.get(self.url, {
            'page[number]': '1',
            'page[size]': '15'
        })
        self.assertEqual(response.status_code, 403)

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @mock.patch('django_forest.utils.permissions.datetime')
    @mock.patch('requests.get', side_effect=mocked_requests_permission(mocked_config_user))
    def test_list_user(self, mocked_requests, mocked_datetime, mocked_decode):
        mocked_datetime.now.return_value = datetime(2021, 7, 8, 9, 20, 22, 582772, tzinfo=pytz.UTC)
        response = self.client.get(self.url, {
            'page[number]': '1',
            'page[size]': '15'
        })
        self.assertEqual(response.status_code, 200)

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @mock.patch('django_forest.utils.permissions.datetime')
    @mock.patch('requests.get', side_effect=mocked_requests_permission(mocked_config_list_forbidden))
    def test_list_forbidden(self, mocked_requests, mocked_datetime, mocked_decode):
        mocked_datetime.now.return_value = datetime(2021, 7, 8, 9, 20, 22, 582772, tzinfo=pytz.UTC)
        response = self.client.get(self.url, {
            'page[number]': '1',
            'page[size]': '15'
        })
        self.assertEqual(response.status_code, 403)


class MiddlewarePermissionsCookieTests(TestCase):

    def setUp(self):
        set_middlewares()
        Schema.schema = copy.deepcopy(test_schema)
        Schema.handle_json_api_schema()
        self.url = reverse('django_forest:resources:list', kwargs={'resource': 'tests_question'})
        self.client = self.client_class(
            HTTP_COOKIE='forest_session_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjUiLCJlbWFpbCI6Imd1aWxsYXVtZWNAZm9yZXN0YWRtaW4uY29tIiwiZmlyc3RfbmFtZSI6Ikd1aWxsYXVtZSIsImxhc3RfbmFtZSI6IkNpc2NvIiwidGVhbSI6Ik9wZXJhdGlvbnMiLCJyZW5kZXJpbmdfaWQiOjEsImV4cCI6MTYyNTY3OTYyNi44ODYwMTh9.mHjA05yvMr99gFMuFv0SnPDCeOd2ZyMSN868V7lsjnw')

    def tearDown(self):
        # reset _registry after each test
        JsonApiSchema._registry = {}
        Permission.permissions_cached = {}
        Permission.renderings_cached = {}
        ScopeManager.cache = {}
        settings.MIDDLEWARE.remove('django_forest.middleware.PermissionMiddleware')
        settings.MIDDLEWARE.remove('django_forest.middleware.IpWhitelistMiddleware')

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @mock.patch('django_forest.utils.permissions.datetime')
    @mock.patch('requests.get', side_effect=mocked_requests_permission(mocked_config))
    def test_list(self, mocked_requests, mocked_datetime, mocked_decode):
        mocked_datetime.now.return_value = datetime(2021, 7, 8, 9, 20, 22, 582772, tzinfo=pytz.UTC)
        response = self.client.get(self.url, {
            'page[number]': '1',
            'page[size]': '15'
        })
        self.assertEqual(response.status_code, 200)


class MiddlewarePermissionsCachedTests(TestCase):

    def setUp(self):
        set_middlewares()
        Schema.schema = copy.deepcopy(test_schema)
        Schema.handle_json_api_schema()
        self.url = reverse('django_forest:resources:list', kwargs={'resource': 'tests_question'})
        self.client = self.client_class(
            HTTP_AUTHORIZATION='Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjUiLCJlbWFpbCI6Imd1aWxsYXVtZWNAZm9yZXN0YWRtaW4uY29tIiwiZmlyc3RfbmFtZSI6Ikd1aWxsYXVtZSIsImxhc3RfbmFtZSI6IkNpc2NvIiwidGVhbSI6Ik9wZXJhdGlvbnMiLCJyZW5kZXJpbmdfaWQiOjEsImV4cCI6MTYyNTY3OTYyNi44ODYwMTh9.mHjA05yvMr99gFMuFv0SnPDCeOd2ZyMSN868V7lsjnw')
        Permission.roles_acl_activated = True
        Permission.permissions_cached = {
            'data': {
                'collections': {
                    'tests_question': {
                        'collection': {
                            'browseEnabled': True,
                            'readEnabled': True,
                            'addEnabled': True,
                            'editEnabled': True,
                            'deleteEnabled': True,
                            'exportEnabled': True
                        },
                        'actions': {}
                    }
                },
                'renderings': {
                    '1': {
                        'stats': {
                            'queries': [],
                            'leaderboards': [],
                            'lines': [],
                            'objectives': [],
                            'percentages': [],
                            'pies': [],
                            'values': []
                        },
                        'last_fetch': datetime(2021, 7, 8, 9, 20, 22, 582772, tzinfo=pytz.UTC)
                    }
                }
            },
            'stats': {
                'queries': [],
                'leaderboards': [],
                'lines': [],
                'objectives': [],
                'percentages': [],
                'pies': [],
                'values': []
            },
            'meta': {
                'rolesACLActivated': True
            },
            'last_fetch': datetime(2021, 7, 8, 9, 20, 22, 582772, tzinfo=pytz.UTC)
        }
        Permission.renderings_cached = {
            '1': {
                'stats': {
                    'queries': [],
                    'leaderboards': [],
                    'lines': [],
                    'objectives': [],
                    'percentages': [],
                    'pies': [],
                    'values': []
                },
                'last_fetch': datetime(2021, 7, 8, 9, 20, 22, 582772, tzinfo=pytz.UTC)
            }
        }

    def tearDown(self):
        # reset _registry after each test
        JsonApiSchema._registry = {}
        Permission.permissions_cached = {}
        Permission.renderings_cached = {}
        ScopeManager.cache = {}
        settings.MIDDLEWARE.remove('django_forest.middleware.PermissionMiddleware')
        settings.MIDDLEWARE.remove('django_forest.middleware.IpWhitelistMiddleware')

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @mock.patch('django_forest.utils.permissions.datetime')
    @mock.patch('requests.get', side_effect=mocked_requests_permission(mocked_config))
    @mock.patch('django_forest.utils.permissions.Permission.fetch_permissions')
    def test_list_once_again(self, mocked_fetch_permissions, mocked_requests, mocked_datetime, mocked_decode):
        mocked_datetime.now.return_value = datetime(2021, 7, 8, 9, 20, 22, 582772, tzinfo=pytz.UTC)
        response = self.client.get(self.url, {
            'page[number]': '1',
            'page[size]': '15'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(mocked_fetch_permissions.called)

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @mock.patch('django_forest.utils.permissions.datetime')
    @mock.patch('requests.get', side_effect=mocked_requests_permission(mocked_config))
    @mock.patch('django_forest.utils.permissions.Permission.fetch_permissions')
    def test_list_no_last_fetch_renderings_cached(self, mocked_fetch_permissions, mocked_requests, mocked_datetime,
                                                  mocked_decode):
        mocked_datetime.now.return_value = datetime(2021, 7, 8, 9, 20, 22, 582772, tzinfo=pytz.UTC)
        del Permission.renderings_cached['1']['last_fetch']
        response = self.client.get(self.url, {
            'page[number]': '1',
            'page[size]': '15'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(mocked_fetch_permissions.called)


# reset forest config dir auto import
@pytest.fixture()
def reset_config_dir_import():
    for key in list(sys.modules.keys()):
        if key.startswith('django_forest.tests.forest'):
            del sys.modules[key]


@pytest.mark.usefixtures('reset_config_dir_import')
class MiddlewarePermissionsActionsTests(TestCase):

    def setUp(self):
        set_middlewares()
        Schema.schema = copy.deepcopy(test_schema)
        Schema.add_smart_features()
        Schema.handle_json_api_schema()
        self.url = reverse('actions:send-invoice')
        self.client = self.client_class(
            HTTP_AUTHORIZATION='Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjUiLCJlbWFpbCI6Imd1aWxsYXVtZWNAZm9yZXN0YWRtaW4uY29tIiwiZmlyc3RfbmFtZSI6Ikd1aWxsYXVtZSIsImxhc3RfbmFtZSI6IkNpc2NvIiwidGVhbSI6Ik9wZXJhdGlvbnMiLCJyZW5kZXJpbmdfaWQiOjEsImV4cCI6MTYyNTY3OTYyNi44ODYwMTh9.mHjA05yvMr99gFMuFv0SnPDCeOd2ZyMSN868V7lsjnw')
        self.body = {
            'data': {
                'attributes': {
                    'collection_name': 'tests_question',
                    'values': {},
                    'ids': [
                        '1'
                    ],
                    'parent_collection_name': None,
                    'parent_collection_id': None,
                    'parent_association_name': None,
                    'all_records': False,
                    'all_records_subset_query': {
                        'fields[pollstests_question]': 'id,pubDate,questionText',
                        'fields[subject]': 'name',
                        'fields[subject2]': 'name',
                        'fields[topic]': 'name',
                        'page[number]': 1,
                        'page[size]': 15,
                        'sort': '-id',
                        'searchExtended': 0,
                        'timezone': 'Europe/Paris'
                    },
                    'all_records_ids_excluded': [
                        '2',
                        '3'
                    ],
                    'smart_action_id': 'tests_question-Send@@@Invoice@@@'
                },
                'type': 'custom-action-requests'
            }
        }

    def tearDown(self):
        # reset _registry after each test
        JsonApiSchema._registry = {}
        Permission.permissions_cached = {}
        Permission.renderings_cached = {}
        ScopeManager.cache = {}
        settings.MIDDLEWARE.remove('django_forest.middleware.PermissionMiddleware')
        settings.MIDDLEWARE.remove('django_forest.middleware.IpWhitelistMiddleware')

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @mock.patch('django_forest.utils.permissions.datetime')
    @mock.patch('requests.get', side_effect=mocked_requests_permission(mocked_config_action))
    def test_actions(self, mocked_requests, mocked_datetime, mocked_decode):
        mocked_datetime.now.return_value = datetime(2021, 7, 8, 9, 20, 22, 582772, tzinfo=pytz.UTC)
        response = self.client.post(self.url, json.dumps(self.body), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data, {'success': 'now live'})

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @mock.patch('django_forest.utils.permissions.datetime')
    @mock.patch('requests.get', side_effect=mocked_requests_permission(mocked_config_action))
    def test_actions_not_exist(self, mocked_requests, mocked_datetime, mocked_decode):
        url = reverse('actions:not-exists')
        mocked_datetime.now.return_value = datetime(2021, 7, 8, 9, 20, 22, 582772, tzinfo=pytz.UTC)
        response = self.client.post(url, json.dumps(self.body), content_type='application/json')
        self.assertEqual(response.status_code, 403)

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @mock.patch('django_forest.utils.permissions.datetime')
    @mock.patch('requests.get', side_effect=mocked_requests_permission(mocked_config_action))
    def test_actions_no_resource(self, mocked_requests, mocked_datetime, mocked_decode):
        mocked_datetime.now.return_value = datetime(2021, 7, 8, 9, 20, 22, 582772, tzinfo=pytz.UTC)
        body = copy.deepcopy(self.body)
        body['data']['attributes']['collection_name'] = 'Foo'
        response = self.client.post(self.url, json.dumps(body), content_type='application/json')
        self.assertEqual(response.status_code, 400)


class MiddlewarePermissionsStatsTests(TestCase):

    def setUp(self):
        set_middlewares()
        Schema.schema = copy.deepcopy(test_schema)
        Schema.handle_json_api_schema()
        self.live_queries_url = f"{reverse('django_forest:stats:liveQueries')}?timezone=Europe%2FParis"
        self.stats_with_parameters_url = f"{reverse('django_forest:stats:statsWithParameters', kwargs={'resource': 'tests_question'})}?timezone=Europe%2FParis"
        self.client = self.client_class(
            HTTP_AUTHORIZATION='Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjUiLCJlbWFpbCI6Imd1aWxsYXVtZWNAZm9yZXN0YWRtaW4uY29tIiwiZmlyc3RfbmFtZSI6Ikd1aWxsYXVtZSIsImxhc3RfbmFtZSI6IkNpc2NvIiwidGVhbSI6Ik9wZXJhdGlvbnMiLCJyZW5kZXJpbmdfaWQiOjEsImV4cCI6MTYyNTY3OTYyNi44ODYwMTh9.mHjA05yvMr99gFMuFv0SnPDCeOd2ZyMSN868V7lsjnw')
        self.live_queries_body = {
            'type': 'Objective',
            'timezone': 'Europe/Paris',
            'query': 'SELECT COUNT(*) AS value, 5 as objective FROM tests_question'
        }
        self.stats_with_parameters_body = {
            'type': 'Leaderboard',
            'collection': 'tests_question',
            'timezone': 'Europe/Paris',
            'label_field': 'question_text',
            'relationship_field': 'choice_set',
            'limit': 5,
            'aggregate': 'Count'
        }

    def tearDown(self):
        # reset _registry after each test
        JsonApiSchema._registry = {}
        Permission.permissions_cached = {}
        Permission.renderings_cached = {}
        ScopeManager.cache = {}
        settings.MIDDLEWARE.remove('django_forest.middleware.PermissionMiddleware')

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @mock.patch('django_forest.utils.permissions.datetime')
    @mock.patch('requests.get', side_effect=mocked_requests_permission(mocked_config_stats))
    def test_live_queries(self, mocked_requests, mocked_datetime, mocked_decode):
        mocked_datetime.now.return_value = datetime(2021, 7, 8, 9, 20, 22, 582772, tzinfo=pytz.UTC)
        response = self.client.post(self.live_queries_url, json.dumps(self.live_queries_body),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @mock.patch('django_forest.utils.permissions.datetime')
    @mock.patch('requests.get', side_effect=mocked_requests_permission(mocked_config_stats))
    def test_live_queries_forbidden(self, mocked_requests, mocked_datetime, mocked_decode):
        mocked_datetime.now.return_value = datetime(2021, 7, 8, 9, 20, 22, 582772, tzinfo=pytz.UTC)
        live_queries_body = {
            'type': 'Objective',
            'timezone': 'Europe/Paris',
            'query': 'SELECT COUNT(*) AS value, 0 as objective FROM tests_question'
        }

        response = self.client.post(self.live_queries_url, json.dumps(live_queries_body),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 403)

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @mock.patch('django_forest.utils.permissions.datetime')
    @mock.patch('requests.get', side_effect=mocked_requests_permission(mocked_config_missing_stats))
    def test_live_queries_missing_stats(self, mocked_requests, mocked_datetime, mocked_decode):
        mocked_datetime.now.return_value = datetime(2021, 7, 8, 9, 20, 22, 582772, tzinfo=pytz.UTC)
        response = self.client.post(self.live_queries_url, json.dumps(self.live_queries_body),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 403)

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @mock.patch('django_forest.utils.permissions.datetime')
    @mock.patch('requests.get', side_effect=mocked_requests_permission(mocked_config_stats))
    def test_stats_with_parameters(self, mocked_requests, mocked_datetime, mocked_decode):
        mocked_datetime.now.return_value = datetime(2021, 7, 8, 9, 20, 22, 582772, tzinfo=pytz.UTC)
        response = self.client.post(self.stats_with_parameters_url, json.dumps(self.stats_with_parameters_body),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @mock.patch('django_forest.utils.permissions.datetime')
    @mock.patch('requests.get', side_effect=mocked_requests_permission(mocked_config_stats))
    def test_stats_with_parameters_forbidden(self, mocked_requests, mocked_datetime, mocked_decode):
        mocked_datetime.now.return_value = datetime(2021, 7, 8, 9, 20, 22, 582772, tzinfo=pytz.UTC)
        stats_with_parameters_body = {
            'type': 'Value',
            'aggregator': 'Count',
            'sourceCollectionId': 'tests_question',
            'timezone': 'Europe/Paris'
        }
        response = self.client.post(self.stats_with_parameters_url, json.dumps(stats_with_parameters_body),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 403)

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @mock.patch('django_forest.utils.permissions.datetime')
    @mock.patch('requests.get', side_effect=mocked_requests_permission(mocked_config_missing_stats))
    def test_stats_with_parameters_missing_stats(self, mocked_requests, mocked_datetime, mocked_decode):
        mocked_datetime.now.return_value = datetime(2021, 7, 8, 9, 20, 22, 582772, tzinfo=pytz.UTC)
        response = self.client.post(self.stats_with_parameters_url, json.dumps(self.stats_with_parameters_body),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 403)
