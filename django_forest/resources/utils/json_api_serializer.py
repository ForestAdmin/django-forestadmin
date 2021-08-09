from django_forest.utils.schema import Schema
from django_forest.utils.schema.json_api_schema import JsonApiSchema


class JsonApiSerializerMixin:
    def get_pk_name(self, Model):
        if Model._meta.pk.name != 'id':
            return 'pk'
        return 'id'

    def compute_only(self, only, field_name, params, Model):
        collection = Schema.get_collection(Model._meta.db_table)
        field = next((x for x in collection['fields'] if x['field'] == field_name), None)
        if field is not None:
            if field['is_virtual']:
                pk_name = field['reference'].split('.')[1]
                only.append(f'{field_name}.{pk_name}')
                only.remove(field_name)
            else:
                only += [f'{field_name}.{y}' for y in params[f'fields[{field_name}]'].split(',')]
                pk_name = self.get_pk_name(Model._meta.get_field(field_name).related_model)
                only.append(f'{field_name}.{pk_name}')
                only.remove(field_name)
        return only

    def get_deep_only(self, params, Model):
        only = params[f'fields[{Model._meta.db_table}]'].split(',')
        sub_only = [x for x in only if f'fields[{x}]' in params]
        for field_name in sub_only:
            only = self.compute_only(only, field_name, params, Model)
        return only

    def get_smart_relationships(self, resource):
        collection = Schema.get_collection(resource)
        return [x['field'] for x in collection['fields']
                if x['is_virtual'] and x['reference'] and not isinstance(x['type'], list)]

    def get_only(self, params, Model):
        only = []
        lookup = f'fields[{Model._meta.db_table}]'
        if lookup in params:
            only = self.get_deep_only(params, Model)
        if 'context[field]' in params:
            fields_and_relationships = [x.name for x in Model._meta.get_fields()
                                        if not x.is_relation or (x.many_to_one or x.one_to_one)]
            smart_relationships = self.get_smart_relationships(Model._meta.db_table)
            only = fields_and_relationships + smart_relationships

        if 'id' not in only:
            pk_name = self.get_pk_name(Model)
            only.append(pk_name)

        return only

    def get_include_data(self, Model):
        relationships = [x.name for x in Model._meta.get_fields() if x.is_relation and (x.many_to_one or x.one_to_one)]
        smart_relationships = self.get_smart_relationships(Model._meta.db_table)
        return relationships + smart_relationships

    def serialize(self, queryset, Model, params):
        Schema = JsonApiSchema._registry[f'{Model._meta.db_table}Schema']

        kwargs = {
            'include_data': self.get_include_data(Model)
        }

        if f'fields[{Model._meta.db_table}]' in params or 'context[field]' in params:
            kwargs['only'] = self.get_only(params, Model)

        if not queryset:
            data = {'data': []}
        else:
            data = Schema(**kwargs).dump(queryset, many=True)

        return data
