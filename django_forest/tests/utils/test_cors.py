from django.conf import settings
from django.test import TestCase, override_settings
from corsheaders.defaults import default_headers

from django_forest.utils.cors import set_cors


class UtilsCorsTests(TestCase):

    @override_settings(MIDDLEWARE=[], INSTALLED_APPS=[])
    def test_set_cors(self):
        set_cors()
        self.assertTrue('corsheaders' in settings.INSTALLED_APPS)
        self.assertTrue('corsheaders.middleware.CorsMiddleware' in settings.MIDDLEWARE)
        self.assertEqual(settings.MIDDLEWARE.index('django_forest.utils.cors.PnaMiddleware'), 0)
        self.assertEqual(settings.MIDDLEWARE.index('corsheaders.middleware.CorsMiddleware'), 1)
        self.assertEqual(settings.CORS_ALLOWED_ORIGIN_REGEXES, ['.*\\.forestadmin\\.com.*'])
        self.assertEqual(settings.CORS_ALLOW_HEADERS, list(default_headers) + ['forest-context-url'])
        self.assertEqual(settings.CORS_ALLOW_CREDENTIALS, True)

    @override_settings(INSTALLED_APPS=['corsheaders'])
    def test_set_cors_apps_already_present(self):
        set_cors()
        self.assertEqual(settings.INSTALLED_APPS, ['corsheaders'])

    @override_settings(MIDDLEWARE=['fake', 'django.middleware.X', 'corsheaders.middleware.CorsMiddleware'])
    def test_set_cors_middleware_already_present(self):
        set_cors()
        self.assertEqual(settings.MIDDLEWARE, ['fake', 'django.middleware.X', 'django_forest.utils.cors.PnaMiddleware', 'corsheaders.middleware.CorsMiddleware'])
    
    @override_settings(MIDDLEWARE=['fake', 'django.middleware.common.CommonMiddleware', 'corsheaders.middleware.CorsMiddleware'])
    def test_set_cors_with_common_middleware(self):
        self.assertEqual(settings.MIDDLEWARE, ['fake', 'django.middleware.common.CommonMiddleware', 'corsheaders.middleware.CorsMiddleware'])

    @override_settings(MIDDLEWARE=['fakemiddleware', 'django.middleware.common.CommonMiddleware', 'fakemiidleware2'])
    def test_set_cors_common_middleware(self):
        set_cors()
        self.assertTrue('corsheaders.middleware.CorsMiddleware' in settings.MIDDLEWARE)
        self.assertEqual(settings.MIDDLEWARE, ['fakemiddleware', 'django_forest.utils.cors.PnaMiddleware', 'corsheaders.middleware.CorsMiddleware', 'django.middleware.common.CommonMiddleware', 'fakemiidleware2'])

    @override_settings(CORS_ALLOWED_ORIGIN_REGEXES=[r'/\.foo\.com$/',r'/\.bar\.com$/'])
    def test_extends_allowed_origin_regexes(self):
        set_cors()
        self.assertEqual(settings.CORS_ALLOWED_ORIGIN_REGEXES, ['.*\\.forestadmin\\.com.*', '/\\.foo\\.com$/', '/\\.bar\\.com$/'])
    
    @override_settings(CORS_ALLOW_HEADERS=['fake', 'fake2'])
    def test_extends_allowed_headers(self):
        set_cors()
        self.assertEqual(settings.CORS_ALLOW_HEADERS, ['fake', 'fake2', 'forest-context-url'])
    