from django.apps import apps


def get_model(resource):
    # TODO handle included/excluded models from settings
    # TODO support smart collection
    models = [model for model in apps.get_models() if model.__name__.lower() == resource.lower()]
    if len(models):
        return models[0]

    return None
