import os
from distutils.util import strtobool

from django.apps import AppConfig

from django_forest.utils.schema import Schema

import urllib3

disable_warnings = os.getenv('URLLIB3_DISABLE_WARNINGS', 'False')
if isinstance(disable_warnings, str):
    try:
        disable_warnings = strtobool(disable_warnings)
    except Exception:
        disable_warnings = False
    if disable_warnings:
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
