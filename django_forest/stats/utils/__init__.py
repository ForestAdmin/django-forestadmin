from django.db.models import Sum, Count


def get_queryset_aggregate(body, queryset, pk_name):
    aggregate = body['aggregate']
    # sum
    if aggregate == 'Sum':
        queryset = queryset.annotate(Sum(body['aggregate_field']))
    # count
    else:
        queryset = queryset.annotate(Count(pk_name))

    return queryset, aggregate.lower()


def get_format_time_frame(body):
    format = ''
    time_frame = ''
    if body['time_range'] == 'Day':
        format = '%d/%m/%Y'
        time_frame = 'days'
    elif body['time_range'] == 'Week':
        format = 'W%V-%Y'  # TODO review format, different from node (week + 1)...
        time_frame = 'weeks'
    elif body['time_range'] == 'Month':
        format = '%b %y'
        time_frame = 'months'
    elif body['time_range'] == 'Year':
        format = '%Y'
        time_frame = 'years'

    return format, time_frame
