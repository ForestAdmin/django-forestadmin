import json
from datetime import timedelta

from dateutil.relativedelta import relativedelta
from django.db.models import Sum

from django_forest.resources.utils import ResourceView
from django_forest.stats.utils import get_annotated_queryset, get_format_time_frame
from django_forest.stats.utils.stats import StatsMixin


class StatWithParametersView(StatsMixin, ResourceView):
    PREVIOUS_DATE_OPERATOR = ['today', 'yesterday',
                              'previous_week', 'previous_month', 'previous_quarter', 'previous_year',
                              'previous_week_to_date', 'previous_month_to_date', 'previous_quarter_to_date',
                              'previous_year_to_date',
                              'previous_x_days', 'previous_x_days_to_date']

    def dispatch(self, request, resource, *args, **kwargs):
        try:
            self.Model = self.get_model(resource)
            self.body = self.get_body(request.body)
            self.body.update(request.GET.dict())
            self.manager = self.Model.objects.all()
            self.queryset = self.enhance_queryset(self.manager, self.Model, self.body)
        except Exception as e:
            return self.error_response(e)
        else:
            return super(ResourceView, self).dispatch(request, *args, **kwargs)

    def compute_value(self, queryset):
        # sum
        if self.body['aggregate'] == 'Sum':
            q = queryset.aggregate(sum=Sum(self.body['aggregate_field']))
            value = q['sum']
            if value is None:
                value = 0
        # count
        else:
            value = queryset.count()

        return value

    def get_previous_count(self):
        self.previous = True
        queryset = self.enhance_queryset(self.manager, self.Model, self.body)
        return self.compute_value(queryset)

    def get_value(self):
        value = self.compute_value(self.queryset)
        key = 'countCurrent'
        if self.body['type'] == 'Objective':
            key = 'value'

        res = {
            key: value
        }

        # Notice: handle countPrevious, check if filter in previous_date_operator
        if self.body['type'] == 'Value' and 'filters' in self.body:
            filters = json.loads(self.body['filters'])
            if filters['operator'] in self.PREVIOUS_DATE_OPERATOR:
                res['countPrevious'] = self.get_previous_count()

        return res

    def get_pie(self):
        pk_name = self.Model._meta.pk.name
        group_by_field = self.body['group_by_field']

        queryset = self.queryset.order_by(group_by_field).values(group_by_field)

        aggregate = self.body['aggregate'].lower()
        queryset, name = get_annotated_queryset(self.body, queryset, pk_name)

        return [{
            'key': self.serialize(x[self.body['group_by_field']]),
            'value': x[f'{name}__{aggregate}']
        } for x in queryset]

    def get_leaderboard(self):
        label_field = self.body['label_field']
        relationship_field = self.body['relationship_field']

        queryset = self.queryset.values(label_field)
        association_field = self.get_association_field(self.Model, relationship_field)
        pk_name = association_field.related_model._meta.pk.name

        aggregate = self.body['aggregate'].lower()
        association_field_name = association_field.name

        queryset, name = get_annotated_queryset(self.body, queryset, pk_name, association_field_name)
        queryset = queryset.order_by(f'-{name}__{aggregate}')
        queryset = queryset[:self.body['limit']]

        return [{
            'key': self.serialize(x[label_field]),
            'value': x[f'{name}__{aggregate}']
        } for x in queryset if x[f'{name}__{aggregate}'] is not None]

    def get_periods(self, queryset, key, group_by_date_field, format):
        periods = {}
        for x in queryset:
            tf_formatted = x.get(group_by_date_field).strftime(format)
            if tf_formatted in periods:
                periods[tf_formatted] += x[key]
            else:
                periods[tf_formatted] = x[key]
        return periods

    def compute_line_values(self, earliest, latest, periods, time_frame):
        keys = periods.keys()
        values = []
        date = earliest
        while date < latest + timedelta(days=1):
            value = 0
            tf_formatted = date.strftime(format)
            if tf_formatted in keys:
                value = periods[tf_formatted]
            values.append({
                'label': tf_formatted,
                'values': {
                    'value': value
                }
            })
            date = date + relativedelta(**{time_frame: 1})

        return values

    def get_line(self):
        pk_name = self.Model._meta.pk.name
        format, time_frame = get_format_time_frame(self.body)

        group_by_date_field = self.body['group_by_date_field']
        queryset = self.queryset.order_by(group_by_date_field).values(group_by_date_field)
        aggregate = self.body['aggregate'].lower()
        queryset, name = get_annotated_queryset(self.body, queryset, pk_name)

        try:
            earliest = queryset.first().get(group_by_date_field, None)
            latest = queryset.last().get(group_by_date_field, None)
        except Exception:
            values = []
        else:
            periods = self.get_periods(queryset, f'{name}__{aggregate}', group_by_date_field, format)
            values = self.compute_line_values(earliest, latest, periods, time_frame)
        return values

    def post(self, request, *args, **kwargs):
        return self.chart()
