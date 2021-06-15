from django_forest.utils.collection import Collection
from django_forest.utils.schema import Schema


class SmartFieldMixin:
    def _handle_get_method(self, smart_field, item, field, resource):
        if 'get' in smart_field:
            method = smart_field['get']
            if isinstance(method, str):
                setattr(item, field, getattr(Collection._registry[resource], method)(item))
            elif callable(method):
                setattr(item, field, method(item))

    def add_smart_fields(self, item, collection, smart_fields, resource):
        for field in smart_fields:
            smart_field = [x for x in collection['fields'] if x['field'] == field][0]
            self._handle_get_method(smart_field, item, field, resource)

    def handle_smart_fields(self, queryset, resource, Model, many=False):
        collection = Schema.get_collection(resource)
        smart_fields = [x['field'] for x in collection['fields'] if
                        x['field'] not in [x.name for x in Model._meta.get_fields()]]
        if many:
            for item in queryset:
                self.add_smart_fields(item, collection, smart_fields, resource)
        else:
            self.add_smart_fields(queryset, collection, smart_fields, resource)
