import sys
from distutils.util import strtobool
from uuid import UUID

from django.db.models import Q

from django_forest.utils.collection import Collection
from ..in_search_fields import in_search_fields
from django_forest.utils.schema import Schema


class SearchMixin:
    def get_fields_to_search(self, collection):
        fields_to_search = []
        for x in collection['fields']:
            if x['type'] in ('String', 'Number', 'Enum') \
                    and not x['reference'] \
                    and not x['is_virtual'] \
                    and in_search_fields(x['field'], collection['search_fields']):
                fields_to_search.append(x)
        return fields_to_search

    def is_number(self, search):
        is_number = True
        try:
            search = int(search)
        except ValueError:
            try:
                search = float(search)
            except ValueError:
                is_number = False

        return search, is_number

    def handle_number(self, search, lookup_field):
        q_object = Q()

        search, is_number = self.is_number(search)

        # Notice, only add condition if value is number
        if is_number:
            # Notice: use LIKE operator when too big
            if search <= sys.maxsize:
                q_object = Q(**{lookup_field: search})
            else:
                q_object = Q(**{f'{lookup_field}__contains': search})

        return q_object

    def is_uuid(self, search):
        try:
            UUID(search)
        except ValueError:
            return False
        else:
            return True

    def handle_string(self, search, lookup_field):
        is_uuid = self.is_uuid(search)

        if is_uuid:
            q_object = Q(**{lookup_field: search})
        else:
            q_object = Q(**{f'{lookup_field}__icontains': search})

        return q_object

    def handle_enum(self, search, enums, lookup_field):
        q_object = Q()

        # Notice: only add condition if search in enums
        if search in enums:
            q_object = Q(**{lookup_field: search})

        return q_object

    def get_lookup_field(self, field_name, related_field):
        lookup_field = field_name
        if related_field is not None:
            lookup_field = f'{related_field}__{lookup_field}'
        return lookup_field

    def handle_field(self, search, field, related_field_name=None):
        q_objects = Q()

        lookup_field = self.get_lookup_field(field['field'], related_field_name)
        if field['type'] == 'Enum':
            q_objects |= self.handle_enum(search, field['enums'], lookup_field)
        elif field['type'] == 'Number':
            q_objects |= self.handle_number(search, lookup_field)
        else:
            q_objects |= self.handle_string(search, lookup_field)

        return q_objects

    def handle_search_extended(self, search, Model):
        q_objects = Q()

        related_fields = [x for x in Model._meta.get_fields() if x.is_relation and not x.many_to_many]
        for related_field in related_fields:
            q_objects |= self.fill_conditions(search, related_field.related_model._meta.db_table, related_field.name)

        return q_objects

    def add_smart_field(self, smart_field, resource, search):
        q_object = Q()
        method = smart_field['search']
        if isinstance(method, str):
            q_object = getattr(Collection._registry[resource], method)(search)
        elif callable(method):
            q_object = method(search)
        return q_object

    def add_smart_fields(self, collection, resource, search):
        q_objects = Q()
        smart_fields = [x for x in collection['fields'] if x['is_virtual']]
        for smart_field in smart_fields:
            if 'search' in smart_field:
                q_objects |= self.add_smart_field(smart_field, resource, search)

        return q_objects

    def fill_conditions(self, search, resource, related_field_name=None):
        q_objects = Q()

        collection = Schema.get_collection(resource)
        fields_to_search = self.get_fields_to_search(collection)
        for field in fields_to_search:
            q_objects |= self.handle_field(search, field, related_field_name)

        # Notice handle smart fields
        q_objects |= self.add_smart_fields(collection, resource, search)

        return q_objects

    def get_search(self, params, Model):
        q_objects = Q()
        search = params['search']

        q_objects |= self.fill_conditions(search, Model._meta.db_table)

        if 'searchExtended' in params and strtobool(str(params['searchExtended'])):
            q_objects |= self.handle_search_extended(search, Model)

        return q_objects
