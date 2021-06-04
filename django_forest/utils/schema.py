import copy
import json
import os
import sys
import logging
import django
from django.conf import settings
from django.db import connection
from django.utils.module_loading import autodiscover_modules

from django_forest.utils.models import Models
from django_forest.utils.get_type import get_type
from django_forest.utils.json_api_serializer import create_json_api_schema

if sys.version_info >= (3, 8):
    from importlib import metadata
else:
    import importlib_metadata as metadata

# Get an instance of a logger
logger = logging.getLogger(__name__)

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

    # schema to send to Forest Admin Server
    schema_data = None

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
            if field.target_field.model not in Models.list():
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
        for model in Models.list():
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

    @classmethod
    def get_serialized_collection(cls, collection):
        for index, field in enumerate(collection['fields']):
            collection['fields'][index] = {x: field[x] for x in field if x in FIELD.keys()}
        return collection

    @classmethod
    def handle_schema_file_production(cls, file_path):
        try:
            with open(file_path, 'r') as f:
                data = f.read()
                try:
                    cls.schema_data = json.loads(data)
                except Exception:
                    logger.error('The content of .forestadmin-schema.json file is not a correct JSON.')
                    logger.error('The schema cannot be synchronized with Forest Admin servers.')
        except Exception:
            logger.error('The .forestadmin-schema.json file does not exist.')
            logger.error('The schema cannot be synchronized with Forest Admin servers.')

    @classmethod
    def handle_schema_file(cls):
        file_path = os.path.join(os.getcwd(), '.forestadmin-schema.json')
        if settings.DEBUG:
            schema = copy.deepcopy(cls.schema)
            for index, collection in enumerate(schema['collections']):
                schema['collections'][index] = cls.get_serialized_collection(collection)

            cls.schema_data = json.dumps(schema, indent=2)
            with open(file_path, 'w') as f:
                f.write(cls.schema_data)
        else:
            cls.handle_schema_file_production(file_path)
