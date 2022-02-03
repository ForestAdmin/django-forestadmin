import pytest
from unittest import mock
from datetime import datetime
try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo

from django_forest.resources.utils.queryset.filters.date.conditions import (
    RangeCondition,
    LowerThanCondition,
    LowerThanOrEqualCondition,
    GreaterThanCondition,
    GreaterThanOrEqualCondition,
)
from django_forest.resources.utils.queryset.filters.date.factory import ConditionFactory


def _init_factory(dt: datetime):
    return ConditionFactory(dt)

def test_date_condition_builders():
    assert ConditionFactory.DATE_CONDITION_BUILDERS == {
        'today': 'build_today_condition',
        'yesterday': 'build_yesterday_condition',
        'previous_x_days': 'build_previous_x_days_condition',
        'previous_x_days_to_date': 'build_previous_x_days_to_date_condition',
        'previous_week': 'build_previous_week_condition',
        'previous_week_to_date': 'build_previous_week_to_date_condition',
        'previous_month': 'build_previous_month_condition',
        'previous_month_to_date': 'build_previous_month_to_date_condition',
        'previous_quarter': 'build_previous_quarter_condition',
        'previous_quarter_to_date': 'build_previous_quarter_to_date_condition',
        'previous_year': 'build_previous_year_condition',
        'previous_year_to_date': 'build_previous_year_to_date_condition',
        'before_x_hours_ago': 'build_before_x_hours_ago_condition',
        'after_x_hours_ago': 'build_after_x_hours_ago_condition',
        'past': 'build_past_condition',
        'future': 'build_future_condition',
    }

def test_operators():
    assert ConditionFactory.OPERATORS == [
        'today',
        'yesterday',
        'previous_x_days',
        'previous_x_days_to_date',
        'previous_week',
        'previous_week_to_date',
        'previous_month',
        'previous_month_to_date',
        'previous_quarter',
        'previous_quarter_to_date',
        'previous_year',
        'previous_year_to_date',
        'before_x_hours_ago',
        'after_x_hours_ago',
        'past',
        'future',
    ]

def test_offset_operators():
    assert ConditionFactory.OFFSET_OPERATORS == [
        'today',
        'yesterday',
        'previous_x_days',
        'previous_x_days_to_date',
        'previous_week',
        'previous_week_to_date',
        'previous_month',
        'previous_month_to_date',
        'previous_quarter',
        'previous_quarter_to_date',
        'previous_year',
        'previous_year_to_date',
    ]

