import os
from distutils.util import strtobool

from django.conf import settings


def get_forest_setting(setting, default=None):
    env_setting = os.getenv(setting, default)
    forest_setting = getattr(settings, 'FOREST', {}).get(setting, env_setting)
    if isinstance(default, bool) and isinstance(forest_setting, str):
        try:
            forest_setting = strtobool(forest_setting)
        except ValueError:
            forest_setting = default
    return forest_setting
