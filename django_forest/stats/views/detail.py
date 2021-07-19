import uuid
from datetime import timedelta, datetime

from dateutil.relativedelta import relativedelta
from django.db.models import Sum
from django.http import JsonResponse

from django_forest.stats.utils import get_annotated_queryset, get_format_time_frame
from django_forest.stats.utils.stats import StatsView


class DetailView(StatsView):
    def serialize(self, value):
        if isinstance(value, datetime):
            return value.strftime('%d/%m/%Y')
        return value

    def get_value(self):
        # TODO handle countPrevious for some date operator
        # sum
        if self.body['aggregate'] == 'Sum':
            q = self.queryset.aggregate(sum=Sum(self.body['aggregate_field']))
            value = q['sum']
        # count
        else:
            value = self.queryset.count()

        key = 'countCurrent'
        if self.body['type'] == 'Objective':
            key = 'value'

        return {
            key: value
        }

    def get_pie(self):
        pk_name = self.Model._meta.pk.name
        group_by_field = self.body['group_by_field']

        queryset = self.queryset.order_by(group_by_field).values(group_by_field)

        aggregate = self.body['aggregate'].lower()
        queryset, value = get_annotated_queryset(self.body, queryset, pk_name)

        return [{
            'key': self.serialize(x[self.body['group_by_field']]),
            'value': x[f'{value}__{aggregate}']
        } for x in queryset]

    def get_leaderboard(self):
        label_field = self.body['label_field']
        relationship_field = self.body['relationship_field']

        queryset = self.queryset.values(label_field)
        association_field = self.get_association_field(self.Model, relationship_field)
        pk_name = association_field.related_model._meta.pk.name

        aggregate = self.body['aggregate'].lower()
        association_field_name = association_field.name

        queryset, value = get_annotated_queryset(self.body, queryset, pk_name, association_field_name)
        queryset = queryset.order_by(f'-{value}__{aggregate}')
        queryset = queryset[:self.body['limit']]

        return [{
            'key': self.serialize(x[label_field]),
            'value': x[f'{value}__{aggregate}']
        } for x in queryset if x[f'{value}__{aggregate}'] is not None]

    def get_time_frames(self, queryset, value, group_by_date_field, format):
        time_frames = {}
        for x in queryset:
            tf_formatted = x.get(group_by_date_field).strftime(format)
            if tf_formatted in time_frames:
                time_frames[tf_formatted] += x[value]
            else:
                time_frames[tf_formatted] = x[value]
        return time_frames

    def get_line(self):
        pk_name = self.Model._meta.pk.name
        format, time_frame = get_format_time_frame(self.body)

        group_by_date_field = self.body['group_by_date_field']
        earliest = getattr(self.queryset.earliest(group_by_date_field), group_by_date_field)
        latest = getattr(self.queryset.latest(group_by_date_field), group_by_date_field)

        queryset = self.queryset.order_by(group_by_date_field).values(group_by_date_field)
        aggregate = self.body['aggregate'].lower()
        queryset, value = get_annotated_queryset(self.body, queryset, pk_name)
        time_frames = self.get_time_frames(queryset, f'{value}__{aggregate}', group_by_date_field, format)

        keys = time_frames.keys()
        values = []
        date = earliest
        while date < latest + timedelta(days=1):
            value = 0
            tf_formatted = date.strftime(format)
            if tf_formatted in keys:
                value = time_frames[tf_formatted]
            values.append({
                'label': tf_formatted,
                'values': {
                    'value': value
                }
            })
            date = date + relativedelta(**{time_frame: 1})
        return values

    def check_aggregate(self):
        if 'aggregate' not in self.body:
            raise Exception('aggregate is missing')

    def handle_values(self, _type):
        values = None
        if _type in ('Value', 'Objective'):
            values = self.get_value()
        elif _type == 'Pie':
            values = self.get_pie()
        elif _type == 'Line':
            values = self.get_line()
        elif _type == 'Leaderboard':
            values = self.get_leaderboard()

        return values

    def handle_chart(self):
        res = {
            'data': {
                'attributes': {},
                'type': 'stats',
                'id': uuid.uuid4()
            }}

        if 'type' in self.body:
            self.check_aggregate()

            res['data']['attributes'] = {
                'value': self.handle_values(self.body['type'])
            }
        return res

    def post(self, request, *args, **kwargs):
        try:
            res = self.handle_chart()
        except Exception as e:
            return self.error_response(e)
        else:
            return JsonResponse(res, safe=False)
