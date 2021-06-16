from datetime import date, timedelta, datetime

import math

from django.db.models import Q
from django.utils.timezone import now

# TODO handle client timezone
DATE_OPERATORS = [
    'past',
    'future',
    'today',
    'yesterday',
    'previous_week',
    'previous_month',
    'previous_quarter',
    'previous_year',
    'previous_week_to_date',
    'previous_month_to_date',
    'previous_quarter_to_date',
    'previous_year_to_date',
    'previous_x_days',
    'previous_x_days_to_date',
    'before_x_hours_ago',
    'after_x_hours_ago'
]


def end_of_day(dt):
    return datetime.combine(dt, datetime.max.time())


def handle_previous_week_from(x):
    return x + timedelta(weeks=-1) + timedelta(days=-x.isoweekday())


def handle_previous_week_to(x):
    last_week = handle_previous_week_from(x)
    end_of_day(last_week + timedelta(days=6))


def handle_previous_quarter_utils(today):
    current_quarter = math.ceil(today.month / 3)
    last_quarter = 4 if current_quarter == 1 else current_quarter - 1
    year = today.year - 1 if current_quarter == 1 else today.year

    return current_quarter, last_quarter, year


def handle_previous_quarter_from(today):
    current_quarter, last_quarter, year = handle_previous_quarter_utils(today)
    return today.replace(day=1, month=(last_quarter * 3) - 2, year=year)


def handle_previous_quarter_to(today):
    current_quarter, last_quarter, year = handle_previous_quarter_utils(today)
    return end_of_day(today.replace(day=1, month=(last_quarter * 3) + 1, year=year) + timedelta(days=-1))


RANGE_DATE_OPERATORS = {
    'today': {
        'to': lambda x, y: end_of_day(x)
    },
    'previous_x_days': {
        'from': lambda x, y: x + timedelta(days=-int(y)),
        'to': lambda x: end_of_day(x + timedelta(days=-1))
    },
    'previous_x_days_to_date': {
        'from': lambda x, y: x + timedelta(days=-(int(y) - 1)),
    },
    'yesterday': {
        'from': lambda x, y: x + timedelta(days=-1),
        'to': lambda x, y: end_of_day(x + timedelta(days=-1))
    },
    'previous_week': {
        'from': lambda x, y: handle_previous_week_from(x),
        'to': lambda x, y: handle_previous_week_to(x)
    },
    'previous_month': {
        'from': lambda x, y: (x.replace(day=1) + timedelta(days=-1)).replace(day=1),
        'to': lambda x, y: end_of_day(x.replace(day=1) + timedelta(days=-1))
    },
    'previous_quarter': {
        'from': lambda x, y: handle_previous_quarter_from(x),
        'to': lambda x, y: handle_previous_quarter_to(x)
    },
    'previous_year': {
        'from': lambda x, y: (x.replace(day=1, month=1) + timedelta(days=-1)).replace(day=1, month=1),
        'to': lambda x, y: end_of_day(x.replace(day=1, month=1) + timedelta(days=-1))
    },
}


def handle_range_date_operator(operator, field, value):
    today = datetime.combine(date.today(), datetime.min.time())
    _from = today
    _to = now()

    if 'from' in RANGE_DATE_OPERATORS[operator]:
        _from = RANGE_DATE_OPERATORS[operator]['from'](today, value)
    if 'to' in RANGE_DATE_OPERATORS[operator] and not operator.endswith('to_date'):
        _to = RANGE_DATE_OPERATORS[operator]['to'](today, value)

    return Q(**{f'{field}__range': [_from, _to]})


def handle_hours_ago(value, field, operator):
    value = now() + timedelta(hours=-int(value))
    if operator.startswith('before'):
        lookup_field = f'{field}__lt'
    else:
        lookup_field = f'{field}__gt'

    return Q(**{lookup_field: value})


def handle_past_future(field, operator):
    if operator == 'past':
        lookup_field = f'{field}__lte'
    else:
        lookup_field = f'{field}__gte'
    return Q(**{lookup_field: now()})


def handle_date_operator(operator, field, value):
    if operator in ('past', 'future'):
        return handle_past_future(field, operator)
    elif operator.endswith('x_hours_ago'):
        return handle_hours_ago(value, field, operator)
    else:
        return handle_range_date_operator(operator, field, value)
