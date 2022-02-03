import pytest
try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo
from datetime import datetime
from django_forest.utils.date import (
    get_now_aware_datetime,
    get_timezone,
    get_utc_now,
)
from freezegun import freeze_time

@pytest.mark.parametrize(
    "timezone",
    (
        "UTC",
        "Europe/Paris",
        "Europe/Berlin"
    )
)
def test_get_timezone(timezone):
    assert get_timezone(timezone) == zoneinfo.ZoneInfo(timezone)

@freeze_time("2021-12-1 12:00:01")
def test_get_utc_now():
    assert get_utc_now() == datetime(2021, 12, 1, 12, 0, 1, tzinfo=zoneinfo.ZoneInfo('UTC'))
