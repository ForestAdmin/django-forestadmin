import re

import marshmallow as ma
from marshmallow.schema import SchemaMeta
from marshmallow_jsonapi import Schema, fields
from django.core.exceptions import FieldDoesNotExist
from django_forest.utils.models import Models
from django_forest.utils.type_mapping import get_type


TYPE_CHOICES = {
    'String': fields.Str,
    'Integer': fields.Integer,
    'Float': fields.Float,
    'Number': fields.Number,
    'Boolean': fields.Boolean,
    'Dateonly': fields.Date,
    'Date': fields.DateTime,
    'Time': fields.Time,
    'Json': fields.Raw,
}


class JsonApiSchema(type):
    _registry = {}

    def __new__(mcs, model_name, bases, attrs):
        klass = super(JsonApiSchema, mcs).__new__(mcs, model_name, bases, attrs)
        mcs._registry[model_name] = klass
        return klass

    @classmethod
    def get(mcs, model_name):
        model_name = f'{model_name}Schema'
        if model_name in mcs._registry:
            return mcs._registry[model_name]
        raise Exception(f'The {model_name} does not exist in the JsonApiSchema. Make sure you correctly set it.')


# Notice: handle metaclass conflict
class MarshmallowType(JsonApiSchema, SchemaMeta):
    pass


def get_type_name(name):
    return re.sub(r'(\w)([A-Z])', r'\1 \2', name)


def get_marshmallow_field(field, Model):
    # Notice, handle Model is None (Smart Collection)
    model_fields = [] if Model is None else Model._meta.get_fields()

    # Notice, handle smart field, default to type
    _type = next((get_type(x) for x in model_fields if x.name == field['field']), field['type'])

    if isinstance(_type, list):
        return fields.List(TYPE_CHOICES.get(_type[0], fields.Str)())
    return TYPE_CHOICES.get(_type, fields.Str)()


class DjangoRelationship(fields.Relationship):

    def _serialize(self, value, attr, obj):
        if value and self.many:
            value = value.all()
        return super(DjangoRelationship, self)._serialize(value, attr, obj)


def populate_attrs(collection, collection_name):
    Model = Models.get(collection_name)
    attrs = {}
    for field in collection['fields']:
        field_name = field['field']
        if field['reference'] is not None:
            related_name = field['reference'].split('.')[0]
            attrs[field_name] = DjangoRelationship(
                type_=get_type_name(related_name).lower(),
                many=field['relationship'] == 'HasMany',
                schema=f'{related_name}Schema',
                related_url=f'/forest/{collection_name}/{{{collection_name.lower()}_id}}/relationships/{field_name}',
                related_url_kwargs={f'{collection_name.lower()}_id': '<pk>'},
                id_field='pk'
            )
        else:
            attrs[field_name] = get_marshmallow_field(field, Model)
    return attrs


# override Marshmallow Schema for Django needs
class DjangoSchema(Schema):

    def __init__(self, *args, **kwargs):
        self.include_data = kwargs.pop("include_data", ())
        super(Schema, self).__init__(*args, **kwargs)
        if self.include_data:
            self.check_relations(self.include_data)

        if not self.opts.type_:
            raise ValueError("Must specify type_ class Meta option")

        if self.opts.self_url_kwargs and not self.opts.self_url:
            raise ValueError(
                "Must specify `self_url` Meta option when "
                "`self_url_kwargs` is specified"
            )
        self.included_data = {}
        self.document_meta = {}

    def format_item(self, item):
        ret = super(DjangoSchema, self).format_item(item)
        if ret and self._original:
            ret['id'] = self._original.pk
        return ret

    def format_items(self, data, many):
        if many:
            res = []
            queryset = self._original
            for i, item in enumerate(data):
                self._original = queryset[i]
                res.append(self.format_item(item))
        else:
            res = super(DjangoSchema, self).format_items(data, many)
        return res

    @ma.post_dump(pass_many=True, pass_original=True)
    def format_json_api_response(self, data, original, many):
        self._original = original  # needed to get the id value
        return super(DjangoSchema, self).format_json_api_response(data, many)

    def cast_value(self, field, value):
        return field.get_prep_value(value)

    def get_attribute(self, obj, attr, default):
        value = super().get_attribute(obj, attr, default)
        if value.__class__.__name__ == 'ManyRelatedManager':
            value = value.all()
        else:
            try:
                field = obj.__class__._meta.get_field(attr)
            except FieldDoesNotExist:
                pass
            else:
                if not field.is_relation:
                    value = self.cast_value(field, value)

        return value

    def get_resource_links(self, item):
        id_attr = self._original._meta.pk.attname
        field = self._original._meta.get_field(id_attr)
        item['__id__'] = self.cast_value(field, self._original.pk)
        res = super(DjangoSchema, self).get_resource_links(item)
        del item['__id__']
        return res

def create_json_api_schema(collection):
    collection_name = collection['name']
    attrs = populate_attrs(collection, collection_name)

    class MarshmallowSchema(DjangoSchema):

        class Meta:
            type_ = get_type_name(collection_name).lower()
            self_url = f'/forest/{collection_name}/{{{collection_name.lower()}_id}}'
            self_url_kwargs = {f'{collection_name.lower()}_id': '<__id__>'}
            strict = True

    return MarshmallowType(f'{collection_name}Schema', (MarshmallowSchema,), attrs)
