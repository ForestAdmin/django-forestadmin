from datetime import timedelta
import math


def handle_previous_quarter_utils(x):
    current_quarter = math.ceil(x.month / 3)
    last_quarter = 4 if current_quarter == 1 else current_quarter - 1
    previous_last_quarter = 4 if last_quarter == 1 else last_quarter - 1
    year = x.year - 1 if current_quarter == 1 else x.year

    return current_quarter, last_quarter, previous_last_quarter, year


def get_current_month(current_quarter, last_quarter, previous):
    month = current_quarter
    if previous:
        month = last_quarter
    return month


def get_last_quarter_month(last_quarter, previous_last_quarter, previous):
    month = last_quarter
    if previous:
        month = previous_last_quarter
    return month


def handle_previous_quarter_from(x, current=False, previous=False):
    current_quarter, last_quarter, previous_last_quarter, year = handle_previous_quarter_utils(x)
    if current:
        month = get_current_month(current_quarter, last_quarter, previous)
    else:
        month = get_last_quarter_month(last_quarter, previous_last_quarter, previous)
    return x.replace(day=1, month=(month * 3) - 2, year=year)


def handle_previous_quarter_to(x, previous=False):
    _, last_quarter, previous_last_quarter, year = handle_previous_quarter_utils(x)
    month = last_quarter
    if previous:
        month = previous_last_quarter
    return x.replace(day=1, month=(month * 3) + 1, year=year) + timedelta(days=-1)


def get_yesterday(time_frame):
    return {
        'from': lambda x, y: x + timedelta(days=-(time_frame)),
        'to': lambda x, y: x + timedelta(days=-(time_frame))
    }


def get_previous_week(time_frame):
    return {
        'from': lambda x, y: x + timedelta(weeks=-(time_frame)) + timedelta(days=-x.weekday()),
        'to': lambda x, y: x + timedelta(weeks=-(time_frame)) + timedelta(days=6 - x.weekday())
    }


def get_previous_month(x):
    return (x.replace(day=1) + timedelta(days=-1)).replace(day=1)


def get_previous_year(x):
    return (x.replace(day=1, month=1) + timedelta(days=-1)).replace(day=1, month=1)


RANGE_DATE_OPERATORS = {
    'today': {
        'to': lambda x, y: x
    },
    'yesterday': get_yesterday(1),
    'previous_x_days': {
        'from': lambda x, y: x + timedelta(days=-int(y)),
        'to': lambda x: x + timedelta(days=-1)
    },
    'previous_x_days_to_date': {
        'from': lambda x, y: x + timedelta(days=-(int(y) - 1)),
    },
    'previous_week': get_previous_week(1),
    'previous_week_to_date': {
        'from': lambda x, y: x + timedelta(days=-x.weekday()),
    },
    'previous_month': {
        'from': lambda x, y: get_previous_month(x),
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
        'from': lambda x, y: get_previous_year(x),
        'to': lambda x, y: x.replace(day=1, month=1) + timedelta(days=-1)
    },
    'previous_year_to_date': {
        'from': lambda x, y: x.replace(day=1, month=1)
    },
}

PREVIOUS_RANGE_DATE_OPERATORS = {
    'today': get_yesterday(1),
    'yesterday': get_yesterday(2),
    'previous_x_days': {
        'from': lambda x, y: x + timedelta(days=-int(y * 2)),
        'to': lambda x: x + timedelta(days=-1)
    },
    'previous_x_days_to_date': {
        'from': lambda x, y: x + timedelta(days=-((int(y) - 1) * 2)),
    },
    'previous_week': get_previous_week(2),
    'previous_week_to_date': {
        'from': lambda x, y: x + timedelta(weeks=-1) + timedelta(days=-x.weekday()),
    },
    'previous_month': {
        'from': lambda x, y: (get_previous_month(x) + timedelta(days=-1)).replace(day=1),
        'to': lambda x, y: get_previous_month(x) + timedelta(days=-1)
    },
    'previous_month_to_date': {
        'from': lambda x, y: get_previous_month(x),
    },
    'previous_quarter': {
        'from': lambda x, y: handle_previous_quarter_from(x, previous=True),
        'to': lambda x, y: handle_previous_quarter_to(x, previous=True)
    },
    'previous_quarter_to_date': {
        'from': lambda x, y: handle_previous_quarter_from(x, current=True, previous=True),
    },
    'previous_year': {
        'from': lambda x, y: get_previous_year(get_previous_year(x)),
        'to': lambda x, y: get_previous_year(x) + timedelta(days=-1)
    },
    'previous_year_to_date': {
        'from': lambda x, y: get_previous_year(x)
    },
}

DATE_OPERATORS = ['past', 'future', 'today', 'before_x_hours_ago', 'after_x_hours_ago'] \
    + list(RANGE_DATE_OPERATORS.keys())

PREVIOUS_DATE_OPERATOR = ['today', 'yesterday',
                          'previous_week', 'previous_month', 'previous_quarter', 'previous_year',
                          'previous_week_to_date', 'previous_month_to_date', 'previous_quarter_to_date',
                          'previous_year_to_date',
                          'previous_x_days', 'previous_x_days_to_date']
