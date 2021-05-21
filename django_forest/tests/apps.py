from django.apps import AppConfig

from django_forest.utils.cors import set_cors
from django_forest.utils.schema import Schema


class ForestConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_forest'

    def ready(self):
        # set cors
        set_cors()

        # schema
        Schema.build_schema()
        Schema.add_smart_features()
        Schema.handle_json_api_serializer()
        Schema.handle_schema_file()
        Schema.send_apimap()
