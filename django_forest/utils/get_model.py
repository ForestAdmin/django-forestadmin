from django.apps import apps


def get_model(resource):
    # TODO handle included/excluded models from settings
    for model in apps.get_models():
        if resource.lower() in (model.__name__.lower(), f'{model.__name__.lower()}s'):
            return model

    return None