from urllib.parse import urljoin
from django.urls import reverse

from django_forest.utils.forest_setting import get_forest_setting


def get_callback_url():
    application_url = get_forest_setting('APPLICATION_URL')

    if not application_url:
        raise Exception('APPLICATION_URL is not defined in your FOREST settings')

    return urljoin(application_url, reverse('django_forest:authentication:callback'))
