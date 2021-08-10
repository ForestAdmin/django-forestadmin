from django.conf import settings


def set_middlewares():
    settings.MIDDLEWARE.insert(0, 'django_forest.middleware.PermissionMiddleware')
    settings.MIDDLEWARE.insert(0, 'django_forest.middleware.IpWhitelistMiddleware')
