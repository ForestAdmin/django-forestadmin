import re

from marshmallow.schema import SchemaMeta
from marshmallow_jsonapi import Schema, fields
from marshmallow_jsonapi.fields import DocumentMeta, ResourceMeta, BaseRelationship
from marshmallow_jsonapi.schema import TYPE

from django_forest.utils.models import Models
from django_forest.utils.type_mapping import get_type


TYPE_CHOICES = {
    'String': fields.Str,
    'Integer': fields.Integer,
    'Float': fields.Float,
    'Number': fields.Number,
    'Boolean': fields.Boolean,
    'DateOnly': fields.Date,
    'Date': fields.DateTime,
    'Time': fields.Time,
    'Json': fields.Dict,  # maybe a fields.Mapping or fields.Raw,
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


def handle_pk_attribute(attrs, Model):
    if 'id' not in attrs:
        attrs['pk'] = TYPE_CHOICES.get(get_type(Model._meta.pk), fields.Str)()
    return attrs


def get_pk_name(collection_name):
    Model = Models.get(collection_name)
    if Model is not None and Model._meta.pk.name != 'id':
        return 'pk'
    return 'id'


def get_marshmallow_field(field, Model):
    # Notice, handle Model is None (Smart Collection)
    model_fields = [] if Model is None else Model._meta.get_fields()

    # Notice, handle smart field, default to type
    _type = next((get_type(x) for x in model_fields if x.name == field['field']), field['type'])

    if isinstance(_type, list):
        return fields.List(TYPE_CHOICES.get(_type[0], fields.Str)())
    return TYPE_CHOICES.get(_type, fields.Str)()


def populate_attrs(collection, collection_name):
    Model = Models.get(collection_name)
    attrs = {}
    for field in collection['fields']:
        field_name = field['field']
        if field['reference'] is not None:
            related_name = field['reference'].split('.')[0]
            attrs[field_name] = fields.Relationship(
                type_=get_type_name(related_name).lower(),
                many=field['relationship'] == 'HasMany',
                schema=f'{related_name}Schema',
                related_url=f'/forest/{collection_name}/{{{collection_name.lower()}_id}}/relationships/{field_name}',
                related_url_kwargs={f'{collection_name.lower()}_id': '<pk>'},
                id_field='pk'
            )
        else:
            attrs[field_name] = get_marshmallow_field(field, Model)

    # Add pk field if id not present
    attrs = handle_pk_attribute(attrs, Model)

    return attrs


# override Marshmallow Schema for Django needs
class DjangoSchema(Schema):
    # Notice override init for not having id error, as we are working with pk
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

    def handle_document_meta(self, value):
        if not self.document_meta:
            self.document_meta = self.dict_class()
        self.document_meta.update(value)

    def handle_resource_meta(self, ret, value):
        if "meta" not in ret:
            ret["meta"] = self.dict_class()
        ret["meta"].update(value)

        return ret

    def handle_relation(self, ret, field_name, value):
        if value:
            if "relationships" not in ret:
                ret["relationships"] = self.dict_class()
            ret["relationships"][self.inflect(field_name)] = value

        return ret

    def handle_default(self, ret, field_name, value):
        if "attributes" not in ret:
            ret["attributes"] = self.dict_class()
        ret["attributes"][self.inflect(field_name)] = value

        return ret

    def handle_attribute(self, ret, attribute, field_name, value):
        # Notice: this part has been overridden for handling pk in django
        if attribute in ('pk', 'id'):
            ret['id'] = value
        elif isinstance(self.fields[attribute], DocumentMeta):
            self.handle_document_meta(value)
        elif isinstance(self.fields[attribute], ResourceMeta):
            ret = self.handle_resource_meta(ret, value)
        elif isinstance(self.fields[attribute], BaseRelationship):
            ret = self.handle_relation(ret, field_name, value)
        else:
            ret = self.handle_default(ret, field_name, value)

        return ret

    def handle_item(self, ret, item, attributes):
        for field_name, value in item.items():
            ret = self.handle_attribute(ret, attributes[field_name], field_name, value)

        return ret

    def format_item(self, item):
        if not item:
            return None

        ret = self.dict_class()
        ret[TYPE] = self.opts.type_

        # Get the schema attributes so we can confirm `dump-to` values exist
        attributes = {
            (self.fields[field].data_key or field): field for field in self.fields
        }

        ret = self.handle_item(ret, item, attributes)

        links = self.get_resource_links(item)
        if links:
            ret['links'] = links
        return ret

    def get_attribute(self, obj, attr, default):
        value = super().get_attribute(obj, attr, default)
        if value.__class__.__name__ == 'ManyRelatedManager':
            value = value.all()
        return value


def create_json_api_schema(collection):
    collection_name = collection['name']
    attrs = populate_attrs(collection, collection_name)

    class MarshmallowSchema(DjangoSchema):
        class Meta:
            type_ = get_type_name(collection_name).lower()
            self_url = f'/forest/{collection_name}/{{{collection_name.lower()}_id}}'
            self_url_kwargs = {f'{collection_name.lower()}_id': f'<{get_pk_name(collection_name)}>'}
            strict = True

    return MarshmallowType(f'{collection_name}Schema', (MarshmallowSchema,), attrs)
