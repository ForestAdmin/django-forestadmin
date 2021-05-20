from marshmallow.schema import SchemaMeta
from marshmallow_jsonapi import Schema, fields
from marshmallow_jsonapi.fields import Relationship


class JsonApiSchema(type):
    _registry = {}

    def __new__(cls, model_name, bases, attrs):
        klass = super(JsonApiSchema, cls).__new__(cls, model_name, bases, attrs)
        cls._registry[model_name] = klass
        return klass


# Notice: handle metaclass conflict
class MarshmallowType(JsonApiSchema, SchemaMeta):
    pass


def create_json_api_schema(model):

    attrs = {}
    for field in model._meta.get_fields():
        if not field.is_relation:
            attrs[field.name] = fields.Str(dump_only=True)
        else:
            related_name = field.related_model.__name__.lower()
            attrs[field.name] = Relationship(
                include_resource_linkage=True,
                type_=related_name,
                many=field.one_to_many or field.many_to_many,
                schema=f'{field.related_model.__name__}Schema',
                related_url=f'/forest/{model.__name__.lower()}/{{{model.__name__.lower()}_id}}/relationships/{field.name}',
                related_url_kwargs={f'{model.__name__.lower()}_id': '<id>'},
            )

    class MarshmallowSchema(Schema):
        class Meta:
            type_ = model.__name__.lower()
            strict = True

    return MarshmallowType(f'{model.__name__}Schema', (MarshmallowSchema,), attrs)
