from django.conf import settings
from django.test import TestCase

from django_forest.utils.middlewares import set_middlewares


class UtilsMiddlewaresTests(TestCase):

    def tearDown(self):
        settings.MIDDLEWARE.remove('django_forest.middleware.PermissionMiddleware')

    def test_set_middlewares(self):
        set_middlewares()
        self.assertTrue('django_forest.middleware.PermissionMiddleware' in settings.MIDDLEWARE)
