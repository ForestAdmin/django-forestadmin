import json
from datetime import datetime
from unittest import mock

import pytz
from django.test import TestCase
from django.urls import reverse

from django_forest.tests.resources.views.list.test_list_scope import mocked_scope
from django_forest.utils.scope import ScopeManager


class ScopeCacheInvalidationViewTests(TestCase):
    def setUp(self):
        self.client = self.client_class(
            HTTP_AUTHORIZATION='Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjUiLCJlbWFpbCI6Imd1aWxsYXVtZWNAZm9yZXN0YWRtaW4uY29tIiwiZmlyc3RfbmFtZSI6Ikd1aWxsYXVtZSIsImxhc3RfbmFtZSI6IkNpc2NvIiwidGVhbSI6Ik9wZXJhdGlvbnMiLCJyZW5kZXJpbmdfaWQiOjEsImV4cCI6MTYyNTY3OTYyNi44ODYwMTh9.mHjA05yvMr99gFMuFv0SnPDCeOd2ZyMSN868V7lsjnw')
        ScopeManager.cache = {
            '1': {
                'scopes': mocked_scope,
                'fetched_at': datetime(2021, 7, 8, 9, 20, 22, 582772, tzinfo=pytz.UTC)
            }
        }

    def tearDown(self):
        # reset _registry after each test
        ScopeManager.cache = {}

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @mock.patch('django_forest.utils.scope.ScopeManager._has_cache_expired', return_value=False)
    def test_post(self, mocked_scope_has_expired, mocked_decode):
        response = self.client.post(reverse('django_forest:scope-cache-invalidation'),
                                    json.dumps({'renderingId': 1}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)

    @mock.patch('jose.jwt.decode', return_value={'id': 1})
    def test_post_no_renderingId(self, mocked_decode):
        response = self.client.post(reverse('django_forest:scope-cache-invalidation'),
                                     json.dumps({}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_post_unauthenticated(self):
        response = self.client.post(reverse('django_forest:scope-cache-invalidation'),
                                     json.dumps({}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 403)
