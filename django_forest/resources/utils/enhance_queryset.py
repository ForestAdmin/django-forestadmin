from .filters import FiltersMixin
from .pagination import PaginationMixin
from .search import SearchMixin


class EnhanceQuerysetMixin(PaginationMixin, FiltersMixin, SearchMixin):
    def enhance_queryset(self, queryset, resource, Model, params):
        # filters
        if 'filters' in params:
            queryset = queryset.filter(self.get_filters(params, Model))

        # search
        if 'search' in params and params['search']:
            queryset = queryset.filter(self.get_search(params, resource, Model))

        # sort
        if 'sort' in params:
            queryset = queryset.order_by(params['sort'].replace('.', '__'))

        # limit fields
        # TODO many to many case
        lookup = f'fields[{Model.__name__}]'
        if lookup in params:
            legal_fields_name = [x.name for x in Model._meta.get_fields()]
            args = []
            for x in params[f'fields[{Model.__name__}]'].split(','):
                if x in legal_fields_name:
                    args.append(x)

            queryset = queryset.only(*args)

        # pagination
        queryset = self.get_pagination(params, queryset)

        return queryset
