# flake8: noqa

import os

from django.conf import settings


def set_cors():
    settings.INSTALLED_APPS += ['corsheaders']
    try:
        common_middleware_index = settings.MIDDLEWARE.index('django.middleware.common.CommonMiddleware')
    except ValueError:
        common_middleware_index = 0
    settings.MIDDLEWARE.insert(common_middleware_index, 'corsheaders.middleware.CorsMiddleware')

    settings.CORS_ALLOWED_ORIGINS = ['http://localhost:4200'] + getattr(settings, 'FOREST', {}).get('CORS_ALLOWED_ORIGINS', os.getenv('CORS_ALLOWED_ORIGINS', '')).split(',')
    settings.CORS_ALLOWED_ORIGIN_REGEXES = [r'/\.forestadmin\.com$/'] + getattr(settings, 'FOREST', {}).get('CORS_ALLOWED_ORIGIN_REGEXES', os.getenv('CORS_ALLOWED_ORIGIN_REGEXES', '')).split(',')
    settings.CORS_URLS_REGEX = r'^/forest(/.*)?$'  # restrict it to /forest
    settings.CORS_PREFLIGHT_MAX_AGE = 86400  # one day
    settings.CORS_ALLOW_CREDENTIALS = True
