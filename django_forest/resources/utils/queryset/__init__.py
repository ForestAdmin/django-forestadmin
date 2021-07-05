from .filters import FiltersMixin
from .limit_fields import LimitFieldsMixin
from .pagination import PaginationMixin
from .search import SearchMixin
from django_forest.resources.utils.decorators import DecoratorsMixin


class QuerysetMixin(PaginationMixin, FiltersMixin, SearchMixin, DecoratorsMixin, LimitFieldsMixin):
    def filter_queryset(self, queryset, Model, params):
        # filters
        if 'filters' in params:
            queryset = queryset.filter(self.get_filters(params, Model))

        # search
        if 'search' in params and params['search']:
            queryset = queryset.filter(self.get_search(params, Model))

        return queryset

    def enhance_queryset(self, queryset, Model, params):
        # filter + search
        queryset = self.filter_queryset(queryset, Model, params)

        # sort
        if 'sort' in params:
            queryset = queryset.order_by(params['sort'].replace('.', '__'))

        # limit fields
        queryset = self.handle_limit_fields(params, Model, queryset)

        # pagination
        queryset = self.get_pagination(params, queryset)

        return queryset
