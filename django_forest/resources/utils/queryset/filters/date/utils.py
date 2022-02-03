import pandas as pd
from datetime import datetime
try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo


def get_date_range(
    current_datetime: datetime,
    frequency: str,
    periods: int,
    previous: bool = True,
    offset: int = 0,
) -> tuple:
    tzinfo = current_datetime.tzinfo
    current_datetime = current_datetime.replace(tzinfo=zoneinfo.ZoneInfo('UTC'))
    current_dt = pd.to_datetime(current_datetime)
    kwargs = {
        'freq': frequency,
        'periods': offset + 2,
    }
    if periods:
        kwargs['freq'] = f"{periods}{frequency}"

    if previous:
        kwargs['end'] = current_dt
        last_idx = 1
        start_idx = 0
    else:
        kwargs['start'] = current_dt
        last_idx = -1
        start_idx = -2
    date_range = pd.date_range(**kwargs)

    replace_kwargs = {
        'tzinfo': tzinfo,
    }
    if frequency != 'H':
        replace_kwargs = {
            **replace_kwargs,
            'hour': 0,
            'minute': 0,
            'second': 0,
            'microsecond': 0,
        }
    return (
        date_range[start_idx].to_pydatetime().replace(**replace_kwargs),
        date_range[last_idx].to_pydatetime().replace(**replace_kwargs),
    )

def get_previous_x_days(current_datetime: datetime, period: int = 0, offset: int = 0) -> tuple:
    return get_date_range(current_datetime, 'd', period, offset=offset)

def get_next_x_days(current_datetime: datetime, period: int = 0, offset: int = 0) -> tuple:
    return get_date_range(current_datetime, 'd', period, False, offset=offset)

def get_previous_x_weeks(current_datetime: datetime, period: int = 0, offset: int = 0) -> tuple:
    return get_date_range(current_datetime, 'W-MON', period, offset=offset)

def get_previous_x_months(current_datetime: datetime, period: int = 0, offset: int = 0) -> tuple:
    return get_date_range(current_datetime, 'MS', period, offset=offset)

def get_previous_x_years(current_datetime: datetime, period: int = 0, offset: int = 0) -> tuple:
    return get_date_range(current_datetime, 'YS', period, offset=offset)

def get_previous_x_quarters(current_datetime: datetime, period: int = 0, offset: int = 0) -> tuple:
    return get_date_range(current_datetime, 'QS', period, offset=offset)

def get_range_x_hours(current_datetime: datetime, period: int = 0, previous: bool = True, offset: int = 0) -> tuple:
    return get_date_range(current_datetime, 'H', period, previous=previous, offset=offset)

def get_previous_x_hours(current_datetime: datetime, period: int = 0, offset: int = 0) -> tuple:
    return get_range_x_hours(current_datetime, period, offset=offset)

def get_next_x_hours(current_datetime: datetime, period: int = 0, offset: int = 0) -> tuple:
    return get_range_x_hours(current_datetime, period, previous=False, offset=offset)
