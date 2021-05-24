from marshmallow.schema import SchemaMeta
from marshmallow_jsonapi import Schema, fields
from marshmallow_jsonapi.fields import Relationship


TYPE_CHOICES = {
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


def create_json_api_schema(collection):
    attrs = {}
    collection_name = collection['name']

    for field in collection['fields']:
        if field['reference'] is not None:
            related_name = field['reference'].split('.')[0]
            field_name = field['field']
            attrs[field_name] = Relationship(
                type_=related_name.lower(),
                many=field['relationship'] == 'HasMany',
                schema=f'{collection_name}Schema',
                related_url=f'/forest/{collection_name}/{{{collection_name.lower()}_id}}/relationships/{related_name}',
                related_url_kwargs={f'{collection_name.lower()}_id': '<id>'},
            )
        else:
            attrs[field['field']] = TYPE_CHOICES.get(field['type'], fields.Str)()

    class MarshmallowSchema(Schema):

        # TODO, if we want modify how is returned the data, we need to override format_json_api_response
        # https://marshmallow-jsonapi.readthedocs.io/en/latest/api_reference.html#marshmallow_jsonapi.Schema.format_json_api_response
        # format_items and format_item will need to be updated

        # We add the id in the attributes
        def format_item(self, item):
            ret = super().format_item(item)
            if 'attributes' in ret:
                attributes = {
                    (self.fields[field].data_key or field): field for field in self.fields
                }
                for field_name, value in item.items():
                    attribute = attributes[field_name]
                    if attribute == 'id':
                        ret['attributes']['id'] = value

            return ret

        class Meta:
            type_ = collection_name.lower()
            strict = True

    return MarshmallowType(f'{collection_name}Schema', (MarshmallowSchema,), attrs)
