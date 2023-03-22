from django.apps import apps
from django_forest.utils.schema import Schema
from django_forest.utils.schema.json_api_schema import JsonApiSchema
from django_forest.resources.utils.query_parameters import parse_qs

class JsonApiSerializerMixin:

    def get_smart_relationships(self, fields):
        return [x['field'] for x in fields
                if x['is_virtual'] and x['reference'] and not isinstance(x['type'], list)]

    def get_include_data(self, fields):
        relationships = [x['field'] for x in fields if x['reference'] and x['relationship'] in ['BelongsTo', 'HasOne']]
        smart_relationships = self.get_smart_relationships(fields)
        return relationships + smart_relationships

    def serialize_field(self, field, parent=None):
        res = field['field']
        if field['is_virtual'] and field['reference']:
            field_name = field['field']
            target_key = field['reference'].split('.')[1]
            res = f'{field_name}.{target_key}'
        if parent:
            res = f'{parent}.{res}'
        return res

    def build_only(self, fields, current_name):
        only = [self.serialize_field(f) for f in fields.pop(current_name)]
        for collection_name, fields in fields.items():
            name = collection_name
            only += [self.serialize_field(f, name) for f in fields]
            only.remove(name)
        return only

    def get_fields_for_collection(self, collection, required_fields=None):
        collection_fields = collection['fields']
        if required_fields:
            collection_fields = list(
                filter(
                    lambda f: f['field'] in required_fields,
                    collection_fields
                )
            )
            Model = next(filter(lambda m: m._meta.db_table == collection['name'], apps.get_models()))
            pk_field = Model._meta.pk
            if 'id' in required_fields and pk_field.name != 'id':
                pk_field = next(filter(lambda f: f['field'] == pk_field.name, collection['fields']))
                collection_fields.append(pk_field)
        return collection_fields

    def build_nested_fields(self, field, required_fields):
        if not field['is_virtual']:
            if not isinstance(required_fields, list):
                required_fields = [required_fields]  # need if only one field in the qs

            nested_name = field['reference'].split('.')[0]
            return self.get_fields_for_collection(
                Schema.get_collection(nested_name),
                required_fields
            )

    def get_fields(self, current_collection, qs):
        current_name = current_collection['name']
        qs_fields = qs.get('fields')
        if not qs_fields:
            return {
                f'{current_name}': self.get_fields_for_collection(
                    current_collection
                )
            }
        fields = {
            f"{current_name}": self.get_fields_for_collection(
                current_collection,
                qs_fields.get(current_name),
            )
        }
        for field in fields[current_name]:
            nested_required_fields = qs_fields.get(field['field'])
            if nested_required_fields:
                res = self.build_nested_fields(
                    field,
                    nested_required_fields
                )
                if res:
                    fields[field['field']] = res
        return fields

    def serialize(self, queryset, Model, params):
        db_name = Model._meta.db_table
        current_collection = Schema.get_collection(db_name)
        JsonSchema = JsonApiSchema.get(db_name)
        qs = parse_qs(params)
        fields = self.get_fields(current_collection, qs)
        kwargs = {
            'include_data': self.get_include_data(fields[db_name])
        }

        if db_name in qs.get('fields', {}):
            kwargs['only'] = self.build_only(fields, db_name)

        data = {'data': []}
        if queryset:
            data = JsonSchema(**kwargs).dump(queryset, many=True)
        return data
