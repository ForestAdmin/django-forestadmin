from .in_search_fields import in_search_fields
from django_forest.utils.schema import Schema


class DecoratorsMixin:
    def get_fields_for_decorator_search(self, collection):
        fields_to_search = []
        for x in collection['fields']:
            if x['type'] in ('String', 'Number', 'Enum') \
                    and not x['reference'] \
                    and in_search_fields(x['field'], collection['search_fields']):
                fields_to_search.append(x)
        return fields_to_search

    def handle_search_decorator_field(self, field, record, data, search):
        if field['field'] in record['attributes'] \
           and search.upper() in str(record['attributes'][field['field']]).upper():
            decorator_instance = next((x for x in self.get_meta_decorators(data) if x['id'] == record['id']), None)
            if decorator_instance is None:
                self.get_meta_decorators(data).append({
                    'id': record['id'],
                    'search': [field['field']]
                })
            else:
                decorator_instance['search'].append(field['field'])

    def handle_search_decorator(self, data, Model, search):
        collection = Schema.get_collection(Model._meta.db_table)
        fields_to_search = self.get_fields_for_decorator_search(collection)

        for record in data['data']:
            for field in fields_to_search:
                self.handle_search_decorator_field(field, record, data, search)

    def get_meta_decorators(self, data):
        if 'meta' not in data or 'decorators' not in data['meta']:
            data['meta'] = {
                'decorators': []
            }
        return data['meta']['decorators']

    def decorators(self, data, Model, params):
        if 'search' in params and params['search']:
            self.handle_search_decorator(data, Model, params['search'])

        return data
