from marshmallow.schema import SchemaMeta
from marshmallow_jsonapi import Schema, fields
from marshmallow_jsonapi.fields import Relationship


TYPE_CHOICES = {
    'AutoField': fields.Str,
    'BigAutoField': fields.Number,
    'BinaryField': fields.Str,
    'BooleanField': fields.Boolean,
    'CharField': fields.Str,
    'DateField': fields.Date,
    'DateTimeField': fields.DateTime,
    'DecimalField': fields.Decimal,
    'DurationField': fields.Number,
    'FileField': fields.Str,
    'FilePathField': fields.Str,
    'FloatField': fields.Float,
    'IntegerField': fields.Integer,
    'BigIntegerField': fields.Integer,
    'IPAddressField': fields.Str,
    'GenericIPAddressField': fields.Str,
    'JSONField': fields.Dict,  # maybe a fields.Mapping or fields.Raw
    'NullBooleanField': fields.Boolean,
    'OneToOneField': fields.Number,
    'PositiveBigIntegerField': fields.Integer,
    'PositiveIntegerField': fields.Integer,
    'PositiveSmallIntegerField': fields.Integer,
    'SlugField': fields.Str,
    'SmallAutoField': fields.Str,
    'SmallIntegerField': fields.Integer,
    'TextField': fields.Str,
    'TimeField': fields.Time,
    'UUIDField': fields.Str,
    'CICharField': fields.Str,
    'CIEmailField': fields.Str,
    'CITextField': fields.Str,
    'HStoreField': fields.Dict,  # maybe a fields.Mapping or fields.Raw
}

SMART_TYPE_CHOICES = {
    'String': fields.Str,
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


# Notice: handle metaclass conflict
class MarshmallowType(JsonApiSchema, SchemaMeta):
    pass


def create_json_api_schema(model, ForestSchema):
    attrs = {}
    # TODO handle included/excluded
    for field in model._meta.get_fields():
        if not field.is_relation:
            attrs[field.name] = TYPE_CHOICES.get(field.get_internal_type(), fields.Str)()
        else:
            related_name = field.related_model.__name__
            field_name = field.name
            attrs[field_name] = Relationship(
                type_=related_name.lower(),
                many=field.one_to_many or field.many_to_many,
                schema=f'{field.related_model.__name__}Schema',
                related_url=f'/forest/{model.__name__}/{{{model.__name__.lower()}_id}}/relationships/{related_name}',
                related_url_kwargs={f'{model.__name__.lower()}_id': '<id>'},
            )
    # add smart fields
    collection = ForestSchema.get_collection(model.__name__)
    smart_fields = [f for f in collection['fields'] if f['is_virtual']]
    for field in smart_fields:
        attrs[field['field']] = SMART_TYPE_CHOICES.get(field['type'], fields.Str)()

    class MarshmallowSchema(Schema):
        class Meta:
            type_ = model.__name__.lower()
            strict = True

    return MarshmallowType(f'{model.__name__}Schema', (MarshmallowSchema,), attrs)
