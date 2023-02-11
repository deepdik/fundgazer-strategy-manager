import asyncio
import datetime
import time

from celery.schedules import crontab
from main import celery, settings


@celery.task(name="test", auto_retry=[], max_retries=3)
def test_celery(x, y):
    t1 = time.time()
    print(
        "long time task finished =>" + str((x + y)) + " " + str(datetime.datetime.now())
    )
    return x + y


@celery.task(
    name="first_time_run_strategy",
    autoretry_for=(Exception,),
    max_retries=3,
    retry_backoff=True,
)
def run_first_time_strategy():
    return {"status": True}


@celery.task(
    bind=True,
    name="periodic_",
    autoretry_for=(Exception,),
    max_retries=3,
    retry_backoff=True,
)
def periodic_(*args, **kwargs):
    # resp = asyncio.run(save_price_ticker_service(kwargs.get("symbols")))
    # print("Ticker Response", resp)
    # return resp
    pass


# celery.conf.beat_schedule = {
#     'binance_kline_data_refresh': {
#         'task': 'periodic_binance_kline',
#         'schedule': crontab(minute=''),
#         'args': [],
#         'kwargs': {'symbols': settings.SYMBOL_LIST, "exchange": 'binance', 'interval': '1d'},
#         'options': {'queue': 'data-handler'}
#     },
#     'binance_ticker_data_refresh': {
#         'task': 'periodic_binance_ticker',
#         'schedule': crontab(minute=''),
#         'args': [],
#         'kwargs': {"symbols": settings.SYMBOL_LIST},
#         'options': {'queue': 'data-handler'}
#     },
# }
