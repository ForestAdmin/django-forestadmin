import copy
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

mocked_config_list_forbidden = copy.deepcopy(mocked_config)
mocked_config_list_forbidden['data']['collections']['Question']['collection']['browseEnabled'] = False


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
    @mock.patch('requests.get', return_value=mocked_requests(mocked_config, 200))
    def test_list(self, mocked_requests, mocked_decode, mocked_app_name):
        response = self.client.get(self.url, {
            'page[number]': '1',
            'page[size]': '15'
        })
        self.assertEqual(response.status_code, 200)

    @mock.patch('middleware.PermissionMiddleware.get_app_name', return_value='django_forest:resources')
    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @mock.patch('requests.get', return_value=mocked_requests(mocked_config_list_forbidden, 200))
    def test_list_forbidden(self, mocked_requests, mocked_decode, mocked_app_name):

        response = self.client.get(self.url, {
            'page[number]': '1',
            'page[size]': '15'
        })
        self.assertEqual(response.status_code, 403)
