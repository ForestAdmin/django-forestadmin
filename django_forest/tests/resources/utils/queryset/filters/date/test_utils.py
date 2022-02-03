import pytest
import pandas
from unittest import mock
from datetime import datetime
from typing import Tuple
try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo

from django_forest.resources.utils.queryset.filters.date.utils import (
    get_previous_x_days,
    get_next_x_days,
    get_previous_x_weeks,
    get_previous_x_months,
    get_previous_x_years,
    get_previous_x_quarters,
    get_date_range,
    get_previous_x_hours,
    get_next_x_hours,
)

@pytest.mark.parametrize(
    "current,days,expected,offset",
    (
        (
            datetime(2021, 1, 12, 1, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")), 
            1, 
            (
                datetime(2021, 1, 11, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")), 
                datetime(2021, 1, 12, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe"))
            ),
            0
        ),
        (
            datetime(2021, 1, 12, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")), 
            1, 
            (
                datetime(2021, 1, 10, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")), 
                datetime(2021, 1, 11, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe"))
            ),
            1
        ),
        (
            datetime(2021, 1, 12, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")), 
            2, 
            (
                datetime(2021, 1, 10, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")), 
                datetime(2021, 1, 12, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo"))
            ),
            0
        ),
        (
            datetime(2021, 1, 12, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")), 
            2, 
            (
                datetime(2021, 1, 8, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")), 
                datetime(2021, 1, 10, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo"))
            ),
            1
        ),
        (
            datetime(2021, 1, 1, tzinfo=zoneinfo.ZoneInfo("UTC")), 
            3, 
            (
                datetime(2020, 12, 29, tzinfo=zoneinfo.ZoneInfo("UTC")), 
                datetime(2021, 1, 1, tzinfo=zoneinfo.ZoneInfo("UTC"))
            ),
            0
        ),
        (
            datetime(2021, 1, 1, tzinfo=zoneinfo.ZoneInfo("UTC")), 
            3, 
            (
                datetime(2020, 12, 26, tzinfo=zoneinfo.ZoneInfo("UTC")), 
                datetime(2020, 12, 29, tzinfo=zoneinfo.ZoneInfo("UTC"))
            ),
            1
        ),
        (
            datetime(2021, 1, 1, tzinfo=zoneinfo.ZoneInfo("UTC")), 
            3, 
            (
                datetime(2020, 12, 23, tzinfo=zoneinfo.ZoneInfo("UTC")), 
                datetime(2020, 12, 26, tzinfo=zoneinfo.ZoneInfo("UTC"))
            ),
            2
        ),
        (
            datetime(2022, 3, 1, tzinfo=zoneinfo.ZoneInfo("America/Araguaina")), 
            1, 
            (
                datetime(2022, 2, 28, tzinfo=zoneinfo.ZoneInfo("America/Araguaina")), 
                datetime(2022, 3, 1, tzinfo=zoneinfo.ZoneInfo("America/Araguaina"))
            ),
            0
        ),
        (
            datetime(2022, 3, 1, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")), 
            365, 
            (
                datetime(2021, 3, 1, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")), 
                datetime(2022, 3, 1, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo"))
            ),
            0
        ),
        (
            datetime(2022, 3, 1, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")), 
            365, 
            (
                datetime(2011, 3, 4, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")), 
                datetime(2012, 3, 3, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo"))
            ),
            10
        ),
        (
            datetime(2024, 3, 1, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")), 
            1, 
            (
                datetime(2024, 2, 29, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")), 
                datetime(2024, 3, 1, tzinfo=zoneinfo.ZoneInfo("Europe/Paris"))
            ),
            0
        ),
        (
            datetime(2024, 3, 1, tzinfo=zoneinfo.ZoneInfo("Asia/Chungking")), 
            365, 
            (
                datetime(2023, 3, 2, tzinfo=zoneinfo.ZoneInfo("Asia/Chungking")), 
                datetime(2024, 3, 1, tzinfo=zoneinfo.ZoneInfo("Asia/Chungking"))
            ),
            0
        ),
    )
)
def test_get_previous_x_days(current: datetime, days: int, expected: Tuple[datetime], offset: int):
    assert get_previous_x_days(current, days, offset) == expected


@pytest.mark.parametrize(
    "current,days,expected,offset",
    (
        (
            datetime(2021, 1, 12, 1, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")), 
            1, 
            (
                datetime(2021, 1, 12, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")), 
                datetime(2021, 1, 13, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe"))
            ),
            0
        ),
        (
            datetime(2021, 1, 12, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")), 
            1, 
            (
                datetime(2021, 1, 13, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")), 
                datetime(2021, 1, 14, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe"))
            ),
            1
        ),
            (
            datetime(2021, 1, 12, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")), 
            2, 
            (
                datetime(2021, 1, 12, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")), 
                datetime(2021, 1, 14, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo"))
            ),
            0
        ),
        (
            datetime(2021, 1, 12, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")), 
            2, 
            (
                datetime(2021, 1, 18, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")), 
                datetime(2021, 1, 20, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo"))
            ),
            3
        ),
        (
            datetime(2020, 12, 29, tzinfo=zoneinfo.ZoneInfo("UTC")), 
            3, 
            (
                datetime(2020, 12, 29, tzinfo=zoneinfo.ZoneInfo("UTC")), 
                datetime(2021, 1, 1, tzinfo=zoneinfo.ZoneInfo("UTC"))
            ),
            0
        ),
        (
            datetime(2020, 12, 29, tzinfo=zoneinfo.ZoneInfo("UTC")), 
            3, 
            (
                datetime(2021, 1, 1, tzinfo=zoneinfo.ZoneInfo("UTC")), 
                datetime(2021, 1, 4, tzinfo=zoneinfo.ZoneInfo("UTC"))
            ),
            1
        ),
        (
            datetime(2022, 2, 28, tzinfo=zoneinfo.ZoneInfo("America/Araguaina")), 
            1, 
            (
                datetime(2022, 2, 28, tzinfo=zoneinfo.ZoneInfo("America/Araguaina")), 
                datetime(2022, 3, 1, tzinfo=zoneinfo.ZoneInfo("America/Araguaina"))
            ),
            0
        ),
        (
            datetime(2022, 2, 28, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")), 
            365, 
            (
                datetime(2022, 2, 28, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")), 
                datetime(2023, 2, 28, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo"))
            ),
            0
        ),
        (
            datetime(2022, 2, 28, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")), 
            365, 
            (
                datetime(2023, 2, 28, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")), 
                datetime(2024, 2, 28, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo"))
            ),
            1
        ),
        (
            datetime(2024, 2, 29, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")), 
            1, 
            (
                datetime(2024, 2, 29, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")), 
                datetime(2024, 3, 1, tzinfo=zoneinfo.ZoneInfo("Europe/Paris"))
            ),
            0
        ),
    )
)
def test_get_next_x_days(current: datetime, days: int, expected: Tuple[datetime], offset: int):
    assert get_next_x_days(current, days, offset) == expected

@pytest.mark.parametrize(
    "current,weeks,expected,offset",
    (
        (
            datetime(2022, 1, 5, 1, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")), 
            52, 
            (
                datetime(2021, 1, 4, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")), 
                datetime(2022, 1, 3, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe"))
            ),
            0
        ),
        (
            datetime(2022, 1, 5, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")), 
            52, 
            (
                datetime(2020, 1, 6, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")), 
                datetime(2021, 1, 4, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe"))
            ),
            1
        ),
        (
            datetime(2022, 1, 5, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")), 
            1, 
            (
                datetime(2021, 12, 27, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")), 
                datetime(2022, 1, 3, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo"))
            ),
            0
        ),
        (
            datetime(2022, 1, 5, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")), 
            1, 
            (
                datetime(2021, 12, 20, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")), 
                datetime(2021, 12, 27, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo"))
            ),
            1
        ),
        (
            datetime(2017, 11, 6, tzinfo=zoneinfo.ZoneInfo("UTC")), 
            3, 
            (
                datetime(2017, 10, 16, tzinfo=zoneinfo.ZoneInfo("UTC")),
                datetime(2017, 11, 6, tzinfo=zoneinfo.ZoneInfo("UTC"))
            ),
            0
        ),
        (
            datetime(2017, 11, 6, tzinfo=zoneinfo.ZoneInfo("UTC")), 
            3, 
            (
                datetime(2017, 9, 4, tzinfo=zoneinfo.ZoneInfo("UTC")),
                datetime(2017, 9, 25, tzinfo=zoneinfo.ZoneInfo("UTC"))
            ),
            2
        ),
    )
)
def test_get_previous_x_weeks(current: datetime, weeks: int, expected: Tuple[datetime], offset: int):
    assert get_previous_x_weeks(current, weeks, offset) == expected


@pytest.mark.parametrize(
    "current,months,expected,offset",
    (
        (
            datetime(2022, 1, 4, 1, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")), 
            1, 
            (
                datetime(2021, 12, 1, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")), 
                datetime(2022, 1, 1, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe"))
            ),
            0
        ),
        (
            datetime(2022, 1, 4, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")), 
            1, 
            (
                datetime(2021, 11, 1, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")), 
                datetime(2021, 12, 1, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe"))
            ),
            1
        ),
        (
            datetime(2022, 2, 4, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")), 
            1, 
            (
                datetime(2022, 1, 1, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")), 
                datetime(2022, 2, 1, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo"))
            ),
            0
        ),
        (
            datetime(2022, 1, 5, tzinfo=zoneinfo.ZoneInfo("UTC")), 
            12, 
            (
                datetime(2021, 1, 1, tzinfo=zoneinfo.ZoneInfo("UTC")), 
                datetime(2022, 1, 1, tzinfo=zoneinfo.ZoneInfo("UTC"))
            ),
            0
        ),
        (
            datetime(2022, 1, 5, tzinfo=zoneinfo.ZoneInfo("UTC")), 
            12, 
            (
                datetime(2018, 1, 1, tzinfo=zoneinfo.ZoneInfo("UTC")), 
                datetime(2019, 1, 1, tzinfo=zoneinfo.ZoneInfo("UTC"))
            ),
            3
        ),
        (
            datetime(2022, 1, 5, tzinfo=zoneinfo.ZoneInfo("America/Araguaina")),
            17, 
            (
                datetime(2020, 8, 1, tzinfo=zoneinfo.ZoneInfo("America/Araguaina")), 
                datetime(2022, 1, 1, tzinfo=zoneinfo.ZoneInfo("America/Araguaina"))
            ),
            0
        ),
        (
            datetime(2022, 1, 5, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")), 
            29, 
            (
                datetime(2019, 8, 1, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")), 
                datetime(2022, 1, 1, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo"))
            ),
            0
        ),
        (
            datetime(2022, 12, 5, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")), 
            121, 
            (
                datetime(2012, 11, 1, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")), 
                datetime(2022, 12, 1, tzinfo=zoneinfo.ZoneInfo("Europe/Paris"))
            ),
            0
        ),
    )
)
def test_get_previous_x_months(current: datetime, months: int, expected: Tuple[datetime], offset: int):
    assert get_previous_x_months(current, months, offset) == expected

@pytest.mark.parametrize(
    "current,years,expected,offset",
    (   
        (
            datetime(2022, 1, 12, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")), 
            1, 
            (
                datetime(2021, 1, 1, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")), 
                datetime(2022, 1, 1, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe"))
            ),
            0
        ),
        (
            datetime(2022, 1, 12, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")), 
            1, 
            (
                datetime(2017, 1, 1, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")), 
                datetime(2018, 1, 1, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe"))
            ),
            4
        ),
        (
            datetime(2022, 2, 5, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")), 
            2, 
            (
                datetime(2020, 1, 1, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")), 
                datetime(2022, 1, 1, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo"))
            ),
            0
        ),
        (
            datetime(2022, 2, 5, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")), 
            2, 
            (
                datetime(2018, 1, 1, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")), 
                datetime(2020, 1, 1, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo"))
            ),
            1
        ),
        (
            datetime(2022, 3, 31, tzinfo=zoneinfo.ZoneInfo("UTC")), 
            10, 
            (
                datetime(2012, 1, 1, tzinfo=zoneinfo.ZoneInfo("UTC")), 
                datetime(2022, 1, 1, tzinfo=zoneinfo.ZoneInfo("UTC"))
            ),
            0
        ),
        (
            datetime(2022, 4, 1, tzinfo=zoneinfo.ZoneInfo("America/Araguaina")), 
            104, 
            (
                datetime(1918, 1, 1, tzinfo=zoneinfo.ZoneInfo("America/Araguaina")), 
                datetime(2022, 1, 1, tzinfo=zoneinfo.ZoneInfo("America/Araguaina"))
            ),
            0
        ),

        (
            datetime(2022, 4, 1, tzinfo=zoneinfo.ZoneInfo("America/Araguaina")), 
            104, 
            (
                datetime(1814, 1, 1, tzinfo=zoneinfo.ZoneInfo("America/Araguaina")), 
                datetime(1918, 1, 1, tzinfo=zoneinfo.ZoneInfo("America/Araguaina"))
            ),
            1
        ),
    )
)
def test_get_previous_x_years(current: datetime, years: int, expected: Tuple[datetime], offset: int):
    assert get_previous_x_years(current, years, offset) == expected

@pytest.mark.parametrize(
    "current,quarter,expected,offset",
    (   
        (	
            datetime(2022, 1, 1, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")),
            1,
            (
                datetime(2021, 10, 1, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")), 
                datetime(2022, 1, 1, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe"))
            ),
            0
        ),
        (	
            datetime(2022, 1, 1, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")),
            1,
            (
                datetime(2021, 4, 1, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")), 
                datetime(2021, 7, 1, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe"))
            ),
            2
        ),
        (
            datetime(2021, 4, 12, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")),
            1, 
            (
                datetime(2021, 1, 1, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")), 
                datetime(2021, 4, 1, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo"))
            ),
            0
        ),
        (
            datetime(2012, 3, 31, tzinfo=zoneinfo.ZoneInfo("UTC")),
            2,
            (
                datetime(2011, 7, 1, tzinfo=zoneinfo.ZoneInfo("UTC")),
                datetime(2012, 1, 1, tzinfo=zoneinfo.ZoneInfo("UTC"))
            ),
            0
        ),
        (
            datetime(2018, 12, 1, tzinfo=zoneinfo.ZoneInfo("America/Araguaina")),
            4, 
            (
                datetime(2017, 10, 1, tzinfo=zoneinfo.ZoneInfo("America/Araguaina")), 
                datetime(2018, 10, 1, tzinfo=zoneinfo.ZoneInfo("America/Araguaina"))
            ),
            0
        ),
        (
            datetime(2018, 12, 1, tzinfo=zoneinfo.ZoneInfo("America/Araguaina")),
            4, 
            (
                datetime(2014, 10, 1, tzinfo=zoneinfo.ZoneInfo("America/Araguaina")), 
                datetime(2015, 10, 1, tzinfo=zoneinfo.ZoneInfo("America/Araguaina"))
            ),
            3
        ),
        (
            datetime(2018, 12, 1, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")),
            4,
            (
                datetime(2017, 10, 1, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo")),
                datetime(2018, 10, 1, tzinfo=zoneinfo.ZoneInfo("Africa/Malabo"))
            ),
            0
        ),
        (
            datetime(2018, 1, 1, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")),
            3,
            (
                datetime(2017, 4, 1, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")),
                datetime(2018, 1, 1, tzinfo=zoneinfo.ZoneInfo("Europe/Paris"))
            ),
            0
        ),
    )
)
def test_get_first_day_of_previous_x_quarter(current: datetime, quarter: int, expected: Tuple[datetime], offset: int):
    assert get_previous_x_quarters(current, quarter, offset) == expected

@pytest.mark.parametrize(
    "current,period,expected,offset",
    (   
        (	
            datetime(2022, 1, 1, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")),
            1,
            (
                datetime(2021, 12, 31, 23, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")), 
                datetime(2022, 1, 1, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe"))
            ),
            0
        ),
        (	
            datetime(2022, 1, 1, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")),
            1,
            (
                datetime(2021, 12, 31, 21, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")), 
                datetime(2021, 12, 31, 22, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe"))
            ),
            2
        ),
        (
            datetime(2021, 4, 12, 1, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")),
            24, 
            (
                datetime(2021, 4, 11, 1, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")), 
                datetime(2021, 4, 12, 1, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo"))
            ),
            0
        ),
        (
            datetime(2021, 4, 12, 1, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")),
            24, 
            (
                datetime(2021, 4, 7, 1, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")), 
                datetime(2021, 4, 8, 1, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo"))
            ),
            4
        ),
        (
            datetime(2012, 3, 31, 12, tzinfo=zoneinfo.ZoneInfo("UTC")),
            2,
            (
                datetime(2012, 3, 31, 10, tzinfo=zoneinfo.ZoneInfo("UTC")),
                datetime(2012, 3, 31, 12, tzinfo=zoneinfo.ZoneInfo("UTC"))
            ),
            0
        ),
    )
)
def test_get_previous_x_hours(current: datetime, period: int, expected: Tuple[datetime], offset: int):
    assert get_previous_x_hours(current, period, offset) == expected

@pytest.mark.parametrize(
    "current,period,expected,offset",
    (   
        (	
            datetime(2021, 12, 31, 23, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")),
            1,
            (
                datetime(2021, 12, 31, 23, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")),
                datetime(2022, 1, 1, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")), 
            ),
            0
        ),
        (	
            datetime(2021, 12, 31, 23, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")),
            1,
            (
                datetime(2022, 1, 1, 1, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")),
                datetime(2022, 1, 1, 2, tzinfo=zoneinfo.ZoneInfo("Asia/Aqtobe")), 
            ),
            2
        ),
        (
            datetime(2021, 4, 12, 1, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")),
            24, 
            (
                datetime(2021, 4, 12, 1, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")), 
                datetime(2021, 4, 13, 1, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo"))
            ),
            0
        ),
        (
            datetime(2021, 4, 12, 1, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")),
            24, 
            (
                datetime(2021, 4, 15, 1, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo")), 
                datetime(2021, 4, 16, 1, tzinfo=zoneinfo.ZoneInfo("Antarctica/McMurdo"))
            ),
            3
        ),
        (
            datetime(2012, 3, 31, 10, tzinfo=zoneinfo.ZoneInfo("UTC")),
            2,
            (
                datetime(2012, 3, 31, 10, tzinfo=zoneinfo.ZoneInfo("UTC")),
                datetime(2012, 3, 31, 12, tzinfo=zoneinfo.ZoneInfo("UTC"))
            ),
            0
        ),
    )
)
def test_get_next_x_hours(current: datetime, period: int, expected: Tuple[datetime], offset: int):
    assert get_next_x_hours(current, period, offset) == expected
    
@pytest.mark.parametrize(
    "current,frequency,period,previous,offset,expected",
    ( 
        (
            datetime(2018, 12, 1, tzinfo=zoneinfo.ZoneInfo("America/Araguaina")),
            'X', 
            2, 
            False, 
            0,
            (
                datetime(2012, 1, 1, tzinfo=zoneinfo.ZoneInfo("America/Araguaina")),
                datetime(2002, 1, 1, tzinfo=zoneinfo.ZoneInfo("America/Araguaina"))
            )
        ),
        (
            datetime(2018, 12, 1, tzinfo=zoneinfo.ZoneInfo("America/Araguaina")),
            'XY', 
            2, 
            True, 
            1,
            (
                datetime(2022, 1, 1, tzinfo=zoneinfo.ZoneInfo("America/Araguaina")),
                datetime(2012, 1, 1, tzinfo=zoneinfo.ZoneInfo("America/Araguaina"))
            )
        ),
        (
            datetime(2018, 12, 1, tzinfo=zoneinfo.ZoneInfo("America/Araguaina")),
            'XY', 
            2, 
            True, 
            2,
            (
                datetime(2022, 1, 1, tzinfo=zoneinfo.ZoneInfo("America/Araguaina")),
                datetime(2012, 1, 1, tzinfo=zoneinfo.ZoneInfo("America/Araguaina"))
            )
        ),
    )
)
def test_get_date_range(current: datetime, frequency: str, period: int, previous: bool, offset: int, expected: Tuple[datetime]):
    with mock.patch('django_forest.resources.utils.queryset.filters.date.utils.pd') as pd:
        pd.date_range.return_value = [
            pandas.Timestamp(2022, 1, 1),
            pandas.Timestamp(2012, 1, 1),
            pandas.Timestamp(2002, 1, 1)
        ]
        pd.to_datetime.return_value = 'faketimestamp'
        res = get_date_range(current, frequency, period, previous, offset)
        pd.to_datetime.assert_called_with(current.replace(tzinfo=zoneinfo.ZoneInfo('UTC')))
        kwargs = {
            'freq': frequency,
            'periods': offset + 2,
        }
        if period:
            kwargs['freq'] = f"{period}{frequency}"
        if previous:
            kwargs["end"] = "faketimestamp"
        else:
            kwargs["start"] = "faketimestamp"

        pd.date_range.assert_called_with(**kwargs)
        assert res == expected