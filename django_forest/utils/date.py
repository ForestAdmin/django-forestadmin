from datetime import datetime
try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo

def get_timezone(string):
    return zoneinfo.ZoneInfo(string)

def get_utc_now():
    return get_now_aware_datetime(get_timezone('UTC'))

def get_now_aware_datetime(tz):
    return datetime.now(tz)
