import os
from urllib.parse import urljoin

from django.conf import settings
from django.urls import reverse


def get_callback_url():
    APPLICATION_URL = getattr(settings, 'FOREST', {}).get('APPLICATION_URL', os.getenv('APPLICATION_URL', None))

    if not APPLICATION_URL:
        raise Exception('APPLICATION_URL is not defined')

    return urljoin(APPLICATION_URL, reverse('django_forest:authentication:callback'))
