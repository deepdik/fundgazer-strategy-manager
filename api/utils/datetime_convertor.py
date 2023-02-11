from datetime import datetime
import pytz
from pydantic.datetime_parse import timezone

from config.config import get_config

settings = get_config()


def convert_utc_to_local(
    timestamp, time_zone=settings.LOCAL_TIME_ZONE, need_date=False
):
    """
    convert UTC to Local Time zone
    """
    # Make a naive datetime.datetime in a given time zone aware
    if timestamp.tzname() != "UTC":
        raise ValueError("date time in not UTC format")
    localtz = pytz.timezone(time_zone)
    local_dt = timestamp.astimezone(localtz)
    if need_date:
        return datetime.strptime(local_dt, settings.DATE_FORMAT)
    return local_dt


def get_current_local_time():
    """
    :return:
    """
    local_dt = datetime.now()
    dt_utc = local_dt.astimezone(pytz.UTC)
    local_time = convert_utc_to_local(dt_utc)
    return local_time
