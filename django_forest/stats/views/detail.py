import uuid
from datetime import timedelta

from dateutil.relativedelta import relativedelta
from django.db.models import Sum
from django.http import JsonResponse, HttpResponse

from django_forest.stats.utils import get_queryset_aggregate, get_format_time_frame
from django_forest.stats.utils.stats import StatsView


class DetailView(StatsView):
    def get_value(self):
        # TODO handle countPrevious for some date operator
        if 'aggregate' not in self.body:
            return HttpResponse({}, status=400)

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
        # TODO handle time_range
        if 'aggregate' not in self.body:
            return HttpResponse({}, status=400)
        pk_name = self.Model._meta.pk.name
        group_by_field = self.body['group_by_field']

        queryset = self.queryset.order_by(group_by_field).values(group_by_field)
        queryset, aggregate = get_queryset_aggregate(self.body, queryset, pk_name)

        return [{
            'key': x[self.body['group_by_field']].strftime('%d/%m/%Y'),
            'value': x[f'{pk_name}__{aggregate}']
        } for x in queryset]

    def get_time_frames(self, queryset, group_by_date_field, aggregate, format):
        pk_name = self.Model._meta.pk.name
        time_frames = {}
        for x in queryset:
            tf_formatted = x.get(group_by_date_field).strftime(format)
            if tf_formatted in time_frames:
                time_frames[tf_formatted] += x[f'{pk_name}__{aggregate}']
            else:
                time_frames[tf_formatted] = x[f'{pk_name}__{aggregate}']
        return time_frames

    def get_line(self):
        if 'aggregate' not in self.body:
            return HttpResponse({}, status=400)
        pk_name = self.Model._meta.pk.name
        format, time_frame = get_format_time_frame(self.body)

        group_by_date_field = self.body['group_by_date_field']
        earliest = getattr(self.queryset.earliest(group_by_date_field), group_by_date_field)
        latest = getattr(self.queryset.latest(group_by_date_field), group_by_date_field)

        queryset = self.queryset.order_by(group_by_date_field).values(group_by_date_field)
        queryset, aggregate = get_queryset_aggregate(self.body, queryset, pk_name)
        time_frames = self.get_time_frames(queryset, group_by_date_field, aggregate, format)

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

    def handle_chart(self):
        res = {
            'data': {
                'attributes': {},
                'type': 'stats',
                'id': uuid.uuid4()
            }}

        if 'type' in self.body:
            _type = self.body['type']
            self.check_aggregate()
            values = None
            if _type in ('Value', 'Objective'):
                values = self.get_value()
            elif _type == 'Pie':
                values = self.get_pie()
            elif _type == 'Line':
                values = self.get_line()
            # TODO handle leaderboard

            res['data']['attributes'] = {
                'value': values
            }
        return res

    def post(self, request, *args, **kwargs):
        try:
            res = self.handle_chart()
        except Exception as e:
            return self.error_response(e)
        else:
            return JsonResponse(res, safe=False)
