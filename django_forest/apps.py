import os
from distutils.util import strtobool

from django.apps import AppConfig

from django_forest.utils.cors import set_cors
from django_forest.utils.schema import Schema

import urllib3

disable_warnings = os.getenv('URLLIB3_DISABLE_WARNINGS', 'False')
try:
    disable_warnings = strtobool(disable_warnings)
except Exception:
    disable_warnings = False
if disable_warnings:
    urllib3.disable_warnings()


# TODO, override runserver command instead (this code run on makmigrations, migrate and all others commands...)
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
