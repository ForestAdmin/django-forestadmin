import re

from .filters import FiltersMixin
from .limit_fields import LimitFieldsMixin
from .pagination import PaginationMixin
from .scope import ScopeMixin
from .search import SearchMixin
from .segment import SegmentMixin
from django_forest.resources.utils.decorators import DecoratorsMixin
from django_forest.utils.schema import Schema


class QuerysetMixin(
    PaginationMixin, FiltersMixin, SearchMixin, ScopeMixin, DecoratorsMixin, LimitFieldsMixin, SegmentMixin
):
    def filter_queryset(self, queryset, Model, params, request):
        # Notice: first apply scope
        scope_filters = self.get_scope(request, Model)
        if scope_filters is not None:
            queryset = queryset.filter(scope_filters)

        # Notice: then apply filters and search
        PARAMS = {
            'filters': self.get_filters,
            'search': self.get_search
        }
        for name, method in PARAMS.items():
            if name in params and params[name]:
                queryset = queryset.filter(method(params, Model))
        return queryset

    def join_relations(self, queryset, Model, params, request):
        select_related = set()

        collection = Schema.get_collection(Model._meta.db_table)
        relations = [
            field['field']
            for field in collection["fields"]
            if field["relationship"] is not None and field["relationship"] in ["BelongsTo", "HasOne"]
        ]

        # projection
        for key, value in params.items():
            if re.search(r"fields\[[^\]]+\]", key):
                fields_for = key.split("fields[")[1][:-1]
                if fields_for in relations:
                    select_related.add(fields_for)

        return queryset.select_related(*select_related)

    def enhance_queryset(self, queryset, Model, params, request, apply_pagination=True):
        # perform inner join
        queryset = self.join_relations(queryset, Model, params, request)

        # scopes + filter + search
        queryset = self.filter_queryset(queryset, Model, params, request)

        # sort
        if 'sort' in params:
            queryset = queryset.order_by(params['sort'].replace('.', '__'))

        # segment
        queryset = self.handle_segment(params, Model, queryset)

        # limit fields
        queryset = self.handle_limit_fields(params, Model, queryset)

        # pagination
        if apply_pagination:
            queryset = self.get_pagination(params, queryset)

        return queryset
