from django.apps import AppConfig

from django_forest.utils.schema import Schema


class ForestConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_forest'

    def ready(self):
        # schema
        Schema.build_schema()
        Schema.add_smart_features()
        Schema.handle_json_api_serializer()
