from datetime import datetime, timedelta
import pytz

# from pydantic.datetime_parse import timezone

from config.config import get_config

settings = get_config()

HOLDIDAYS_NSE = [
    "26-01-2023",
    "07-03-2023",
    "30-03-2023",
    "04-04-2023",
    "07-04-2023",
    "14-04-2023",
    "21-04-2023",
    "01-05-2023",
    "28-06-2023",
    "15-08-2023",
    "19-09-2023",
    "02-10-2023",
    "24-10-2023",
    "14-11-2023",
    "27-11-2023",
    "25-12-2023",
]


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


def get_holdidays(exchange="fyers"):
    # await MongoManager().connect_to_database(settings.DB_URI)
    # # database = MongoManager.get_instance_by_database(settings.STRATEGIES_DATABASE)
    # database = await MongoManager.get_instance_by_database("fundgazer-dev")
    # # database = await MongoManager.get_instance()
    # response = await database.list_collections()
    # response = await database.tradingholidays.find_one()
    # r = [i for i in response]
    # print(r)
    return HOLDIDAYS_NSE


def get_business_days(start, end=None, number_of_days=None):
    if end is None and number_of_days is None:
        end = start + timedelta(days=32)

    if number_of_days is not None:
        if isinstance(number_of_days, int):
            end = start + timedelta(days=32)
        else:
            raise TypeError("number_of_days SHOULD BE A INTEGER")

    # get list of all days
    all_days = [start] + [start + timedelta(x + 1) for x in range((end - start).days)]

    # also remove exchange holdings
    holidays_list = get_holdidays()
    holiday_dates = [datetime.strptime(i, "%d-%m-%Y").date() for i in holidays_list]
    # print("Holidays: ", holiday_dates)

    # business days
    business_days = [day.date() for day in all_days if day.weekday() < 5]
    # print(business_days)
    trading_days = [i for i in business_days if i not in holiday_dates]
    trading_days.sort()
    return trading_days
