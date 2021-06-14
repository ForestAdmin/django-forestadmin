from django.conf import settings
from django.test import TestCase, override_settings

from django_forest.utils.cors import set_cors


class UtilsCorsTests(TestCase):

    def test_set_cors(self):
        set_cors()
        self.assertTrue('corsheaders.middleware.CorsMiddleware' in settings.MIDDLEWARE)
        common_middleware_index = settings.MIDDLEWARE.index('django.middleware.common.CommonMiddleware')
        self.assertEqual(settings.MIDDLEWARE.index('corsheaders.middleware.CorsMiddleware'), common_middleware_index - 1)
        self.assertEqual(settings.CORS_ALLOWED_ORIGINS, ['http://localhost:4200'])
        self.assertEqual(settings.CORS_ALLOWED_ORIGIN_REGEXES, ['.*\\.forestadmin\\.com.*'])
        self.assertEqual(settings.CORS_URLS_REGEX, r'^/forest(/.*)?$')
        self.assertEqual(settings.CORS_PREFLIGHT_MAX_AGE, 86400)
        self.assertEqual(settings.CORS_ALLOW_CREDENTIALS, True)

    @override_settings(MIDDLEWARE=[])
    def test_set_cors_no_common_middleware(self):
        set_cors()
        self.assertTrue('corsheaders.middleware.CorsMiddleware' in settings.MIDDLEWARE)
        self.assertEqual(settings.MIDDLEWARE, ['corsheaders.middleware.CorsMiddleware'])

    @override_settings(FOREST={'CORS_ALLOWED_ORIGINS': 'http://foo.com,https://bar.com', 'CORS_ALLOWED_ORIGIN_REGEXES': '/\.foo\.com$/,/\.bar\.com$/'})
    def test_set_cors_forest_settings(self):
        set_cors()
        self.assertEqual(settings.CORS_ALLOWED_ORIGINS, ['http://localhost:4200', 'http://foo.com', 'https://bar.com'])
        self.assertEqual(settings.CORS_ALLOWED_ORIGIN_REGEXES, ['.*\\.forestadmin\\.com.*', '/\\.foo\\.com$/', '/\\.bar\\.com$/'])
