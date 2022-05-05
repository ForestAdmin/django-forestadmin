import re
from django.conf import settings
from corsheaders.defaults import default_headers

from django_forest.utils.forest_setting import get_forest_setting


#  Waiting cors-header implem
def PnaMiddleware(get_response):
    def middleware(request):
        response = get_response(request)
        if request.headers.get('Access-Control-Request-Private-Network'):
            res = any([
                re.match(pattern, request.headers['origin']) for pattern in settings.CORS_ALLOWED_ORIGIN_REGEXES
            ])
            if res:
                response['Access-Control-Allow-Private-Network'] = 'true'
        return response

    return middleware


def get_list_setting(setting):
    return [x for x in get_forest_setting(setting, '').split(',') if x != '']


def set_cors():

    settings.INSTALLED_APPS = list(settings.INSTALLED_APPS)
    if 'corsheaders' not in settings.INSTALLED_APPS:
        settings.INSTALLED_APPS += ['corsheaders']

    settings.MIDDLEWARE = list(settings.MIDDLEWARE)
    if 'corsheaders.middleware.CorsMiddleware' not in settings.MIDDLEWARE:
        try:
            common_middleware_index = settings.MIDDLEWARE.index('django.middleware.common.CommonMiddleware')
        except ValueError:
            common_middleware_index = 0
        settings.MIDDLEWARE.insert(common_middleware_index, 'corsheaders.middleware.CorsMiddleware')

    pna_index = settings.MIDDLEWARE.index('corsheaders.middleware.CorsMiddleware')
    settings.MIDDLEWARE.insert(pna_index, 'django_forest.utils.cors.PnaMiddleware')

    settings.CORS_ALLOWED_ORIGIN_REGEXES = [
        r'.*\.forestadmin\.com.*',
        *getattr(settings, 'CORS_ALLOWED_ORIGIN_REGEXES', [])
    ]

    settings.CORS_ALLOW_HEADERS = [
        *getattr(settings, 'CORS_ALLOW_HEADERS', list(default_headers)),
        'forest-context-url',
    ]

    settings.CORS_ALLOW_CREDENTIALS = True
