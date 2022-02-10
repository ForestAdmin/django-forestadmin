import os
from distutils.util import strtobool

from django.conf import settings


def get_forest_setting(setting, default=None):
    django_settings = getattr(settings, 'FOREST', {}).get(setting, default)
    forest_setting = os.getenv(setting, django_settings)
    if isinstance(default, bool) and isinstance(forest_setting, str):
        try:
            forest_setting = strtobool(forest_setting)
        except ValueError:
            forest_setting = default
    return forest_setting
