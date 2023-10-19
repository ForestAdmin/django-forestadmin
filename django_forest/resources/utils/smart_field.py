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

    def _get_smart_fields_for_request(self, collection, params=None):

        fields = [field for field in collection['fields'] if field['is_virtual']]

        if params is None:
            return fields

        filtered_fields = params.get('fields', {}).get(collection.get('name'))
        if filtered_fields is None:
            return fields

        return [field for field in fields if field['field'] in filtered_fields]

    def handle_smart_fields(self, queryset, resource, params=None, many=False, follow_relations=True):
        collection = Schema.get_collection(resource)

        # Rather than calculate and then filter out smart fields, we want to ignore them entirely
        smart_fields = self._get_smart_fields_for_request(collection, params)

        # Don't bother adding anything if there are no smart fields
        if smart_fields and many:
            for item in queryset:
                self._add_smart_fields(item, smart_fields, resource)
        elif smart_fields:
            self._add_smart_fields(queryset, smart_fields, resource)

        # handle smart fields on nested relations (call handle_smart_fields recursively)
        if follow_relations is True:
            self._handle_smart_field_on_relations(queryset, collection, params, many)

    def _handle_smart_field_on_relations(self, queryset, base_collection, params, many):
        relations = self.__get_relations_for_smart_fields(base_collection, params)
        for relation_field in relations:
            collection_name = relation_field["reference"].split(".")[0]

            transformed_params = None
            if params:
                transformed_params = {
                    "fields": {
                        collection_name: [params.get("fields", {}).get(relation_field["field"])]
                    }
                }
            self._handle_smart_field_for_relation(queryset, relation_field, collection_name, transformed_params, many)

    def _handle_smart_field_for_relation(self, queryset, relation_field, collection_name, params, many):
        if many:
            for item in queryset:
                if getattr(item, relation_field["field"], None) is not None:
                    self.handle_smart_fields(
                        getattr(item, relation_field["field"]), collection_name, params, False, False
                    )
        else:
            if getattr(queryset, relation_field["field"], None) is not None:
                self.handle_smart_fields(
                    getattr(queryset, relation_field["field"]), collection_name, params, False, False
                )

    def __get_relations_for_smart_fields(self, base_collection, params):
        relations = [
            field
            for field in base_collection["fields"]
            if field["relationship"] is not None and field["relationship"] in ["BelongsTo", "HasOne"]
        ]
        # filter with asked fields in params (if set)
        if params is not None:
            relations = [
                rel for rel in relations
                if rel["field"] in params.get("fields", {}).keys()
            ]
        return relations

    def update_smart_fields(self, instance, body, resource):
        collection = Schema.get_collection(resource)
        smart_fields = [x for x in collection['fields'] if x['is_virtual']]
        for smart_field in smart_fields:
            if smart_field['field'] in body['data']['attributes'].keys():
                value = body['data']['attributes'][smart_field['field']]
                instance = self._handle_set_method(smart_field, instance, value, resource)
        return instance
