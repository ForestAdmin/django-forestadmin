from django.conf import settings
from corsheaders.defaults import default_headers

from django_forest.utils.forest_setting import get_forest_setting


def get_list_setting(setting):
    return [x for x in get_forest_setting(setting, '').split(',') if x != '']


def set_cors():
    settings.INSTALLED_APPS += ['corsheaders']
    try:
        common_middleware_index = settings.MIDDLEWARE.index('django.middleware.common.CommonMiddleware')
    except ValueError:
        common_middleware_index = 0
    settings.MIDDLEWARE.insert(common_middleware_index, 'corsheaders.middleware.CorsMiddleware')

    cors_allowed_origins = ['http://localhost:4200']
    cors_allowed_origins.extend(get_list_setting('CORS_ALLOWED_ORIGINS'))

    cors_allowed_origins_regexes = [r'.*\.forestadmin\.com.*']
    cors_allowed_origins_regexes.extend(get_list_setting('CORS_ALLOWED_ORIGIN_REGEXES'))

    settings.CORS_ALLOWED_ORIGINS = cors_allowed_origins
    settings.CORS_ALLOWED_ORIGIN_REGEXES = cors_allowed_origins_regexes
    settings.CORS_URLS_REGEX = r'^/forest(/.*)?$'  # restrict it to /forest
    settings.CORS_PREFLIGHT_MAX_AGE = 86400  # one day
    settings.CORS_ALLOW_CREDENTIALS = True

    settings.CORS_ALLOW_HEADERS = list(default_headers) + [
        'forest-context-url',
    ]
