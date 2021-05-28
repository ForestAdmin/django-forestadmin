import copy
import json
import os
import sys

from django_forest.utils.json_api_serializer import create_json_api_schema

if sys.version_info >= (3, 8):
    from importlib import metadata
else:
    import importlib_metadata as metadata

import django
from django.apps import apps
from django.conf import settings
from django.db import connection
from django.utils.module_loading import autodiscover_modules

from django_forest.utils.forest_api_requester import ForestApiRequester


TYPE_CHOICES = {
    'AutoField': 'String',
    'BigAutoField': 'Number',
    'BinaryField': 'String',
    'BooleanField': 'Boolean',
    'CharField': 'String',
    'DateField': 'DateOnly',
    'DateTimeField': 'Date',
    'DecimalField': 'Number',
    'DurationField': 'Number',
    'FileField': 'String',
    'FilePathField': 'String',
    'FloatField': 'Number',
    'IntegerField': 'Number',
    'BigIntegerField': 'Number',
    'IPAddressField': 'String',
    'GenericIPAddressField': 'String',
    'JSONField': 'Json',
    'NullBooleanField': 'Boolean',
    'OneToOneField': 'Number',
    'PositiveBigIntegerField': 'Number',
    'PositiveIntegerField': 'Number',
    'PositiveSmallIntegerField': 'Number',
    'SlugField': 'String',
    'SmallAutoField': 'String',
    'SmallIntegerField': 'Number',
    'TextField': 'String',
    'TimeField': 'Time',
    'UUIDField': 'String',
    'CICharField': 'String',
    'CIEmailField': 'String',
    'CITextField': 'String',
    'HStoreField': 'Json',
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


def get_app_version():
    version = '0.0.0'
    try:
        version = metadata.version('django_forest')
    except:
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


    @classmethod
    def get_collection(cls, resource):
        collections = [collection for collection in cls.schema['collections'] if collection['name'] == resource]
        if len(collections):
            return collections[0]

        return None

    @classmethod
    def get_default_field(cls, obj):
        for key, value in copy.deepcopy(FIELD).items():
            obj[key] = value if key not in obj else obj[key]

        return obj

    @classmethod
    def get_default_collection(cls, obj):
        for key, value in copy.deepcopy(COLLECTION).items():
            obj[key] = value if key not in obj else obj[key]

        return obj

    @classmethod
    def build_schema(cls):
        # TODO support included/excluded, smart collection
        models = apps.get_models()
        for model in models:
            collection = cls.get_default_collection({'name': model.__name__})
            for field in model._meta.get_fields():
                f = cls.get_default_field({
                    'field': field.name,
                    'type': cls.get_type(field.get_internal_type())
                })
                if field.is_relation:
                    many = field.one_to_many or field.many_to_many
                    f['type'] = ['Number'] if many else 'Number'  # TODO review, maybe not a Number
                    f['relationship'] = 'HasMany' if many else 'BelongsTo'
                    f['reference'] = f'{field.target_field.model.__name__}.{field.target_field.name}'  # TODO review

                collection['fields'].append(f)
            cls.schema['collections'].append(collection)
        return cls.schema

    @classmethod
    def get_type(cls, field_type):
        # TODO handle Enum
        # handle ArrayField
        # handle 'RangeField', 'IntegerRangeField', 'BigIntegerRangeField',
        #     'DecimalRangeField', 'DateTimeRangeField', 'DateRangeField',
        # See connection.data_types (different for each DB Engine)
        return TYPE_CHOICES.get(field_type, 'default')  # TODO raise error, do not put default

    @classmethod
    def add_smart_features(cls):
        # will load all files in <app>/forest folder from client
        autodiscover_modules('forest')

    @classmethod
    def handle_json_api_serializer(cls):
        for collection in cls.schema['collections']:
            # create marshmallow-jsonapi resource for json api serializer
            # TODO place in a registry
            create_json_api_schema(collection, cls)

    @classmethod
    def handle_schema_file(cls):
        schema = copy.deepcopy(cls.schema)
        for index, collection in enumerate(schema['collections']):
            schema['collections'][index] = cls.get_serialized_collection(collection)

        schema_data = json.dumps(schema, indent=2)
        if settings.DEBUG:
            file_path = os.path.join(os.getcwd(), 'forestadmin-schema.json')
            with open(file_path, 'w') as f:
                f.write(schema_data)
        else:
            # TODO read from file
            pass

    @classmethod
    def get_serialized_collection(cls, collection):
        for index, field in enumerate(collection['fields']):
            collection['fields'][index] = {x: field[x] for x in field if x in FIELD.keys()}
        return collection

    @classmethod
    def get_serialized_schema(cls):
        data = []
        included = []  # TODO
        for collection in copy.deepcopy(cls.schema['collections']):
            # TODO handle actions/segments
            c = {
                'id': collection['name'],
                'type': 'collections',
                'attributes': cls.get_serialized_collection(collection),
                'relationships': {
                    'actions': {
                        'data': []
                    },
                    'segments': {
                        'data': []
                    }
                }
            }
            data.append(c)

        return {
            'data': data,
            'included': included,
            'meta': cls.schema['meta']
        }

    @classmethod
    def send_apimap(cls):
        serialized_schema = cls.get_serialized_schema()
        ForestApiRequester.post('forest/apimaps', serialized_schema)
