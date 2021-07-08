import copy
import pytz

from datetime import datetime
from unittest import mock

from django.test import TestCase
from django.urls import reverse

from django_forest.tests.fixtures.schema import test_schema
from django_forest.utils.middlewares import set_middlewares
from django_forest.utils.permissions import Permission
from django_forest.utils.schema import Schema
from django_forest.utils.schema.json_api_schema import JsonApiSchema
from django_forest.tests.utils.test_forest_api_requester import mocked_requests

mocked_config = {
    'data': {
        'collections': {
            'Question': {
                'collection': {
                    'browseEnabled': True,
                    'readEnabled': True,
                    'addEnabled': True,
                    'editEnabled': True,
                    'deleteEnabled': True,
                    'exportEnabled': True
                },
                'actions': {}
            },
        },
        'renderings': {
            '1': {}
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
    }
}

mocked_config_scope = copy.deepcopy(mocked_config)
mocked_config_scope['data']['renderings']['1'] = {
    'Question': {
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

mocked_config_none = copy.deepcopy(mocked_config)
mocked_config_none['data']['collections']['Question']['collection']['browseEnabled'] = None

mocked_config_user = copy.deepcopy(mocked_config)
mocked_config_user['data']['collections']['Question']['collection']['browseEnabled'] = [1]

mocked_config_no_collection = copy.deepcopy(mocked_config)
del mocked_config_no_collection['data']['collections']['Question']

mocked_config_list_forbidden = copy.deepcopy(mocked_config)
mocked_config_list_forbidden['data']['collections']['Question']['collection']['browseEnabled'] = False

mocked_config_list_no_role_acl = {
    'data': {
        'Question': {
            'collection': {
                'list': True,
                'show': True,
                'create': True,
                'update': True,
                'delete': True,
                'export': True
            },
            'actions': {},
            'scope': ''
        },
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
        'rolesACLActivated': False
    }
}


class MiddlewarePermissionsNoTokenTests(TestCase):

    def setUp(self):
        set_middlewares()
        Schema.schema = copy.deepcopy(test_schema)
        Schema.handle_json_api_schema()
        self.url = reverse('resources:list', kwargs={'resource': 'Question'})

    def tearDown(self):
        # reset _registry after each test
        JsonApiSchema._registry = {}
        Permission.permissions_cached = {}
        Permission.renderings_cached = {}

    @mock.patch('middleware.PermissionMiddleware.get_app_name', return_value='django_forest:resources')
    def test_list(self, mocked_app_name):
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
        self.url = reverse('resources:list', kwargs={'resource': 'Question'})
        self.client = self.client_class(
            HTTP_AUTHORIZATION='Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjUiLCJlbWFpbCI6Imd1aWxsYXVtZWNAZm9yZXN0YWRtaW4uY29tIiwiZmlyc3RfbmFtZSI6Ikd1aWxsYXVtZSIsImxhc3RfbmFtZSI6IkNpc2NvIiwidGVhbSI6Ik9wZXJhdGlvbnMiLCJyZW5kZXJpbmdfaWQiOjEsImV4cCI6MTYyNTY3OTYyNi44ODYwMTh9.mHjA05yvMr99gFMuFv0SnPDCeOd2ZyMSN868V7lsjnw')

    def tearDown(self):
        # reset _registry after each test
        JsonApiSchema._registry = {}
        Permission.permissions_cached = {}
        Permission.renderings_cached = {}

    @mock.patch('middleware.PermissionMiddleware.get_app_name', return_value='django_forest:resources')
    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @mock.patch('django_forest.utils.permissions.datetime')
    @mock.patch('requests.get', return_value=mocked_requests(mocked_config, 200))
    def test_list(self, mocked_requests, mocked_datetime, mocked_decode, mocked_app_name):
        mocked_datetime.now.return_value = datetime(2021, 7, 8, 9, 20, 22, 582772, tzinfo=pytz.UTC)
        response = self.client.get(self.url, {
            'page[number]': '1',
            'page[size]': '15',
        })
        self.assertEqual(response.status_code, 200)

    @mock.patch('middleware.PermissionMiddleware.get_app_name', return_value='django_forest:resources')
    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @mock.patch('django_forest.utils.permissions.datetime')
    @mock.patch('requests.get', return_value=mocked_requests(mocked_config_scope, 200))
    def test_list_scope(self, mocked_requests, mocked_datetime, mocked_decode, mocked_app_name):
        mocked_datetime.now.return_value = datetime(2021, 7, 8, 9, 20, 22, 582772, tzinfo=pytz.UTC)
        response = self.client.get(self.url, {
            'page[number]': '1',
            'page[size]': '15',
            'filters': '{"field":"question_text","operator":"contains","value":"what"}'
        })
        self.assertEqual(response.status_code, 200)

    @mock.patch('middleware.PermissionMiddleware.get_app_name', return_value='django_forest:resources')
    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @mock.patch('django_forest.utils.permissions.datetime')
    @mock.patch('requests.get', return_value=mocked_requests(mocked_config_no_collection, 200))
    def test_list_no_collection(self, mocked_requests, mocked_datetime, mocked_decode, mocked_app_name):
        mocked_datetime.now.return_value = datetime(2021, 7, 8, 9, 20, 22, 582772, tzinfo=pytz.UTC)
        response = self.client.get(self.url, {
            'page[number]': '1',
            'page[size]': '15'
        })
        self.assertEqual(response.status_code, 403)

    @mock.patch('middleware.PermissionMiddleware.get_app_name', return_value='django_forest:resources')
    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @mock.patch('django_forest.utils.permissions.datetime')
    @mock.patch('requests.get', return_value=mocked_requests(mocked_config_none, 200))
    def test_list_none(self, mocked_requests, mocked_datetime, mocked_decode, mocked_app_name):
        mocked_datetime.now.return_value = datetime(2021, 7, 8, 9, 20, 22, 582772, tzinfo=pytz.UTC)
        response = self.client.get(self.url, {
            'page[number]': '1',
            'page[size]': '15'
        })
        self.assertEqual(response.status_code, 403)

    @mock.patch('middleware.PermissionMiddleware.get_app_name', return_value='django_forest:resources')
    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @mock.patch('django_forest.utils.permissions.datetime')
    @mock.patch('requests.get', return_value=mocked_requests(mocked_config_user, 200))
    def test_list_user(self, mocked_requests, mocked_datetime, mocked_decode, mocked_app_name):
        mocked_datetime.now.return_value = datetime(2021, 7, 8, 9, 20, 22, 582772, tzinfo=pytz.UTC)
        response = self.client.get(self.url, {
            'page[number]': '1',
            'page[size]': '15'
        })
        self.assertEqual(response.status_code, 200)

    @mock.patch('middleware.PermissionMiddleware.get_app_name', return_value='django_forest:resources')
    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @mock.patch('django_forest.utils.permissions.datetime')
    @mock.patch('requests.get', return_value=mocked_requests(mocked_config_list_forbidden, 200))
    def test_list_forbidden(self, mocked_requests, mocked_datetime, mocked_decode, mocked_app_name):
        mocked_datetime.now.return_value = datetime(2021, 7, 8, 9, 20, 22, 582772, tzinfo=pytz.UTC)
        response = self.client.get(self.url, {
            'page[number]': '1',
            'page[size]': '15'
        })
        self.assertEqual(response.status_code, 403)


class MiddlewareCookiePermissionsTests(TestCase):

    def setUp(self):
        set_middlewares()
        Schema.schema = copy.deepcopy(test_schema)
        Schema.handle_json_api_schema()
        self.url = reverse('resources:list', kwargs={'resource': 'Question'})
        self.client = self.client_class(
            HTTP_COOKIE='forest_session_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjUiLCJlbWFpbCI6Imd1aWxsYXVtZWNAZm9yZXN0YWRtaW4uY29tIiwiZmlyc3RfbmFtZSI6Ikd1aWxsYXVtZSIsImxhc3RfbmFtZSI6IkNpc2NvIiwidGVhbSI6Ik9wZXJhdGlvbnMiLCJyZW5kZXJpbmdfaWQiOjEsImV4cCI6MTYyNTY3OTYyNi44ODYwMTh9.mHjA05yvMr99gFMuFv0SnPDCeOd2ZyMSN868V7lsjnw')

    def tearDown(self):
        # reset _registry after each test
        JsonApiSchema._registry = {}
        Permission.permissions_cached = {}
        Permission.renderings_cached = {}

    @mock.patch('middleware.PermissionMiddleware.get_app_name', return_value='django_forest:resources')
    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @mock.patch('django_forest.utils.permissions.datetime')
    @mock.patch('requests.get', return_value=mocked_requests(mocked_config, 200))
    def test_list(self, mocked_requests, mocked_datetime, mocked_decode, mocked_app_name):
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
        self.url = reverse('resources:list', kwargs={'resource': 'Question'})
        self.client = self.client_class(
            HTTP_AUTHORIZATION='Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjUiLCJlbWFpbCI6Imd1aWxsYXVtZWNAZm9yZXN0YWRtaW4uY29tIiwiZmlyc3RfbmFtZSI6Ikd1aWxsYXVtZSIsImxhc3RfbmFtZSI6IkNpc2NvIiwidGVhbSI6Ik9wZXJhdGlvbnMiLCJyZW5kZXJpbmdfaWQiOjEsImV4cCI6MTYyNTY3OTYyNi44ODYwMTh9.mHjA05yvMr99gFMuFv0SnPDCeOd2ZyMSN868V7lsjnw')
        Permission.roles_acl_activated = True
        Permission.permissions_cached = {
            'data': {
                'collections': {
                    'Question': {
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

    @mock.patch('middleware.PermissionMiddleware.get_app_name', return_value='django_forest:resources')
    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @mock.patch('django_forest.utils.permissions.datetime')
    @mock.patch('requests.get', return_value=mocked_requests(mocked_config, 200))
    @mock.patch('django_forest.utils.permissions.Permission.fetch_permissions')
    def test_list_once_again(self, mocked_fetch_permissions, mocked_requests, mocked_datetime, mocked_decode,
                             mocked_app_name):
        mocked_datetime.now.return_value = datetime(2021, 7, 8, 9, 20, 22, 582772, tzinfo=pytz.UTC)
        response = self.client.get(self.url, {
            'page[number]': '1',
            'page[size]': '15'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(mocked_fetch_permissions.called)

    @mock.patch('middleware.PermissionMiddleware.get_app_name', return_value='django_forest:resources')
    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @mock.patch('django_forest.utils.permissions.datetime')
    @mock.patch('requests.get', return_value=mocked_requests(mocked_config, 200))
    @mock.patch('django_forest.utils.permissions.Permission.fetch_permissions')
    def test_list_no_last_fetch_renderings_cached(self, mocked_fetch_permissions, mocked_requests, mocked_datetime,
                                                  mocked_decode,
                                                  mocked_app_name):
        mocked_datetime.now.return_value = datetime(2021, 7, 8, 9, 20, 22, 582772, tzinfo=pytz.UTC)
        Permission.renderings_cached['1']['last_fetch'] = None
        response = self.client.get(self.url, {
            'page[number]': '1',
            'page[size]': '15'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(mocked_fetch_permissions.called)


class MiddlewareNoRolesAclTests(TestCase):

    def setUp(self):
        set_middlewares()
        Schema.schema = copy.deepcopy(test_schema)
        Schema.handle_json_api_schema()
        self.url = reverse('resources:list', kwargs={'resource': 'Question'})
        self.client = self.client_class(
            HTTP_AUTHORIZATION='Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjUiLCJlbWFpbCI6Imd1aWxsYXVtZWNAZm9yZXN0YWRtaW4uY29tIiwiZmlyc3RfbmFtZSI6Ikd1aWxsYXVtZSIsImxhc3RfbmFtZSI6IkNpc2NvIiwidGVhbSI6Ik9wZXJhdGlvbnMiLCJyZW5kZXJpbmdfaWQiOjEsImV4cCI6MTYyNTY3OTYyNi44ODYwMTh9.mHjA05yvMr99gFMuFv0SnPDCeOd2ZyMSN868V7lsjnw')

    def tearDown(self):
        # reset _registry after each test
        JsonApiSchema._registry = {}
        Permission.permissions_cached = {}
        Permission.renderings_cached = {}

    @mock.patch('middleware.PermissionMiddleware.get_app_name', return_value='django_forest:resources')
    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @mock.patch('django_forest.utils.permissions.datetime')
    @mock.patch('requests.get', return_value=mocked_requests(mocked_config_list_no_role_acl, 200))
    def test_list_no_role_acl(self, mocked_requests, mocked_datetime, mocked_decode, mocked_app_name):
        mocked_datetime.now.return_value = datetime(2021, 7, 8, 9, 20, 22, 582772, tzinfo=pytz.UTC)
        response = self.client.get(self.url, {
            'page[number]': '1',
            'page[size]': '15'
        })
        self.assertEqual(response.status_code, 200)

    @mock.patch('middleware.PermissionMiddleware.get_app_name', return_value='django_forest:resources')
    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @mock.patch('django_forest.utils.permissions.datetime')
    @mock.patch('requests.get', return_value=mocked_requests(mocked_config_list_no_role_acl, 200))
    def test_list_no_role_acl_permissions_cached(self, mocked_requests, mocked_datetime, mocked_decode,
                                                 mocked_app_name):
        mocked_datetime.now.return_value = datetime(2021, 7, 8, 9, 20, 22, 582772, tzinfo=pytz.UTC)
        Permission.roles_acl_activated = False
        Permission.permissions_cached = {
            '1': {
                'data': {
                    'collections': {
                        'Question': {
                            'collection': {
                                'browseEnabled': True,
                                'readEnabled': True,
                                'addEnabled': True,
                                'editEnabled': True,
                                'deleteEnabled': True,
                                'exportEnabled': True
                            },
                            'actions': None
                        }
                    },
                    'renderings': {
                        '1': {
                            'Question': {
                                'scope': ''
                            }
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
                    'rolesACLActivated': False
                },
                'last_fetch': datetime(2021, 7, 8, 9, 19, 22, 582772, tzinfo=pytz.UTC)
            }
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
                'last_fetch': datetime(2021, 7, 8, 9, 19, 22, 582772, tzinfo=pytz.UTC)
            }
        }
        response = self.client.get(self.url, {
            'page[number]': '1',
            'page[size]': '15'
        })
        self.assertEqual(response.status_code, 200)
