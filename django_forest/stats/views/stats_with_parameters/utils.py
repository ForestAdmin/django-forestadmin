from datetime import timedelta

from dateutil.relativedelta import relativedelta
from django.db.models import Sum, Count

from django_forest.resources.utils.queryset.filters.date.factory import ConditionFactory as DateConditionFactory


def compute_value(params, queryset):
    # sum
    if params['aggregate'] == 'Sum':
        q = queryset.aggregate(sum=Sum(params['aggregate_field']))
        value = q['sum']
        if value is None:
            value = 0
    # count
    else:
        value = queryset.count()

    return int(value)


def get_annotated_queryset(body, queryset, pk_name, association_field_name=None):
    aggregate = body['aggregate']

    # determine name
    name = pk_name  # count by default
    if aggregate == 'Sum':  # sum
        name = body['aggregate_field']

    # do we have an association field?
    if association_field_name is not None:
        name = f'{association_field_name}__{name}'

    # select annotation
    annotation = Count(name)  # count
    if aggregate == 'Sum':
        annotation = Sum(name)  # sum

    return queryset.annotate(annotation), name


def get_format_time_frame(params):
    format = ''
    time_frame = ''
    time_range = params['time_range']
    if time_range == 'Day':
        format = '%d/%m/%Y'
        time_frame = 'days'
    elif time_range == 'Week':
        format = 'W%V-%Y'
        time_frame = 'weeks'
    elif time_range == 'Month':
        format = '%b %y'
        time_frame = 'months'
    elif time_range == 'Year':
        format = '%Y'
        time_frame = 'years'

    return format, time_frame


def get_periods(queryset, key, group_by_date_field, format):
    periods = {}
    for x in queryset:
        tf_formatted = x.get(group_by_date_field).strftime(format)
        if tf_formatted in periods:
            periods[tf_formatted] += x[key]
        else:
            periods[tf_formatted] = x[key]
    return periods


def compute_line_values(bounds, periods, time_frame, format):
    keys = periods.keys()
    values = []
    date = bounds['earliest']
    while date < bounds['latest'] + timedelta(days=1):
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


def contains_previous_date_operator(filters):
    if 'aggregator' in filters:
        previous_date_operator = next(
            (x for x in filters['conditions'] if x['operator'] in DateConditionFactory.OFFSET_OPERATORS), None)
        return previous_date_operator is not None
    else:
        return filters['operator'] in DateConditionFactory.OFFSET_OPERATORS
