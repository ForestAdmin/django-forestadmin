from datetime import timedelta

from dateutil.relativedelta import relativedelta
from django.db import connection
from django.db.models import Sum, Count


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
        format = 'W%V-%Y'  # TODO review format, different from node (week + 1)...
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


def get_row(query):
    with connection.cursor() as cursor:
        cursor.execute(query)
        if not len(cursor.description) == 1:
            raise Exception("The result column must be named 'value'")
        value = cursor.description[0].name
        if value != 'value':
            raise Exception(f"The result column must be named 'value' instead of '{value}'.")
        row = cursor.fetchone()

    return row[0]


def check_query(description, column_1, column_2):
    if not len(description) == 2:
        raise Exception(f"The result columns must be named '{column_1}' and '{column_2}'.")
    first = description[0].name
    second = description[1].name
    if first != column_1 or second != column_2:
        err_msg = f"The result columns must be named '{column_1}', '{column_2}' instead of '{first}', '{second}'."
        raise Exception(err_msg)


def execute_query(query, column_1, column_2, one=False):
    with connection.cursor() as cursor:
        cursor.execute(query)
        check_query(cursor.description, column_1, column_2)
        if one:
            res = cursor.fetchone()
        else:
            res = cursor.fetchall()

    return res
