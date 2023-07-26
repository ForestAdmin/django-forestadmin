import copy
import json
import os
import logging

import django
from django.conf import settings
from django.db import connection
from django.utils.module_loading import autodiscover_modules

from django_forest.utils.schema.apimap_errors import APIMAP_ERRORS
from django_forest.utils.models import Models
from django_forest.utils.type_mapping import get_type
from django_forest.utils.schema.json_api_schema import create_json_api_schema
from django_forest.utils.forest_api_requester import ForestApiRequester
from .definitions import COLLECTION, FIELD
from .validations import handle_validations
from .enums import handle_enums
from .default import handle_default_value

from .version import get_app_version

from .. import get_accessor_name
from ..forest_setting import get_forest_setting

# Get an instance of a logger
logger = logging.getLogger(__name__)


class Schema:
    schema = {
        'collections': [],
        'meta': {
            'liana': 'django-forestadmin',
            'liana_version': get_app_version(),
            'stack': {
                'database_type': connection.vendor,
                'orm_version': django.get_version(),
            }
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
            if field.related_model not in Models.list():
                return None

            many = field.one_to_many or field.many_to_many
            f['field'] = get_accessor_name(field)
            f['type'] = cls._get_relation_type(many)
            f['relationship'] = cls._get_relationship(field)
            # Notice: forest-rails always put id on the end (it should not), do we handle polymorphic support?
            f['reference'] = f'{field.related_model._meta.db_table}.{field.target_field.column}'
            f['is_filterable'] = not many
            f['inverse_of'] = get_accessor_name(field.remote_field)
        return f

    @staticmethod
    def get_type(field):
        type = get_type(field)
        if type in ('Integer', 'Float'):
            return 'Number'
        return type

    @classmethod
    def add_fields(cls, model, collection):
        for field in model._meta.get_fields():
            f = cls.get_default({
                'field': field.name,
                'type': cls.get_type(field),
                'is_primary_key': model._meta.pk.name == field.name,
            }, FIELD)
            f = handle_default_value(field, f)
            f = handle_validations(field, f)
            f = handle_enums(field, f)
            f = cls.handle_relation(field, f)

            if f is not None:
                collection['fields'].append(f)

    @classmethod
    def build_schema(cls):
        cls.schema['collections'] = []
        for model in Models.list():
            collection = cls.get_default({'name': model._meta.db_table}, COLLECTION)
            cls.add_fields(model, collection)
            cls.schema['collections'].append(collection)
        return cls.schema

    @staticmethod
    def add_smart_features():
        # Notice: will load all files in <app>/forest folder from client
        autodiscover_modules(get_forest_setting('CONFIG_DIR', 'forest'))

    @classmethod
    def handle_json_api_schema(cls):
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
            fields = list(FIELD.keys()) + ['validations', 'enums']
            collection['fields'][index] = {x: field[x] for x in field if x in fields}
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
    def handle_data(r):
        try:
            data = r.json()
        except Exception:
            pass
        else:
            if 'warning' in data:
                logger.warning(data['warning'])

    @classmethod
    def handle_status_code(cls, r):
        if r.status_code in (200, 202, 204):
            cls.handle_data(r)
        elif r.status_code in APIMAP_ERRORS.keys():
            getattr(logger, APIMAP_ERRORS[r.status_code]['level'])(APIMAP_ERRORS[r.status_code]['message'])
        else:
            getattr(logger, APIMAP_ERRORS['error']['level'])(APIMAP_ERRORS['error']['message'])

    @classmethod
    def send_apimap(cls):
        disable_auto_schema_apply = get_forest_setting('FOREST_DISABLE_AUTO_SCHEMA_APPLY', False)
        if not disable_auto_schema_apply:
            try:
                serialized_schema = cls.get_serialized_schema()
                url = ForestApiRequester.build_url('forest/apimaps')
                r = ForestApiRequester.post(url, serialized_schema)
            except Exception:
                logger.warning('Cannot send the apimap to Forest. Are you online?')
            else:
                cls.handle_status_code(r)
