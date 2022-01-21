from django.conf import settings
from django.test import TestCase, override_settings
from corsheaders.defaults import default_headers

from django_forest.utils.cors import set_cors


class UtilsCorsTests(TestCase):

    def test_set_cors(self):
        set_cors()
        self.assertTrue('corsheaders.middleware.CorsMiddleware' in settings.MIDDLEWARE)
        common_middleware_index = settings.MIDDLEWARE.index('django.middleware.common.CommonMiddleware')
        self.assertEqual(settings.MIDDLEWARE.index('corsheaders.middleware.CorsMiddleware'), common_middleware_index - 1)
        self.assertEqual(settings.CORS_ALLOWED_ORIGIN_REGEXES, ['.*\\.forestadmin\\.com.*'])
        self.assertEqual(settings.CORS_ALLOW_HEADERS, list(default_headers) + ['forest-context-url'])

    @override_settings(MIDDLEWARE=[])
    def test_set_cors_no_common_middleware(self):
        set_cors()
        self.assertTrue('corsheaders.middleware.CorsMiddleware' in settings.MIDDLEWARE)
        self.assertEqual(settings.MIDDLEWARE, ['corsheaders.middleware.CorsMiddleware'])

    @override_settings(CORS_ALLOWED_ORIGIN_REGEXES=[r'/\.foo\.com$/',r'/\.bar\.com$/'])
    def test_extends_allowed_origin_regexes(self):
        set_cors()
        self.assertEqual(settings.CORS_ALLOWED_ORIGIN_REGEXES, ['.*\\.forestadmin\\.com.*', '/\\.foo\\.com$/', '/\\.bar\\.com$/'])
    
    @override_settings(CORS_ALLOW_HEADERS=['fake', 'fake2'])
    def test_extends_allowed_headers(self):
        set_cors()
        self.assertEqual(settings.CORS_ALLOW_HEADERS, ['fake', 'fake2', 'forest-context-url'])
    