from django_forest.utils.collection import Collection
from django_forest.utils.schema import Schema


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

    def handle_smart_fields(self, queryset, resource, many=False):
        collection = Schema.get_collection(resource)
        smart_fields = [x for x in collection['fields'] if x['is_virtual']]
        if many:
            for item in queryset:
                self._add_smart_fields(item, smart_fields, resource)
        else:
            self._add_smart_fields(queryset, smart_fields, resource)

    def update_smart_fields(self, instance, body, resource):
        collection = Schema.get_collection(resource)
        smart_fields = [x for x in collection['fields'] if x['is_virtual']]
        for smart_field in smart_fields:
            if smart_field['field'] in body['data']['attributes'].keys():
                value = body['data']['attributes'][smart_field['field']]
                instance = self._handle_set_method(smart_field, instance, value, resource)
        return instance
