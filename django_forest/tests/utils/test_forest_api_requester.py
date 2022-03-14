import json
from unittest import mock

from django.core.serializers.json import DjangoJSONEncoder
from django.test import TestCase, override_settings

from django_forest.utils.forest_api_requester import ForestApiRequester


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code
        self.headers = {'content-type': 'application/json'}
        self.text = json.dumps(json_data, cls=DjangoJSONEncoder)

    def json(self):
        return self.json_data


class MockResponseNoData:
    def __init__(self, status_code):
        self.status_code = status_code


def mocked_requests(json_data, status_code):
    return MockResponse(json_data, status_code)


def mocked_requests_no_data(status_code):
    return MockResponseNoData(status_code)


class UtilsForestApiRequesterTests(TestCase):

    @mock.patch('requests.get', return_value=mocked_requests({'key1': 'value1'}, 200))
    def test_get(self, mocked_requests_get):
        r = ForestApiRequester.get('/foo')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json_data, {'key1': 'value1'})

    @override_settings(DEBUG=True)
    @mock.patch('requests.get', return_value=mocked_requests({'key1': 'value1'}, 200))
    def test_get_debug(self, mocked_requests_get):
        r = ForestApiRequester.get(
            ForestApiRequester.build_url('/foo')
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json_data, {'key1': 'value1'})
        mocked_requests_get.assert_called_once_with(
            'https://api.test.forestadmin.com/foo',
            headers={'Content-Type': 'application/json', 'forest-secret-key': 'foo'},
            params={},
            verify=False
        )

    @mock.patch('requests.post', return_value=mocked_requests({'key1': 'value1'}, 200))
    def test_post(self, mocked_requests_post):
        r = ForestApiRequester.post('/foo', {'foo': 'bar'})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json_data, {'key1': 'value1'})

    @override_settings(DEBUG=True)
    @mock.patch('requests.post', return_value=mocked_requests({'key1': 'value1'}, 200))
    def test_post_debug(self, mocked_requests_post):
        r = ForestApiRequester.post(
            ForestApiRequester.build_url('/foo'), 
            {'foo': 'bar'}
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json_data, {'key1': 'value1'})
        mocked_requests_post.assert_called_once_with(
            'https://api.test.forestadmin.com/foo',
            data=json.dumps({'foo': 'bar'}),
            headers={'Content-Type': 'application/json', 'forest-secret-key': 'foo'},
            params={},
            verify=False
        )

    @mock.patch('requests.post', return_value=mocked_requests({'key1': 'value1'}, 200))
    def test_post_ssl(self, mocked_requests_post):
        r = ForestApiRequester.post('/foo', {'foo': 'bar'})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json_data, {'key1': 'value1'})

    def test_get_url(self):
        url = ForestApiRequester._get_url('/foo')
        self.assertEqual(url, 'https://api.test.forestadmin.com/foo')

    def test_get_url_ssl(self):
        url = ForestApiRequester._get_url('https://foo.com')
        self.assertEqual(url, 'https://foo.com')
