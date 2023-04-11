from django.conf import settings
from django.test import TestCase

from django_forest.utils.middlewares import set_middlewares


class UtilsMiddlewaresTests(TestCase):
    def tearDown(self):
        settings.MIDDLEWARE.remove("django_forest.middleware.PermissionMiddleware")
        settings.MIDDLEWARE.remove("django_forest.middleware.IpWhitelistMiddleware")

    def test_set_middlewares(self):
        set_middlewares()
        self.assertTrue(
            "django_forest.middleware.PermissionMiddleware" in settings.MIDDLEWARE
        )
        self.assertTrue(
            "django_forest.middleware.IpWhitelistMiddleware" in settings.MIDDLEWARE
        )

    def test_set_middlewares_already_present(self):
        settings.MIDDLEWARE.insert(0, "django_forest.middleware.PermissionMiddleware")
        settings.MIDDLEWARE.append("django_forest.middleware.IpWhitelistMiddleware")

        set_middlewares()

        permission_filtered_middlewares = list(
            filter(
                lambda x: x == "django_forest.middleware.PermissionMiddleware",
                settings.MIDDLEWARE,
            )
        )
        ip_whitelist_filtered_middlewares = list(
            filter(
                lambda x: x == "django_forest.middleware.IpWhitelistMiddleware",
                settings.MIDDLEWARE,
            )
        )
        # exists only once
        self.assertEqual(len(permission_filtered_middlewares), 1)
        self.assertEqual(len(ip_whitelist_filtered_middlewares), 1)

        # order preserved
        self.assertEqual(settings.MIDDLEWARE[0], "django_forest.middleware.PermissionMiddleware")
        self.assertEqual(settings.MIDDLEWARE[-1], "django_forest.middleware.IpWhitelistMiddleware")