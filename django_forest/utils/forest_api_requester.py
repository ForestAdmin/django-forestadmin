import json
from urllib.parse import urljoin

import requests
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from django_forest.utils.forest_setting import get_forest_setting


class ForestApiRequester:

    @staticmethod
    def get_headers(headers):
        forest_secret_key = get_forest_setting('FOREST_ENV_SECRET')
        base_headers = {
            'Content-Type': 'application/json',
            'forest-secret-key': forest_secret_key,
        }
        base_headers.update(headers)
        return base_headers

    @staticmethod
    def error_msg(url):
        return f'Cannot reach Forest API at {url}, it seems to be down right now.'

    @staticmethod
    def _get_url(route):
        validate = URLValidator()

        try:
            validate(route)
        except ValidationError:
            forest_api_url = get_forest_setting('FOREST_URL', 'https://api.forestadmin.com')
            url = urljoin(forest_api_url, route)
        else:
            url = route
        return url

    @staticmethod
    def build_url(resource):
        forest_api_url = get_forest_setting('FOREST_URL', 'https://api.forestadmin.com')
        return urljoin(forest_api_url, resource)

    @staticmethod
    def get_params(body=None, query=None, headers=None):
        if body is None:
            body = {}
        if query is None:
            query = {}
        if headers is None:
            headers = {}

        return body, query, headers

    @classmethod
    def run_method(cls, method, url, kwargs):
        try:
            r = method(url, **kwargs)
        except Exception:
            raise Exception(cls.error_msg(url))
        else:
            return r

    @classmethod
    def get_from_rendering_id(cls, route, rendering_id):
        query = {
            'renderingId': rendering_id
        }
        url = ForestApiRequester.build_url(route)
        response = ForestApiRequester.get(url, query=query)
        if response.status_code == requests.codes.ok:
            return response.json()
        else:
            raise Exception(f'Forest API returned an #{response.content}')

    @classmethod
    def get(cls, url, query=None, headers=None):
        kwargs = {
            'params': query or {},
            'headers': cls.get_headers(headers or {})
        }
        if settings.DEBUG:
            kwargs['verify'] = False

        return requests.get(url, **kwargs)

    @classmethod
    def post(cls, url, body=None, query=None, headers=None):
        body, query, headers = cls.get_params(body=body, query=query, headers=headers)

        kwargs = {
            'data': json.dumps(body),
            'params': query,
            'headers': cls.get_headers(headers)
        }
        if settings.DEBUG:
            kwargs['verify'] = False
        return requests.post(url, **kwargs)
