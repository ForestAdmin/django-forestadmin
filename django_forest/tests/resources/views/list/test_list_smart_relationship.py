import sys
from datetime import datetime
from unittest import mock

import pytest
import pytz
from django.test import TransactionTestCase
from django.urls import reverse
from freezegun import freeze_time

from django_forest.tests.resources.views.list.test_list_scope import mocked_scope
from django_forest.utils.collection import Collection
from django_forest.utils.models import Models
from django_forest.utils.schema import Schema
from django_forest.utils.schema.json_api_schema import JsonApiSchema
from django_forest.utils.date import get_timezone


# reset forest config dir auto import
from django_forest.utils.scope import ScopeManager


@pytest.fixture()
def reset_config_dir_import():
    for key in list(sys.modules.keys()):
        if key.startswith('django_forest.tests.forest'):
            del sys.modules[key]


@pytest.mark.usefixtures('reset_config_dir_import')
class ResourceListSmartRelationshipViewTests(TransactionTestCase):
    fixtures = ['question.json', 'choice.json']

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, django_assert_num_queries):
        self._django_assert_num_queries = django_assert_num_queries

    def setUp(self):
        Schema.build_schema()
        Schema.add_smart_features()
        Schema.handle_json_api_schema()
        self.url = reverse('django_forest:resources:list', kwargs={'resource': 'tests_choice'})
        self.client = self.client_class(
            HTTP_AUTHORIZATION='Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjUiLCJlbWFpbCI6Imd1aWxsYXVtZWNAZm9yZXN0YWRtaW4uY29tIiwiZmlyc3RfbmFtZSI6Ikd1aWxsYXVtZSIsImxhc3RfbmFtZSI6IkNpc2NvIiwidGVhbSI6Ik9wZXJhdGlvbnMiLCJyZW5kZXJpbmdfaWQiOjEsImV4cCI6MTYyNTY3OTYyNi44ODYwMTh9.mHjA05yvMr99gFMuFv0SnPDCeOd2ZyMSN868V7lsjnw')

    def tearDown(self):
        # reset _registry after each test
        JsonApiSchema._registry = {}
        Collection._registry = {}
        ScopeManager.cache = {}
        Schema.schema_data = None
        Models.models = None

    @mock.patch('jose.jwt.decode', return_value={'id': 1, 'rendering_id': 1})
    @freeze_time(
        lambda: datetime(2021, 6, 4, 9, 20, 22, 582772, tzinfo=get_timezone('UTC'))
    )
    @mock.patch('django_forest.utils.scope.ScopeManager._has_cache_expired', return_value=False)
    def test_get(self, mocked_scope_has_expired, mocked_decode):
        ScopeManager.cache = {
            '1': {
                'scopes': mocked_scope,
                'fetched_at': datetime(2021, 7, 8, 9, 20, 22, 582772, tzinfo=pytz.UTC)
            }
        }
        response = self.client.get(self.url, {
            'fields[tests_choice]': 'id,question,topic,choice_text,votes',
            'fields[question]': 'question_text',
            'fields[topic]': 'name',
            'page[number]': '1',
            'page[size]': '15'
        })
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {
            'data': [{'type': 'tests_choice', 'attributes': {'choice_text': 'yes', 'votes': 0}, 'relationships': {
                'topic': {'links': {'related': '/forest/tests_choice/1/relationships/topic'}, 'data': None},
                'question': {'links': {'related': '/forest/tests_choice/1/relationships/question'},
                             'data': {'type': 'tests_question', 'id': '1'}}}, 'id': 1, 'links': {'self': '/forest/tests_choice/1'}},
                     {'type': 'tests_choice', 'attributes': {'choice_text': 'no', 'votes': 1}, 'relationships': {
                         'topic': {'links': {'related': '/forest/tests_choice/2/relationships/topic'}, 'data': None},
                         'question': {'links': {'related': '/forest/tests_choice/2/relationships/question'},
                                      'data': {'type': 'tests_question', 'id': '1'}}}, 'id': 2,
                      'links': {'self': '/forest/tests_choice/2'}},
                     {'type': 'tests_choice', 'attributes': {'choice_text': 'good', 'votes': 1}, 'relationships': {
                         'topic': {'links': {'related': '/forest/tests_choice/3/relationships/topic'}, 'data': None},
                         'question': {'links': {'related': '/forest/tests_choice/3/relationships/question'},
                                      'data': {'type': 'tests_question', 'id': '2'}}}, 'id': 3,
                      'links': {'self': '/forest/tests_choice/3'}}], 'included': [
                {'type': 'tests_question', 'attributes': {'question_text': 'what is your favorite color?'}, 'id': 1,
                 'links': {'self': '/forest/tests_question/1'}},
                {'type': 'tests_question', 'attributes': {'question_text': 'do you like chocolate?'}, 'id': 2,
                 'links': {'self': '/forest/tests_question/2'}}]})