@pytest.mark.parametrize(
    "current,expected,offset",
    (   
        (
            datetime(2022, 1, 1), 
            RangeCondition(
                datetime(2022, 1, 1),
                datetime(2022, 1, 2)
            ),
            0
        ),
        (
            datetime(2022, 1, 1), 
            RangeCondition(
                datetime(2021, 12, 31),
                datetime(2022, 1, 1)
            ),
            1
        ),
        (
            datetime(2022, 1, 1), 
            RangeCondition(
                datetime(2021, 12, 30),
                datetime(2021, 12, 31)
            ),
            2
        ),
        (
            datetime(2022, 12, 31, tzinfo=zoneinfo.ZoneInfo("UTC")), 
            RangeCondition(
                datetime(2022, 12, 31, tzinfo=zoneinfo.ZoneInfo("UTC")),
                datetime(2023, 1, 1, tzinfo=zoneinfo.ZoneInfo("UTC"))
            ),
            0
        ),
        (
            datetime(2020, 2, 29, tzinfo=zoneinfo.ZoneInfo("America/Araguaina")), 
            RangeCondition(
                datetime(2020, 2, 29, tzinfo=zoneinfo.ZoneInfo("America/Araguaina")),
                datetime(2020, 3, 1, tzinfo=zoneinfo.ZoneInfo("America/Araguaina"))
            ),
            0
        ),
        (
            datetime(2025, 8, 10, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")), 
            RangeCondition(
                datetime(2025, 8, 10, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")),
                datetime(2025, 8, 11, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo"))
            ),
            0
        ),
    )
)
def test_build_today_condition(current: datetime, expected: RangeCondition, offset: int) -> None:
    factory = _init_factory(current)
    assert factory.build_today_condition(current, offset) == expected

@pytest.mark.parametrize(
    "current,expected,offset",
    (   
        (
            datetime(2022, 1, 1), 
            RangeCondition(
                start=datetime(2021, 12, 31),
                end=datetime(2022, 1, 1)
            ),
            0
        ),
        (
            datetime(2022, 1, 1), 
            RangeCondition(
                start=datetime(2021, 12, 30),
                end=datetime(2021, 12, 31)
            ),
            1
        ),
        (
            datetime(2022, 12, 31, tzinfo=zoneinfo.ZoneInfo("UTC")), 
            RangeCondition(
                start=datetime(2022, 12, 30, tzinfo=zoneinfo.ZoneInfo("UTC")),
                end=datetime(2022, 12, 31, tzinfo=zoneinfo.ZoneInfo("UTC"))
            ),
            0
        ),
        (
            datetime(2020, 2, 1, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")), 
            RangeCondition(
                start=datetime(2020, 1, 31, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")),
                end=datetime(2020, 2, 1, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo"))
            ),
            0
        ),
        (
            datetime(2020, 2, 1, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")), 
            RangeCondition(
                start=datetime(2020, 1, 30, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")),
                end=datetime(2020, 1, 31, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo"))
            ),
            1
        ),
        (
            datetime(2025, 8, 10, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")), 
            RangeCondition(
                start=datetime(2025, 8, 9, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")),
                end=datetime(2025, 8, 10, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo"))
            ),
            0
        ),
    )
)
def test_build_yesterday_condition(current, expected, offset):
    factory = _init_factory(current)
    assert factory.build_yesterday_condition(current, offset) == expected


@pytest.mark.parametrize(
    "current,days,expected,offset",
    (   
        (
            datetime(2022, 1, 1, 23, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")), 
            1,
            RangeCondition(
                datetime(2021, 12, 31, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")),
                datetime(2022, 1, 1, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe"))
            ),
            0
        ),
        (
            datetime(2022, 1, 1, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")), 
            1,
            RangeCondition(
                datetime(2021, 12, 30, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")),
                datetime(2021, 12, 31, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe"))
            ),
            1
        ),
        (
            datetime(2022, 12, 31, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")), 
            2,
            RangeCondition(
                datetime(2022, 12, 29, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")),
                datetime(2022, 12, 31, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo"))
            ),
            0
        ),
        (
            datetime(2022, 12, 31, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")), 
            2,
            RangeCondition(
                datetime(2022, 12, 27, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")),
                datetime(2022, 12, 29, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo"))
            ),
            1
        ),
        (
            datetime(2020, 2, 1, tzinfo=zoneinfo.ZoneInfo("UTC")), 
            5,
            RangeCondition(
                datetime(2020, 1, 27, tzinfo=zoneinfo.ZoneInfo("UTC")),
                datetime(2020, 2, 1, tzinfo=zoneinfo.ZoneInfo("UTC"))
            ),
            0
        ),
        (
            datetime(2025, 8, 10), 
            60,
            RangeCondition(
                datetime(2025, 6, 11),
                datetime(2025, 8, 10)
            ),
            0
        ),
    )
)
def test_build_previous_x_days_condition(current, days, expected, offset):
    factory = _init_factory(current)
    assert factory.build_previous_x_days_condition(current, offset, days) == expected

@pytest.mark.parametrize(
    "current,days,expected,offset",
    (   
        (
            datetime(2022, 1, 1), 
            1,
            RangeCondition(
                datetime(2022, 1, 1),
                datetime(2022, 1, 2)
            ),
            0
        ),
        (
            datetime(2022, 1, 1), 
            1,
            RangeCondition(
                datetime(2021, 12, 31),
                datetime(2022, 1, 1)
            ),
            1
        ),
        (
            datetime(2022, 1, 1), 
            1,
            RangeCondition(
                datetime(2021, 12, 30),
                datetime(2021, 12, 31)
            ),
            2
        ),
        (
            datetime(2022, 12, 31), 
            2,
            RangeCondition(
                datetime(2022, 12, 30),
                datetime(2023, 1, 1)
            ),
            0
        ),
        (
            datetime(2020, 2, 1), 
            5,
            RangeCondition(
                datetime(2020, 1, 28),
                datetime(2020, 2, 2)
            ),
            0
        ),
        (
            datetime(2020, 2, 1), 
            5,
            RangeCondition(
                datetime(2020, 1, 23),
                datetime(2020, 1, 28)
            ),
            1
        ),
        (
            datetime(2020, 2, 1), 
            5,
            RangeCondition(
                datetime(2020, 1, 23),
                datetime(2020, 1, 28)
            ),
            1
        ),
        (
            datetime(2025, 8, 10), 
            60,
            RangeCondition(
                datetime(2025, 6, 12),
                datetime(2025, 8, 11)
            ),
            0
        ),
    )
)
def test_build_previous_x_days_to_date_condition(current, days, expected, offset):
    factory = _init_factory(current)
    assert factory.build_previous_x_days_to_date_condition(current, offset, days) == expected

@pytest.mark.parametrize(
    "current,expected,offset",
    (
        (
            datetime(2022, 1, 5), 
            RangeCondition(
                datetime(2021, 12, 27),
                datetime(2022, 1, 3)
            ),
            0
        ),
        (
            datetime(2022, 1, 5), 
            RangeCondition(
                datetime(2021, 12, 20),
                datetime(2021, 12, 27)
            ),
            1
        ),
        (
            datetime(2022, 2, 14, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")), 
            RangeCondition(
                datetime(2022, 2, 7, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")),
                datetime(2022, 2, 14, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe"))
            ),
            0
        ),
        (
            datetime(2022, 4, 14, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")), 
            RangeCondition(
                datetime(2022, 4, 4, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")),
                datetime(2022, 4, 11, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")),
            ),
            0
        ),
        (
            datetime(2017, 11, 6, tzinfo=zoneinfo.ZoneInfo("UTC")), 
            RangeCondition(
                datetime(2017, 10, 30, tzinfo=zoneinfo.ZoneInfo("UTC")),
                datetime(2017, 11, 6, tzinfo=zoneinfo.ZoneInfo("UTC"))
            ),
            0
        ),
        (
            datetime(2017, 11, 6, tzinfo=zoneinfo.ZoneInfo("UTC")), 
            RangeCondition(
                datetime(2017, 10, 16, tzinfo=zoneinfo.ZoneInfo("UTC")),
                datetime(2017, 10, 23, tzinfo=zoneinfo.ZoneInfo("UTC"))
            ),
            2
        ),
    )
)
def test_build_previous_week_condition(current, expected, offset):
    factory = _init_factory(current)
    assert factory.build_previous_week_condition(current, offset) == expected

@pytest.mark.parametrize(
    "current,expected,offset",
    (
        (
            datetime(2022, 1, 5, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")), 
            RangeCondition(
                datetime(2022, 1, 3, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")),
                datetime(2022, 1, 6, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")), 
            ),
            0
        ),
        (
            datetime(2022, 2, 14, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")), 
            RangeCondition(
                datetime(2022, 2, 14, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")),
                datetime(2022, 2, 15, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")),
            ),
            0
        ),
        (
            datetime(2022, 2, 14, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")), 
            RangeCondition(
                datetime(2022, 2, 7, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")),
                datetime(2022, 2, 14, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")),
            ),
            1
        ),
        (
            datetime(2022, 2, 14, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")), 
            RangeCondition(
                datetime(2022, 1, 31, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")),
                datetime(2022, 2, 7, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")),
            ),
            2
        ),
        (
            datetime(2022, 4, 14, tzinfo=zoneinfo.ZoneInfo("UTC")), 
            RangeCondition(
                datetime(2022, 4, 11, tzinfo=zoneinfo.ZoneInfo("UTC")),
                datetime(2022, 4, 15, tzinfo=zoneinfo.ZoneInfo("UTC")),
            ),
            0
        ),
        (
            datetime(2017, 11, 6), 
            RangeCondition(
                datetime(2017, 11, 6),
                datetime(2017, 11, 7),
            ),
            0
        ),
    )
)
def test_previous_week_to_date_condition(current, expected, offset):
    factory = _init_factory(current)
    assert factory.build_previous_week_to_date_condition(current, offset) == expected

@pytest.mark.parametrize(
    "current,expected,offset",
    (
        (
            datetime(2022, 1, 5, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")), 
            RangeCondition(
                datetime(2021, 12, 1, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")),
                datetime(2022, 1, 1, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")), 
            ),
            0
        ),
        (
            datetime(2022, 1, 5, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")), 
            RangeCondition(
                datetime(2021, 11, 1, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")),
                datetime(2021, 12, 1, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")), 
            ),
            1
        ),
        (
            datetime(2022, 2, 14, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")), 
            RangeCondition(
                datetime(2022, 1, 1, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")),
                datetime(2022, 2, 1, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")),
            ),
            0
        ),
        (
            datetime(2022, 4, 14, tzinfo=zoneinfo.ZoneInfo("UTC")), 
            RangeCondition(
                datetime(2022, 3, 1, tzinfo=zoneinfo.ZoneInfo("UTC")),
                datetime(2022, 4, 1, tzinfo=zoneinfo.ZoneInfo("UTC")),
            ),
            0
        ),
        (
            datetime(2022, 4, 14, tzinfo=zoneinfo.ZoneInfo("UTC")), 
            RangeCondition(
                datetime(2022, 1, 1, tzinfo=zoneinfo.ZoneInfo("UTC")),
                datetime(2022, 2, 1, tzinfo=zoneinfo.ZoneInfo("UTC")),
            ),
            2
        ),
        (
            datetime(2017, 11, 6), 
            RangeCondition(
                datetime(2017, 10, 1),
                datetime(2017, 11, 1),
            ),
            0
        ),
    )
)
def test_build_previous_month_condition(current, expected, offset):
    factory = _init_factory(current)
    assert factory.build_previous_month_condition(current, offset) == expected

@pytest.mark.parametrize(
    "current,expected,offset",
    (
        (
            datetime(2022, 1, 5, tzinfo=zoneinfo.ZoneInfo("UTC")), 
            RangeCondition(
                datetime(2022, 1, 1, tzinfo=zoneinfo.ZoneInfo("UTC")),
                datetime(2022, 1, 6, tzinfo=zoneinfo.ZoneInfo("UTC")), 
            ),
            0
        ),
        (
            datetime(2022, 1, 5, tzinfo=zoneinfo.ZoneInfo("UTC")), 
            RangeCondition(
                datetime(2021, 12, 1, tzinfo=zoneinfo.ZoneInfo("UTC")),
                datetime(2022, 1, 1, tzinfo=zoneinfo.ZoneInfo("UTC")), 
            ),
            1
        ),
        (
            datetime(2022, 1, 5, tzinfo=zoneinfo.ZoneInfo("UTC")), 
            RangeCondition(
                datetime(2021, 11, 1, tzinfo=zoneinfo.ZoneInfo("UTC")),
                datetime(2021, 12, 1, tzinfo=zoneinfo.ZoneInfo("UTC")), 
            ),
            2
        ),
        (
            datetime(2022, 2, 14, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")), 
            RangeCondition(
                datetime(2022, 2, 1, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")),
                datetime(2022, 2, 15, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")),
            ),
            0
        ),
        (
            datetime(2022, 4, 14, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")), 
            RangeCondition(
                datetime(2022, 4, 1, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")),
                datetime(2022, 4, 15, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")),
            ),
            0
        ),
        (
            datetime(2017, 11, 1), 
            RangeCondition(
                datetime(2017, 11, 1),
                datetime(2017, 11, 2),
            ),
            0
        ),
    )
)
def test_build_previous_month_to_date_condition(current, expected, offset):
    factory = _init_factory(current)
    assert factory.build_previous_month_to_date_condition(current, offset) == expected

@pytest.mark.parametrize(
    "current,expected,offset",
    (   
        (
            datetime(2022, 1, 1, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")), 
            RangeCondition(
                datetime(2021, 10, 1, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")),
                datetime(2022, 1, 1, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")),
            ),
            0
        ),
        (
            datetime(2022, 2, 12, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")), 
            RangeCondition(
                datetime(2021, 10, 1, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")),
                datetime(2022, 1, 1, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")),
            ),
            0
        ),
        (
            datetime(2022, 3, 31, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")), 
            RangeCondition(
                datetime(2021, 10, 1, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")),
                datetime(2022, 1, 1, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")),
            ),
            0
        ),
        (
            datetime(2022, 4, 1, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")), 
            RangeCondition(
                datetime(2022, 1, 1, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")),
                datetime(2022, 4, 1, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")),
            ),
            0
        ),
        (
            datetime(2022, 5, 12, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")), 
            RangeCondition(
                datetime(2022, 1, 1, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")),
                datetime(2022, 4, 1, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")),
            ),
            0
        ),
        (
            datetime(2022, 6, 30, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")), 
            RangeCondition(
                datetime(2022, 1, 1, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")),
                datetime(2022, 4, 1, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")),
            ),
            0
        ),
        (
            datetime(2022, 7, 1, tzinfo=zoneinfo.ZoneInfo("UTC")), 
            RangeCondition(
                datetime(2022, 4, 1, tzinfo=zoneinfo.ZoneInfo("UTC")),
                datetime(2022, 7, 1, tzinfo=zoneinfo.ZoneInfo("UTC")),
            ),
            0
        ),
        (
            datetime(2022, 8, 12, tzinfo=zoneinfo.ZoneInfo("UTC")), 
            RangeCondition(
                datetime(2022, 4, 1, tzinfo=zoneinfo.ZoneInfo("UTC")),
                datetime(2022, 7, 1, tzinfo=zoneinfo.ZoneInfo("UTC")),
            ),
            0
        ),
        (
            datetime(2022, 9, 30, tzinfo=zoneinfo.ZoneInfo("UTC")), 
            RangeCondition(
                datetime(2022, 4, 1, tzinfo=zoneinfo.ZoneInfo("UTC")),
                datetime(2022, 7, 1, tzinfo=zoneinfo.ZoneInfo("UTC")),
            ),
            0
        ),
        (
            datetime(2022, 9, 30, tzinfo=zoneinfo.ZoneInfo("UTC")), 
            RangeCondition(
                datetime(2022, 1, 1, tzinfo=zoneinfo.ZoneInfo("UTC")),
                datetime(2022, 4, 1, tzinfo=zoneinfo.ZoneInfo("UTC")),
            ),
            1
        ),
        (
            datetime(2022, 10, 1), 
            RangeCondition(
                datetime(2022, 7, 1),
                datetime(2022, 10, 1),
            ),
            0
        ),
        (
            datetime(2022, 11, 12), 
            RangeCondition(
                datetime(2022, 7, 1),
                datetime(2022, 10, 1),
            ),
            0
        ),
        (
            datetime(2022, 12, 31), 
            RangeCondition(
                datetime(2022, 7, 1),
                datetime(2022, 10, 1),
            ),
            0
        ),
        (
            datetime(2022, 12, 31), 
            RangeCondition(
                datetime(2022, 1, 1),
                datetime(2022, 4, 1),
            ),
            2
        ),
    )
)
def test_build_previous_quarter_condition(current, expected, offset):
    factory = _init_factory(current)
    assert factory.build_previous_quarter_condition(current, offset) == expected 

@pytest.mark.parametrize(
    "current,expected,offset",
    (   
        (
            datetime(2022, 1, 1, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")), 
            RangeCondition(
                datetime(2022, 1, 1, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")),
                datetime(2022, 1, 2, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")),
            ),
            0
        ),
        (
            datetime(2022, 2, 12, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")), 
            RangeCondition(
                datetime(2022, 1, 1, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")),
                datetime(2022, 2, 13, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")), 
            ),
            0
        ),
        (
            datetime(2022, 3, 31, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")), 
            RangeCondition(
                datetime(2022, 1, 1, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")),
                datetime(2022, 4, 1, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")),
            ),
            0
        ),
        (
            datetime(2022, 4, 1, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")), 
            RangeCondition(
                datetime(2022, 4, 1, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")),
                datetime(2022, 4, 2, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")),
            ),
            0
        ),
        (
            datetime(2022, 5, 12, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")), 
            RangeCondition(
                datetime(2022, 4, 1, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")),
                datetime(2022, 5, 13, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")),
            ),
            0
        ),
        (
            datetime(2022, 6, 30, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")), 
            RangeCondition(
                datetime(2022, 4, 1, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")),
                datetime(2022, 7, 1, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")),
            ),
            0
        ),
        (
            datetime(2022, 7, 1, tzinfo=zoneinfo.ZoneInfo("UTC")), 
            RangeCondition(
                datetime(2022, 7, 1, tzinfo=zoneinfo.ZoneInfo("UTC")),
                datetime(2022, 7, 2, tzinfo=zoneinfo.ZoneInfo("UTC")),
            ),
            0
        ),
        (
            datetime(2022, 8, 12, tzinfo=zoneinfo.ZoneInfo("UTC")), 
            RangeCondition(
                datetime(2022, 7, 1, tzinfo=zoneinfo.ZoneInfo("UTC")),
                datetime(2022, 8, 13, tzinfo=zoneinfo.ZoneInfo("UTC")),
            ),
            0
        ),
        (
            datetime(2022, 9, 30, tzinfo=zoneinfo.ZoneInfo("UTC")), 
            RangeCondition(
                datetime(2022, 7, 1, tzinfo=zoneinfo.ZoneInfo("UTC")),
                datetime(2022, 10, 1, tzinfo=zoneinfo.ZoneInfo("UTC")),
            ),
            0
        ),
        (
            datetime(2022, 10, 1), 
            RangeCondition(
                datetime(2022, 10, 1),
                datetime(2022, 10, 2),
            ),
            0
        ),
        (
            datetime(2022, 11, 12), 
            RangeCondition(
                datetime(2022, 10, 1),
                datetime(2022, 11, 13),
            ),
            0
        ),
        (
            datetime(2022, 12, 31), 
            RangeCondition(
                datetime(2022, 10, 1),
                datetime(2023, 1, 1),
            ),
            0
        ),
    )
)
def test_build_previous_quarter_to_date_condition(current, expected, offset):
    factory = _init_factory(current)
    assert factory.build_previous_quarter_to_date_condition(current, offset) == expected

@pytest.mark.parametrize(
    "current,expected,offset",
    (   
        (
            datetime(2022, 1, 1), 
            RangeCondition(
                datetime(2021, 1, 1),
                datetime(2022, 1, 1),
            ),
            0
        ),
        (
            datetime(2022, 1, 1), 
            RangeCondition(
                datetime(2020, 1, 1),
                datetime(2021, 1, 1),
            ),
            1
        ),
        (
            datetime(2022, 5, 12, tzinfo=zoneinfo.ZoneInfo("UTC")), 
            RangeCondition(
                datetime(2021, 1, 1, tzinfo=zoneinfo.ZoneInfo("UTC")),
                datetime(2022, 1, 1, tzinfo=zoneinfo.ZoneInfo("UTC")),
            ),
            0
        ),
        (
            datetime(2022, 5, 12, tzinfo=zoneinfo.ZoneInfo("UTC")), 
            RangeCondition(
                datetime(2019, 1, 1, tzinfo=zoneinfo.ZoneInfo("UTC")),
                datetime(2020, 1, 1, tzinfo=zoneinfo.ZoneInfo("UTC")),
            ),
            2
        ),
        (
            datetime(2022, 12, 31, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")), 
            RangeCondition(
                datetime(2021, 1, 1, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")),
                datetime(2022, 1, 1, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")),
            ),
            0
        ),
    )
)
def test_previous_year_condition(current, expected, offset):
    factory = _init_factory(current)
    assert factory.build_previous_year_condition(current, offset) == expected

@pytest.mark.parametrize(
    "current,expected,offset",
    (   
        (
            datetime(2022, 1, 1), 
            RangeCondition(
                datetime(2022, 1, 1),
                datetime(2022, 1, 2),
            ),
            0
        ),
        (
            datetime(2022, 1, 1), 
            RangeCondition(
                datetime(2021, 1, 1),
                datetime(2022, 1, 1),
            ),
            1
        ),
        (
            datetime(2022, 5, 12, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")), 
            RangeCondition(
                datetime(2022, 1, 1, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")),
                datetime(2022, 5, 13, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")),
            ),
            0
        ),
        (
            datetime(2022, 12, 31, tzinfo=zoneinfo.ZoneInfo("UTC")), 
            RangeCondition(
                datetime(2022, 1, 1, tzinfo=zoneinfo.ZoneInfo("UTC")),
                datetime(2023, 1, 1, tzinfo=zoneinfo.ZoneInfo("UTC")),
            ),
            0
        ),
        (
            datetime(2022, 12, 31, tzinfo=zoneinfo.ZoneInfo("UTC")), 
            RangeCondition(
                datetime(2020, 1, 1, tzinfo=zoneinfo.ZoneInfo("UTC")),
                datetime(2021, 1, 1, tzinfo=zoneinfo.ZoneInfo("UTC")),
            ),
            2
        ),
    )
)
def test_build_previous_year_to_date_condition(current, expected, offset):
    factory = _init_factory(current)
    assert factory.build_previous_year_to_date_condition(current, offset) == expected


@pytest.mark.parametrize(
    "current,value,expected",
    (   
        (
            datetime(2022, 1, 1),
            2,
            LowerThanCondition(
                datetime(2021, 12, 31, 22),
            ),
        ),
        (
            datetime(2022, 5, 12, 0, 12, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")), 
            1,
            LowerThanCondition(
                datetime(2022, 5, 11, 23, 12, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")),
            ),
        ),
        (
            datetime(2022, 5, 12, 0, 12, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")), 
            1,
            LowerThanCondition(
                datetime(2022, 5, 11, 23, 12, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")),
            ),
        ),
        (
            datetime(2022, 2, 1, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")), 
            1,
            LowerThanCondition(
                datetime(2022, 1, 31, 23, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")),
            ),
        ),
    )
)
def test_build_before_x_hours_ago_condition(current, value, expected):
    factory = _init_factory(current)
    assert factory.build_before_x_hours_ago_condition(current, value) == expected

@pytest.mark.parametrize(
    "current,value,expected",
    (   
        (
            datetime(2021, 12, 31, 23),
            2,
            GreaterThanCondition(
                datetime(2022, 1, 1, 1)
            ),
        ),
        (
            datetime(2022, 5, 12, 0, 9, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")), 
            1,
            GreaterThanCondition(
                datetime(2022, 5, 12, 1, 9, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo"))
            ),
        ),
        (
            datetime(2022, 5, 12, 0, 9, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")), 
            2,
            GreaterThanCondition(
                datetime(2022, 5, 12, 2, 9, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")), 
            ),
        ),
        (
            datetime(2022, 1, 31, 23, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")), 
            1,
            GreaterThanCondition(
                datetime(2022, 2, 1, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo"))
            ),
        ),
    )
)
def test_build_after_x_hours_ago_condition(current, value, expected):
    factory = _init_factory(current)
    assert factory.build_after_x_hours_ago_condition(current, value) == expected

@pytest.mark.parametrize(
    "current,expected",
    (   
        (
            datetime(2021, 12, 31, 23),
            LowerThanOrEqualCondition(datetime(2021, 12, 31, 23))
        ),
        (
            datetime(2022, 5, 12, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")), 
            LowerThanOrEqualCondition(datetime(2022, 5, 12, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")))
        ),
        (
            datetime(2022, 1, 31, 23, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")), 
            LowerThanOrEqualCondition(datetime(2022, 1, 31, 23, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")))
        ),
    )
)
def test_build_past_condition(current, expected):
    factory = _init_factory(current)
    assert factory.build_past_condition(current) == expected

@pytest.mark.parametrize(
    "current,expected",
    (   
        (
            datetime(2021, 12, 31, 23),
            GreaterThanOrEqualCondition(datetime(2021, 12, 31, 23))
        ),
        (
            datetime(2022, 5, 12, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")), 
            GreaterThanOrEqualCondition(datetime(2022, 5, 12, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")))
        ),
        (
            datetime(2022, 1, 31, 23, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")), 
            GreaterThanOrEqualCondition(datetime(2022, 1, 31, 23, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")))
        ),
    )
)
def test_build_future_condition(current, expected):
    factory = _init_factory(current)
    assert factory.build_future_condition(current) == expected


@pytest.mark.parametrize(
    "current,operator,operator_to_mock,period,offset",
    (   
        (
            datetime(2025, 8, 10, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")),
            'today',
            'build_today_condition',
            1,
            0
        ),
        (
            datetime(2022, 8, 10, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")),
            'yesterday',
            'build_yesterday_condition',
            2,
            1
        ),
        (
            datetime(2022, 8, 10, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")),
            'previous_x_days',
            'build_previous_x_days_condition',
            3,
            2
        ),
        (
            datetime(2022, 8, 10, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")),
            'previous_x_days_to_date',
            'build_previous_x_days_to_date_condition',
            4,
            3
        ),
        (
            datetime(2022, 8, 10, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")),
            'previous_week',
            'build_previous_week_condition',
            5,
            4
        ),
        (
            datetime(2022, 8, 10, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")),
            'previous_week_to_date',
            'build_previous_week_to_date_condition',
            6,
            5
        ),
        (
            datetime(2022, 8, 10, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")),
            'previous_month',
            'build_previous_month_condition',
            7,
            6
        ),
        (
            datetime(2022, 8, 10, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")),
            'previous_month_to_date',
            'build_previous_month_to_date_condition',
            8,
            7
        ),
        (
            datetime(2022, 8, 10, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")),
            'previous_quarter',
            'build_previous_quarter_condition',
            9,
            8
        ),
        (
            datetime(2022, 8, 10, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")),
            'previous_quarter_to_date',
            'build_previous_quarter_to_date_condition',
            10,
            9
        ),
        (
            datetime(2022, 8, 10, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")),
            'previous_year',
            'build_previous_year_condition',
            11,
            10
        ),
        (
            datetime(2022, 8, 10, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")),
            'previous_year_to_date',
            'build_previous_year_to_date_condition',
            12,
            11
        ),
        (
            datetime(2022, 8, 10, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")),
            'before_x_hours_ago',
            'build_before_x_hours_ago_condition',
            13,
            12
        ),
        (
            datetime(2022, 8, 10, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")),
            'after_x_hours_ago',
            'build_after_x_hours_ago_condition',
            14,
            13
        ),
        (
            datetime(2022, 8, 10, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")),
            'past',
            'build_past_condition',
            15,
            14
        ),
        (
            datetime(2022, 8, 10, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")),
            'future',
            'build_future_condition',
            16,
            15
        ),
    )
)
def test_build(current, operator, operator_to_mock, period, offset):
    factory = _init_factory(current)
    with mock.patch.object(factory, operator_to_mock) as mocked:
        factory.build(operator, period, offset)
        mocked.assert_called_with(current_datetime=current, offset=offset, period=period)