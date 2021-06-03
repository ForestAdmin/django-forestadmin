import copy
import os
import sys
import django
from django.conf import settings
from django.db import connection
from django.utils.module_loading import autodiscover_modules

from django_forest.utils.get_model import get_models
from django_forest.utils.get_type import get_type
from django_forest.utils.json_api_serializer import create_json_api_schema

if sys.version_info >= (3, 8):
    from importlib import metadata
else:
    import importlib_metadata as metadata


COLLECTION = {
    'name': '',
    'is_virtual': False,
    'icon': None,
    'is_read_only': False,
    'is_searchable': True,
    'only_for_relationships': False,
    'pagination_type': 'page',
    'search_fields': None,
    'actions': [],
    'segments': [],
    'fields': []
}

FIELD = {
    'field': '',
    'type': '',
    'is_filterable': True,
    'is_sortable': True,
    'is_read_only': False,
    'is_required': False,
    'is_virtual': False,
    'default_value': None,
    'integration': None,
    'reference': None,
    'inverse_of': None,
    'relationship': None,
    'widget': None,
    'validations': []
}

ACTION_FIELD = {
    'field': '',
    'type': '',
    'is_read_only': False,
    'is_required': False,
    'default_value': None,
    'enums': None,
    'integration': None,
    'reference': None,
    'description': None,
    'widget': None,
    'position': 0,
}


def get_app_version():
    version = '0.0.0'
    try:
        version = metadata.version('django_forest')
    except Exception:
        pass
    finally:
        return version


class Schema:
    schema = {
        'collections': [],
        'meta': {
            'database_type': connection.vendor,
            'liana': 'django-forest',
            'liana_version': get_app_version(),
            'orm_version': django.get_version()
        }
    }
    models = get_models()

    @classmethod
    def get_collection(cls, resource):
        collections = [collection for collection in cls.schema['collections'] if collection['name'] == resource]
        if len(collections):
            return collections[0]

        return None

    @classmethod
    def get_default_collection(cls, obj):
        for key, value in copy.deepcopy(COLLECTION).items():
            obj[key] = value if key not in obj else obj[key]

        return obj

    @classmethod
    def get_default_field(cls, obj):
        for key, value in copy.deepcopy(FIELD).items():
            obj[key] = value if key not in obj else obj[key]

        return obj

    @classmethod
    def get_default_action_field(cls, obj):
        for key, value in copy.deepcopy(ACTION_FIELD).items():
            obj[key] = value if key not in obj else obj[key]

        return obj

    @classmethod
    def _get_relation_type(cls, many):
        if many:
            return ['Number']
        return 'Number'

    @classmethod
    def _get_relationship(cls, field):
        if field.one_to_many or field.many_to_many:
            return 'HasMany'
        elif field.one_to_one:
            return 'HasOne'
        return 'BelongsTo'

    @classmethod
    def handle_relation(cls, field, f):
        if field.is_relation:
            # Notice: do not add if not in included/excluded models
            if field.target_field.model not in cls.models:
                return None

            many = field.one_to_many or field.many_to_many
            f['type'] = cls._get_relation_type(many)
            f['relationship'] = cls._get_relationship(field)
            # Notice: forest-rails always put id on the end, do we support polymorphic support?
            f['reference'] = f'{field.target_field.model.__name__}.{field.target_field.name}'
            f['is_filterable'] = not many
            f['inverse_of'] = None if not hasattr(field, 'related_name') else field.related_name
        return f

    @classmethod
    def add_fields(cls, model, collection):
        for field in model._meta.get_fields():
            f = cls.get_default_field({
                'field': field.name,
                'type': get_type(field)
            })
            f = cls.handle_relation(field, f)

            if f is not None:
                collection['fields'].append(f)

    @classmethod
    def build_schema(cls):
        for model in cls.models:
            collection = cls.get_default_collection({'name': model.__name__})
            cls.add_fields(model, collection)
            cls.schema['collections'].append(collection)
        return cls.schema

    @classmethod
    def add_smart_features(cls):
        # Notice: will load all files in <app>/forest folder from client
        autodiscover_modules(getattr(settings, 'FOREST', {}).get('CONFIG_DIR', os.getenv('CONFIG_DIR', 'forest')))

    @classmethod
    def handle_json_api_serializer(cls):
        for collection in cls.schema['collections']:
            # Notice: create marshmallow-jsonapi resource for json api serializer
            create_json_api_schema(collection)
