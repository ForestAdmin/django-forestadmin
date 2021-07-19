from django.db.models import Sum, Count


def get_annotated_queryset(body, queryset, pk_name, association_field_name=None):
    aggregate = body['aggregate']

    # determine value
    value = pk_name  # count by default
    if aggregate == 'sum':  # sum
        value = body['aggregate_field']

    # do we have an association field?
    if association_field_name is not None:
        value = f'{association_field_name}__{value}'

    # select annotation
    annotation = Count(value)  # count
    if aggregate == 'Sum':
        annotation = Sum(value)  # sum

    return queryset.annotate(annotation), value


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
