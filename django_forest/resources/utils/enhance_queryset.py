import sys

from django.db.models import Q

from .filters import FiltersMixin
from .pagination import PaginationMixin
from ...utils.schema import Schema


class EnhanceQuerysetMixin(PaginationMixin, FiltersMixin):
    def enhance_queryset(self, queryset, params, Model, resource):
        # filters
        if 'filters' in params:
            queryset = self.get_filters(params, Model)

        # search
        # handle search_fields for excluding from collection
        if 'search' in params and params['search']:
            search = params['search']
            collection = Schema.get_collection(resource)
            fields_to_search = [x for x in collection['fields'] if not x['reference'] and not x['is_virtual'] and x['field'] not in collection['search_fields']]
            q_objects = Q()
            for field in fields_to_search:
                is_number = True
                try:
                    search = int(search)
                except ValueError:
                    is_number = False
                if field['type'] == 'Number' and is_number and search <= sys.maxsize:
                    q_objects |= Q(**{field['field']: search})
                else:
                    q_objects |= Q(**{f"{field['field']}__contains": search})
            queryset = queryset.filter(q_objects)

        # sort
        if 'sort' in params:
            queryset = queryset.order_by(params['sort'].replace('.', '__'))

        # limit fields
        legal_fields_name = [x.name for x in Model._meta.get_fields()]
        queryset = queryset.only(*[x for x in params[f'fields[{Model.__name__}]'].split(',') if x in legal_fields_name])

        # pagination
        _from, _to = self.get_pagination(params)
        return queryset[_from:_to]
