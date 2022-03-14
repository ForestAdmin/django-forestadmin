from urllib.parse import urljoin
from django.urls import reverse

from django.http import JsonResponse
from django_forest.authentication.exception import AuthenticationSettingsException, BaseAuthenticationException
from django_forest.utils.forest_setting import get_forest_setting


def get_callback_url():
    application_url = get_forest_setting('APPLICATION_URL')

    if not application_url:
        raise AuthenticationSettingsException('APPLICATION_URL is not defined in your FOREST settings')

    return urljoin(application_url, reverse('django_forest:authentication:callback'))


def authentication_exception(f):
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except BaseAuthenticationException as error:
            return JsonResponse({'errors': [{'detail': str(error)}]}, status=error.STATUS)
    return wrapper
