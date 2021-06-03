import os

from django.apps import apps
from django.conf import settings


# TODO memoize this
def get_models():
    included_models = getattr(settings, 'FOREST', {}).get('INCLUDED_MODELS', os.getenv('INCLUDED_MODELS', None))
    excluded_models = getattr(settings, 'FOREST', {}).get('EXCLUDED_MODELS', os.getenv('EXCLUDED_MODELS', None))
    models = apps.get_models()
    if included_models is not None:
        models = [m for m in models if m.__name__ in included_models]
    elif excluded_models is not None:
        models = [m for m in models if m.__name__ not in excluded_models]
    return models


def get_model(resource):
    for model in get_models():
        if resource.lower() in (model.__name__.lower(), f'{model.__name__.lower()}s'):
            return model

    return None
