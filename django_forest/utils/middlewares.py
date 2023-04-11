from django.conf import settings


def set_middlewares():
    middlewares = list(settings.MIDDLEWARE)

    if 'django_forest.middleware.PermissionMiddleware' not in middlewares:
        settings.MIDDLEWARE.insert(0, 'django_forest.middleware.PermissionMiddleware')

    if 'django_forest.middleware.IpWhitelistMiddleware' not in middlewares:
        settings.MIDDLEWARE.insert(0, 'django_forest.middleware.IpWhitelistMiddleware')
