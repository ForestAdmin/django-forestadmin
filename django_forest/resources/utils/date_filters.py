from datetime import timedelta, datetime
import math

from django.db.models import Q


def handle_previous_quarter_utils(x):
    current_quarter = math.ceil(x.month / 3)
    last_quarter = 4 if current_quarter == 1 else current_quarter - 1
    year = x.year - 1 if current_quarter == 1 else x.year

    return current_quarter, last_quarter, year


def handle_previous_quarter_from(x, current=False):
    current_quarter, last_quarter, year = handle_previous_quarter_utils(x)
    if current:
        month = current_quarter
    else:
        month = last_quarter
    return x.replace(day=1, month=(month * 3) - 2, year=year)


def handle_previous_quarter_to(x):
    _, last_quarter, year = handle_previous_quarter_utils(x)
    return x.replace(day=1, month=(last_quarter * 3) + 1, year=year) + timedelta(days=-1)


RANGE_DATE_OPERATORS = {
    'today': {
        'to': lambda x, y: x
    },
    'yesterday': {
        'from': lambda x, y: x + timedelta(days=-1),
        'to': lambda x, y: x + timedelta(days=-1)
    },
    'previous_x_days': {
        'from': lambda x, y: x + timedelta(days=-int(y)),
        'to': lambda x: x + timedelta(days=-1)
    },
    'previous_x_days_to_date': {
        'from': lambda x, y: x + timedelta(days=-(int(y) - 1)),
    },
    'previous_week': {
        'from': lambda x, y: x + timedelta(weeks=-1) + timedelta(days=-x.weekday()),
        'to': lambda x, y: x + timedelta(weeks=-1) + timedelta(days=6-x.weekday())
    },
    'previous_week_to_date': {
        'from': lambda x, y: x + timedelta(days=-x.weekday()),
    },
    'previous_month': {
        'from': lambda x, y: (x.replace(day=1) + timedelta(days=-1)).replace(day=1),
        'to': lambda x, y: x.replace(day=1) + timedelta(days=-1)
    },
    'previous_month_to_date': {
        'from': lambda x, y: x.replace(day=1),
    },
    'previous_quarter': {
        'from': lambda x, y: handle_previous_quarter_from(x),
        'to': lambda x, y: handle_previous_quarter_to(x)
    },
    'previous_quarter_to_date': {
        'from': lambda x, y: handle_previous_quarter_from(x, current=True),
    },
    'previous_year': {
        'from': lambda x, y: (x.replace(day=1, month=1) + timedelta(days=-1)).replace(day=1, month=1),
        'to': lambda x, y: x.replace(day=1, month=1) + timedelta(days=-1)
    },
    'previous_year_to_date': {
        'from': lambda x, y: x.replace(day=1, month=1)
    },
}

DATE_OPERATORS = [
    'past',
    'future',
    'today',
    'before_x_hours_ago',
    'after_x_hours_ago'
] + list(RANGE_DATE_OPERATORS.keys())


def handle_range_date_operator(operator, field, value, now):
    start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_today = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    _from = start_of_today
    _to = now

    if 'from' in RANGE_DATE_OPERATORS[operator]:
        _from = RANGE_DATE_OPERATORS[operator]['from'](start_of_today, value)
    if 'to' in RANGE_DATE_OPERATORS[operator]:
        _to = RANGE_DATE_OPERATORS[operator]['to'](end_of_today, value)

    return Q(**{f'{field}__range': [_from, _to]})


def handle_hours_ago(value, field, operator, now):
    value = now + timedelta(hours=-int(value))
    if operator.startswith('before'):
        lookup_field = f'{field}__lt'
    else:
        lookup_field = f'{field}__gt'

    return Q(**{lookup_field: value})


def handle_past_future(field, operator, now):
    if operator == 'past':
        lookup_field = f'{field}__lte'
    else:
        lookup_field = f'{field}__gte'
    return Q(**{lookup_field: now})


def handle_date_operator(operator, field, value, tz):
    now = datetime.now(tz)
    if operator in ('past', 'future'):
        return handle_past_future(field, operator, now)
    elif operator.endswith('x_hours_ago'):
        return handle_hours_ago(value, field, operator, now)
    else:
        return handle_range_date_operator(operator, field, value, now)
