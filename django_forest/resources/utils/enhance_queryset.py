from .filters import FiltersMixin
from .pagination import PaginationMixin


class EnhanceQuerysetMixin(PaginationMixin, FiltersMixin):
    def enhance_queryset(self, queryset, params, Model):
        # filters
        if 'filters' in params:
            queryset = self.get_filters(params, Model)

        # search
        # TODO

        # sort
        if 'sort' in params:
            queryset = queryset.order_by(params['sort'].replace('.', '__'))

        # limit fields
        legal_fields_name = [x.name for x in Model._meta.get_fields()]
        queryset = queryset.only(*[x for x in params[f'fields[{Model.__name__}]'].split(',') if x in legal_fields_name])

        # pagination
        _from, _to = self.get_pagination(params)
        return queryset[_from:_to]
