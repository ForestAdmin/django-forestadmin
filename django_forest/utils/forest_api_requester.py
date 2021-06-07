import json
import os
from urllib.parse import urljoin

import requests
from django.conf import settings


class ForestApiRequester:

    @staticmethod
    def get_headers(headers):
        forest_secret_key = getattr(settings, 'FOREST', {}).get('FOREST_ENV_SECRET', os.getenv('FOREST_ENV_SECRET'))
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
    def forest_api_url():
        return getattr(settings, 'FOREST', {}).get('FOREST_URL', os.getenv('FOREST_URL', 'https://api.forestadmin.com'))

    @classmethod
    def _get_url(cls, route):
        if route.startswith('https://'):
            url = route
        else:
            url = urljoin(cls.forest_api_url(), route)
        return url

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
    def get(cls, route, query=None, headers=None):
        body, query, headers = cls.get_params(query=query, headers=headers)
        url = urljoin(cls.forest_api_url(), route)

        try:
            r = requests.get(url,
                             params=query,
                             headers=cls.get_headers(headers),
                             verify=not settings.DEBUG)
        except Exception:
            raise Exception(cls.error_msg(url))
        else:
            return r

    @classmethod
    def post(cls, route, body=None, query=None, headers=None):
        body, query, headers = cls.get_params(body=body, query=query, headers=headers)
        url = cls._get_url(route)

        try:
            r = requests.post(url,
                              data=json.dumps(body),
                              headers=cls.get_headers(headers),
                              params=query,
                              verify=not settings.DEBUG)
        except Exception:
            raise Exception(cls.error_msg(url))
        else:
            return r
