from django_forest.utils.collection import Collection
from django_forest.utils.schema import Schema
from django_forest.resources.utils.query_parameters import parse_qs

class SmartFieldMixin:
    def _handle_get_method(self, smart_field, item, resource):
        if 'get' in smart_field:
            method = smart_field['get']
            if isinstance(method, str):
                setattr(item, smart_field['field'], getattr(Collection._registry[resource], method)(item))
            elif callable(method):
                setattr(item, smart_field['field'], method(item))

    def _handle_set_method(self, smart_field, instance, value, resource):
        if 'set' in smart_field:
            method = smart_field['set']
            if isinstance(method, str):
                instance = getattr(Collection._registry[resource], method)(instance, value)
            elif callable(method):
                instance = method(instance, value)
        return instance

    def _add_smart_fields(self, item, smart_fields, resource):
        for smart_field in smart_fields:
            self._handle_get_method(smart_field, item, resource)

    def _handle_nested_smart_fields(self, related_item, fields):
        if related_item:
            related_resource = related_item._meta.db_table
            related_collection = Schema.get_collection(related_resource)
            related_smart_fields = [x for x in related_collection['fields'] if x['is_virtual']]
            if not isinstance(fields, list):
                fields = [fields]
            for smart_field_name in fields:
                smart_field = list(filter(lambda x: x['field'] == smart_field_name, related_smart_fields))
                if smart_field:
                    self._handle_get_method(smart_field[0], related_item, related_resource)

    def handle_nested_smart_fields(self, item, resource, qs):
        for relation, fields in qs['fields'].items():
            if relation != resource:
                try:
                    related_item = getattr(item, relation)
                except AttributeError:
                    pass
                else:
                    self._handle_nested_smart_fields(related_item, fields)

    def handle_smart_fields(self, queryset, resource, qs=None, many=False):
        if qs is None:
            qs = {}
        qs = parse_qs(qs)
        collection = Schema.get_collection(resource)
        smart_fields = [x for x in collection['fields'] if x['is_virtual']]
        if many:
            for item in queryset:
                self._add_smart_fields(item, smart_fields, resource)
                self.handle_nested_smart_fields(item, resource, qs)
        else:
            self._add_smart_fields(queryset, smart_fields, resource)
            self.handle_nested_smart_fields(queryset, resource, qs)

    def update_smart_fields(self, instance, body, resource):
        collection = Schema.get_collection(resource)
        smart_fields = [x for x in collection['fields'] if x['is_virtual']]
        for smart_field in smart_fields:
            if smart_field['field'] in body['data']['attributes'].keys():
                value = body['data']['attributes'][smart_field['field']]
                instance = self._handle_set_method(smart_field, instance, value, resource)
        return instance
