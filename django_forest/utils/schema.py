import copy
import json
import os
import sys
import logging
import django
from django.conf import settings
from django.db import connection
from django.utils.module_loading import autodiscover_modules

from django_forest.utils.apimap_errors import APIMAP_ERRORS
from django_forest.utils.models import Models
from django_forest.utils.get_type import get_type
from django_forest.utils.json_api_serializer import create_json_api_schema
from django_forest.utils.to_bool import to_bool

if sys.version_info >= (3, 8):
    from importlib import metadata
else:
    import importlib_metadata as metadata

from django_forest.utils.forest_api_requester import ForestApiRequester

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

ACTION = {
    'name': '',
    'type': 'bulk',
    'baseUrl': None,
    'endpoint': '',
    'httpMethod': 'POST',
    'redirect': None,
    'download': False,
    'fields': [],
    'hooks': {
        'load': False,
        'change': []
    }
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

    @staticmethod
    def get_default(obj, definition):
        for key, value in copy.deepcopy(definition).items():
            obj[key] = value if key not in obj else obj[key]

        return obj

    @staticmethod
    def _get_relation_type(many):
        if many:
            return ['Number']
        return 'Number'

    @staticmethod
    def _get_relationship(field):
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
            f = cls.get_default({
                'field': field.name,
                'type': get_type(field)
            }, FIELD)
            f = cls.handle_relation(field, f)

            if f is not None:
                collection['fields'].append(f)

    @classmethod
    def build_schema(cls):
        for model in Models.list():
            collection = cls.get_default({'name': model.__name__}, COLLECTION)
            cls.add_fields(model, collection)
            cls.schema['collections'].append(collection)
        return cls.schema

    @staticmethod
    def add_smart_features():
        # Notice: will load all files in <app>/forest folder from client
        autodiscover_modules(getattr(settings, 'FOREST', {}).get('CONFIG_DIR', os.getenv('CONFIG_DIR', 'forest')))

    @classmethod
    def handle_json_api_serializer(cls):
        for collection in cls.schema['collections']:
            # Notice: create marshmallow-jsonapi resource for json api serializer
            create_json_api_schema(collection)

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

    @staticmethod
    def get_serialized_collection(collection):
        for index, field in enumerate(collection['fields']):
            collection['fields'][index] = {x: field[x] for x in field if x in FIELD.keys()}
        return collection

    @classmethod
    def handle_schema_file(cls):
        file_path = os.path.join(os.getcwd(), '.forestadmin-schema.json')
        if settings.DEBUG:
            cls.schema_data = copy.deepcopy(cls.schema)
            for index, collection in enumerate(cls.schema_data['collections']):
                cls.schema_data['collections'][index] = cls.get_serialized_collection(collection)

            with open(file_path, 'w') as f:
                f.write(json.dumps(cls.schema_data, indent=2))
        else:
            cls.handle_schema_file_production(file_path)

    @staticmethod
    def get_serialized_collection_relation(collection, rel_type):
        data = []
        included = []
        for rel in collection[rel_type]:
            id = f"{collection['name']}.{rel['name']}"
            data.append({'id': id, 'type': rel_type})
            included.append({
                'id': id,
                'type': rel_type,
                'attributes': rel
            })
        return data, included

    @classmethod
    def get_serialized_schema(cls):
        data = []
        included = []
        for collection in copy.deepcopy(cls.schema_data['collections']):
            actions_data, actions_included = cls.get_serialized_collection_relation(collection, 'actions')
            segments_data, segments_included = cls.get_serialized_collection_relation(collection, 'segments')
            c = {
                'id': collection['name'],
                'type': 'collections',
                'attributes': cls.get_serialized_collection(collection),
                'relationships': {
                    'actions': {
                        'data': actions_data
                    },
                    'segments': {
                        'data': segments_data
                    }
                }
            }
            data.append(c)
            included.extend(actions_included)
            included.extend(segments_included)

        return {
            'data': data,
            'included': included,
            'meta': cls.schema_data['meta']
        }

    @staticmethod
    def handle_apimap_error(status):
        if APIMAP_ERRORS[status]['level'] == 'warning':
            logger.warning(APIMAP_ERRORS[status]['message'])
        else:
            logger.error(APIMAP_ERRORS[status]['message'])

    @classmethod
    def _send_apimap(cls):
        serialized_schema = cls.get_serialized_schema()
        r = ForestApiRequester.post('forest/apimaps', serialized_schema)
        if r.status_code in (200, 202, 204):
            r = r.json()
            if 'warning' in r:
                logger.warning(r['warning'])
        elif r.status_code in APIMAP_ERRORS.keys():
            cls.handle_apimap_error(r.status_code)
        else:
            logger.error(
                'An error occured with the apimap sent to Forest. Please contact support@forestadmin.com for further investigations.')  # noqa E501

    @classmethod
    def send_apimap(cls):
        disable_auto_schema_apply = getattr(settings, 'FOREST', {}) \
            .get('FOREST_DISABLE_AUTO_SCHEMA_APPLY', to_bool(os.getenv('FOREST_DISABLE_AUTO_SCHEMA_APPLY', False)))
        if not disable_auto_schema_apply:
            cls._send_apimap()
