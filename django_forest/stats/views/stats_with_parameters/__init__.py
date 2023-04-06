import json

from django_forest.resources.utils.resource import ResourceView
from django_forest.stats.utils.stats import StatsMixin
from django_forest.utils import get_association_field

from .utils import get_annotated_queryset, get_format_time_frame, compute_value, compute_line_values, get_periods, \
    contains_previous_date_operator


class StatsWithParametersView(StatsMixin, ResourceView):
    def compute_data(self, key, value, queryset):
        data = {}
        for x in queryset:
            if x[value] is not None:
                self.fill_data(data, x[key], int(x[value]))
        return [{
            'key': k,
            'value': v
        } for k, v, in data.items()]

    def get_previous_count(self, params, request):
        self.previous = True
        queryset = self.enhance_queryset(self.Model.objects.all(), self.Model, params, request)
        return compute_value(params, queryset)

    def handle_count_previous(self, params, res, request):
        if params['type'] == 'Value' and 'filters' in params:
            filters = json.loads(params['filters'])
            if contains_previous_date_operator(filters):
                res['countPrevious'] = self.get_previous_count(params, request)

    def get_value(self, params, queryset, request):
        value = compute_value(params, queryset)
        key = 'countCurrent'
        if params['type'] == 'Objective':
            key = 'value'

        res = {
            key: value
        }

        # Notice: handle countPrevious
        self.handle_count_previous(params, res, request)

        return res

    def get_pie(self, params, queryset):
        pk_name = self.Model._meta.pk.name
        group_by_field = params['group_by_field'].replace(":", "__")

        queryset = queryset.order_by(group_by_field).values(group_by_field)

        aggregate = params['aggregate'].lower()
        queryset, name = get_annotated_queryset(params, queryset, pk_name)

        return self.compute_data(group_by_field, f'{name}__{aggregate}', queryset)

    def get_line(self, params, queryset):
        pk_name = self.Model._meta.pk.name
        format, time_frame = get_format_time_frame(params)

        group_by_date_field = params['group_by_date_field']
        queryset = queryset.order_by(group_by_date_field).values(group_by_date_field)
        aggregate = params['aggregate'].lower()
        queryset, name = get_annotated_queryset(params, queryset, pk_name)

        try:
            bounds = {
                'earliest': queryset.first().get(group_by_date_field, None),
                'latest': queryset.last().get(group_by_date_field, None)
            }
        except Exception:
            values = []
        else:
            periods = get_periods(queryset, f'{name}__{aggregate}', group_by_date_field, format)
            values = compute_line_values(bounds, periods, time_frame, format)
        return values

    def get_leaderboard(self, params, queryset):
        label_field = params['label_field']
        relationship_field = params['relationship_field']

        queryset = queryset.values(label_field)
        association_field = get_association_field(self.Model, relationship_field)
        pk_name = association_field.related_model._meta.pk.name

        aggregate = params['aggregate'].lower()
        association_field_name = association_field.name

        queryset, name = get_annotated_queryset(params, queryset, pk_name, association_field_name)
        queryset = queryset.order_by(f'-{name}__{aggregate}')
        queryset = queryset[:params['limit']]

        return self.compute_data(label_field, f'{name}__{aggregate}', queryset)

    def post(self, request, *args, **kwargs):
        params = self.get_body(request.body)
        params.update(request.GET.dict())
        queryset = self.Model.objects.all()
        queryset = self.enhance_queryset(queryset, self.Model, params, request)
        return self.chart(params, request, queryset)
