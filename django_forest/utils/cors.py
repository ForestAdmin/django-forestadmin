from django.conf import settings
from corsheaders.defaults import default_headers

from django_forest.utils.forest_setting import get_forest_setting


def get_list_setting(setting):
    return [x for x in get_forest_setting(setting, '').split(',') if x != '']


def set_cors():

    if 'corsheaders' not in settings.INSTALLED_APPS:
        settings.INSTALLED_APPS += ['corsheaders']

    if 'corsheaders.middleware.CorsMiddleware' not in settings.MIDDLEWARE:
        try:
            common_middleware_index = settings.MIDDLEWARE.index('django.middleware.common.CommonMiddleware')
        except ValueError:
            common_middleware_index = 0
        settings.MIDDLEWARE.insert(common_middleware_index, 'corsheaders.middleware.CorsMiddleware')

    settings.CORS_ALLOWED_ORIGIN_REGEXES = [
        r'.*\.forestadmin\.com.*',
        *getattr(settings, 'CORS_ALLOWED_ORIGIN_REGEXES', [])
    ]

    settings.CORS_ALLOW_HEADERS = [
        *getattr(settings, 'CORS_ALLOW_HEADERS', list(default_headers)),
        'forest-context-url',
    ]

    settings.CORS_ALLOW_CREDENTIALS = True
