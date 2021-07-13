from .filters import FiltersMixin
from .limit_fields import LimitFieldsMixin
from .pagination import PaginationMixin
from .search import SearchMixin
from django_forest.resources.utils.decorators import DecoratorsMixin


class QuerysetMixin(PaginationMixin, FiltersMixin, SearchMixin, DecoratorsMixin, LimitFieldsMixin):

    def filter_queryset(self, queryset, Model, params):
        PARAMS = {
            'filters': self.get_filters,
            'search': self.get_search,
        }
        for name, method in PARAMS.items():
            if name in params and params[name]:
                queryset = queryset.filter(method(params, Model))
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
