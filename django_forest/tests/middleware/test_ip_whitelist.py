import copy
from unittest import mock

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from django_forest.tests.fixtures.schema import test_schema
from django_forest.tests.middleware import mocked_ip_whitelist, mocked_config, \
    mocked_requests_permission
from django_forest.utils.ip_whitelist import IpWhitelist
from django_forest.utils.middlewares import set_middlewares
from django_forest.utils.permissions import Permission
from django_forest.utils.schema import Schema
from django_forest.utils.schema.json_api_schema import JsonApiSchema
from django_forest.utils.scope import ScopeManager


mocked_ip_whitelist_ip = copy.deepcopy(mocked_ip_whitelist)
mocked_ip_whitelist_ip['data']['attributes']['use_ip_whitelist'] = True
mocked_ip_whitelist_ip['data']['attributes']['rules'] = [
    {
        'type': 0,
        'ip': '123.12.34.0'
    }
]
mocked_ip_whitelist_ip_loopback = copy.deepcopy(mocked_ip_whitelist)
mocked_ip_whitelist_ip_loopback['data']['attributes']['use_ip_whitelist'] = True
mocked_ip_whitelist_ip_loopback['data']['attributes']['rules'] = [
    {
        'type': 0,
        'ip': '127.0.0.1'
    }
]
mocked_ip_whitelist_range = copy.deepcopy(mocked_ip_whitelist)
mocked_ip_whitelist_range['data']['attributes']['use_ip_whitelist'] = True
mocked_ip_whitelist_range['data']['attributes']['rules'] = [
    {
        'type': 1,
        'ipMinimum': '10.0.0.1',
        'ipMaximum': '200.0.0.1'
    }
]
mocked_ip_whitelist_subnet = copy.deepcopy(mocked_ip_whitelist)
mocked_ip_whitelist_subnet['data']['attributes']['use_ip_whitelist'] = True
mocked_ip_whitelist_subnet['data']['attributes']['rules'] = [
    {
        'type': 2,
        'range': '123.12.34.0/31'
    }
]


mocked_config_server_error = copy.deepcopy(mocked_config)
mocked_config_server_error['ip_whitelist']['status'] = 400
mocked_config_ip = copy.deepcopy(mocked_config)
mocked_config_ip['ip_whitelist']['data'] = mocked_ip_whitelist_ip
mocked_config_ip_loopback = copy.deepcopy(mocked_config)
mocked_config_ip_loopback['ip_whitelist']['data'] = mocked_ip_whitelist_ip_loopback
mocked_config_range = copy.deepcopy(mocked_config)
mocked_config_range['ip_whitelist']['data'] = mocked_ip_whitelist_range
mocked_config_subnet = copy.deepcopy(mocked_config)
mocked_config_subnet['ip_whitelist']['data'] = mocked_ip_whitelist_subnet


@mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
class MiddlewareIpWhitelistTests(TestCase):

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
        IpWhitelist.fetched = False
        settings.MIDDLEWARE.remove('django_forest.middleware.PermissionMiddleware')
        settings.MIDDLEWARE.remove('django_forest.middleware.IpWhitelistMiddleware')

    @mock.patch('requests.get', side_effect=mocked_requests_permission(mocked_config_server_error))
    @mock.patch('django_forest.middleware.ip_whitelist.IpWhitelistMiddleware.get_client_ip', return_value='123.12.34.0')
    def test_server_error(self, mocked_ip, mocked_requests, mocked_decode):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    @mock.patch('requests.get', side_effect=mocked_requests_permission(mocked_config))
    @mock.patch('django_forest.middleware.ip_whitelist.IpWhitelistMiddleware.get_client_ip', return_value='123.12.34.0')
    def test_no_rules(self, mocked_ip, mocked_requests, mocked_decode):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    @mock.patch('requests.get', side_effect=mocked_requests_permission(mocked_config_ip))
    @mock.patch('django_forest.middleware.ip_whitelist.IpWhitelistMiddleware.get_client_ip', return_value=None)
    def test_no_ip(self, mocked_ip, mocked_requests, mocked_decode):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    @mock.patch('requests.get', side_effect=mocked_requests_permission(mocked_config_ip))
    def test_machine_ip(self, mocked_requests, mocked_decode):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    @mock.patch('requests.get', side_effect=mocked_requests_permission(mocked_config_ip))
    @mock.patch('django_forest.middleware.ip_whitelist.IpWhitelistMiddleware.get_client_ip', return_value='123.12.34.0')
    def test_ip(self, mocked_ip, mocked_requests, mocked_decode):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    @mock.patch('requests.get', side_effect=mocked_requests_permission(mocked_config_ip))
    @mock.patch('django_forest.middleware.ip_whitelist.IpWhitelistMiddleware.get_client_ip', return_value='123.12.34.1')
    def test_ip_invalid(self, mocked_ip, mocked_requests, mocked_decode):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    @mock.patch('requests.get', side_effect=mocked_requests_permission(mocked_config_ip))
    @mock.patch('django_forest.middleware.ip_whitelist.IpWhitelistMiddleware.get_client_ip', return_value='2001:db8::1000')
    def test_ip_v6_invalid(self, mocked_ip, mocked_requests, mocked_decode):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    @mock.patch('requests.get', side_effect=mocked_requests_permission(mocked_config_ip_loopback))
    @mock.patch('django_forest.middleware.ip_whitelist.IpWhitelistMiddleware.get_client_ip', return_value='127.0.0.2')
    def test_ip_loopback(self, mocked_ip, mocked_requests, mocked_decode):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    @mock.patch('requests.get', side_effect=mocked_requests_permission(mocked_config_range))
    @mock.patch('django_forest.middleware.ip_whitelist.IpWhitelistMiddleware.get_client_ip', return_value='123.12.34.5')
    def test_range(self, mocked_ip, mocked_requests, mocked_decode):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    @mock.patch('requests.get', side_effect=mocked_requests_permission(mocked_config_range))
    @mock.patch('django_forest.middleware.ip_whitelist.IpWhitelistMiddleware.get_client_ip', return_value='223.12.34.5')
    def test_range_invalid(self, mocked_ip, mocked_requests, mocked_decode):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    @mock.patch('requests.get', side_effect=mocked_requests_permission(mocked_config_range))
    @mock.patch('django_forest.middleware.ip_whitelist.IpWhitelistMiddleware.get_client_ip', return_value='2001:db8::1000')
    def test_range_ipv6_invalid(self, mocked_ip, mocked_requests, mocked_decode):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    @mock.patch('requests.get', side_effect=mocked_requests_permission(mocked_config_subnet))
    @mock.patch('django_forest.middleware.ip_whitelist.IpWhitelistMiddleware.get_client_ip', return_value='123.12.34.1')
    def test_no_subnet(self, mocked_ip, mocked_requests, mocked_decode):
        response = self.client.get(self.url, {
            'page[number]': '1',
            'page[size]': '15'
        })
        self.assertEqual(response.status_code, 200)

    @mock.patch('requests.get', side_effect=mocked_requests_permission(mocked_config_subnet))
    @mock.patch('django_forest.middleware.ip_whitelist.IpWhitelistMiddleware.get_client_ip', return_value='123.12.34.3')
    def test_subnet_invalid(self, mocked_ip, mocked_requests, mocked_decode):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)
