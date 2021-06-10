from django.apps import AppConfig
from django.conf import settings

from django_forest.utils.schema import Schema

import urllib3

if settings.DEBUG:
    urllib3.disable_warnings()


class ForestConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_forest'

    def ready(self):
        # schema
        Schema.build_schema()
        Schema.add_smart_features()
        Schema.handle_json_api_serializer()
        Schema.handle_schema_file()
        Schema.send_apimap()
