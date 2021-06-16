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
        # TODO

        # pagination
        _from, _to = self.get_pagination(params)
        return queryset[_from:_to]
