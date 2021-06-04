import os

from django.apps import apps
from django.conf import settings


class Models:
    models = None

    @classmethod
    def list(cls, force=False):
        if cls.models is None or force:
            included_models = getattr(settings, 'FOREST', {}).get('INCLUDED_MODELS', os.getenv('INCLUDED_MODELS', None))
            excluded_models = getattr(settings, 'FOREST', {}).get('EXCLUDED_MODELS', os.getenv('EXCLUDED_MODELS', None))
            cls.models = apps.get_models()
            if included_models is not None:
                cls.models = [m for m in cls.models if m.__name__ in included_models]
            elif excluded_models is not None:
                cls.models = [m for m in cls.models if m.__name__ not in excluded_models]
        return cls.models

    @classmethod
    def get(cls, resource):
        for model in cls.list():
            if resource.lower() in (model.__name__.lower(), f'{model.__name__.lower()}s'):
                return model

        return None
