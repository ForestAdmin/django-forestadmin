from django.apps import apps

from django_forest.utils.forest_setting import get_forest_setting


class Models:
    models = None

    @classmethod
    def list(cls, force=False):
        if cls.models is None or force:
            included_models = get_forest_setting('INCLUDED_MODELS')
            excluded_models = get_forest_setting('EXCLUDED_MODELS')
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
