import os
import urllib3
from distutils.util import strtobool

from django.apps import AppConfig

disable_warnings = os.getenv('URLLIB3_DISABLE_WARNINGS', 'False')
try:
    disable_warnings = strtobool(disable_warnings)
except Exception:
    disable_warnings = False
finally:
    if disable_warnings:
        urllib3.disable_warnings()


class BaseForestException(Exception):
    pass


class ForestConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_forest'
