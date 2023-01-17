import asyncio
import json

from celery.schedules import crontab

from api.models.task_schedular_model import TaskType
from api.repository.task_schedular import get_task_list, update_strategies
from api.service.strategy_service import first_time_run_strategy, run_master_strategy, run_user_strategy
from api.utils.utils import is_required_scheduling
from main import celery, settings
from utils.logger import logger_config

logger = logger_config(__name__)

TEST_SYMBOLS = "ICXUSDT,XMRUSDT,EOSUSDT,QTUMUSDT,ETCUSDT,VETUSDT,XLMUSDT,ETHUSDT,ADAUSDT,SOLUSDT,XRPUSDT,DOTUSDT," \
               "LTCUSDT,UNIUSDT,LINKUSDT,BCHUSDT,MATICUSDT,BTCUSDT,SNXUSDT,AAVEUSDT,RENUSDT,COMPUSDT,IOTAUSDT," \
               "KAVAUSDT,ATOMUSDT,MKRUSDT"


@celery.task(name='run_strategy', autoretry_for=(Exception,),
             max_retries=3, retry_backoff=True)
def run_strategy(*args, **kwargs):
    logger.info(args)
    logger.info(kwargs)
    if args[0] == TaskType.RUN_FIRST_TIME_STRATEGY:
        resp = asyncio.run(first_time_run_strategy(**kwargs))
        logger.info(f"finished running RUN_FIRST_TIME_STRATEGY with status => {resp}")
        if resp:
            asyncio.run(update_strategies(kwargs.get("ms_id")))
    elif args[0] == TaskType.RUN_MASTER_STRATEGY:
        logger.info(f"Started running RUN_MASTER_STRATEGY with status =>")
        resp = asyncio.run(run_master_strategy(**kwargs))
    elif args[0] == TaskType.RUN_USER_STRATEGY:
        logger.info(f"Started running RUN_USER_STRATEGY with status =>")
        resp = asyncio.run(run_user_strategy(**kwargs))
    logger.info(resp)
    return resp


@celery.task(name='push_task_in_queue', autoretry_for=(Exception,),
             max_retries=3, retry_backoff=True)
def push_task_in_queue():
    # get task list
    tasks = asyncio.run(get_task_list())
    # tasks = await get_task_list()
    # for master Strategy
    print(tasks)
    for task in tasks["master_strategy"]:
        print("Started adding master strategy task")
        status, schedule_time = is_required_scheduling(task.get("runTime"), settings.TASK_CRON_SLEEP)
        if task.get('status') and status:
            if isinstance(task.get('symbolList'), list):
                symbol_list = task.get('symbolList')
            elif isinstance(task.get('symbolList'), str):
                symbol_list = task.get('symbolList').split(",")

            payload = {
                "symbols": symbol_list,
                "timeframe": task.get('timeFrame'),
                "exchange": task.get('exchangeDetail')[0].get("exchangeName"),
                "ms_id": task.get('msId'),
            }

            if task.get('isFirstTime'):
                queue = "master-strategy"
                priority = 9
                task_type = TaskType.RUN_FIRST_TIME_STRATEGY
            else:
                queue = "master-strategy"
                priority = 8
                task_type = TaskType.RUN_MASTER_STRATEGY

            logger.info(payload)
            run_strategy.apply_async(
                queue=queue,
                priority=priority,
                args=[task_type],
                kwargs=payload,
                eta=schedule_time
            )

    for task in tasks["user_strategy"]:
        print("Started adding user strategy task")
        status, schedule_time = is_required_scheduling(task.get("runTime"), settings.TASK_CRON_SLEEP)
        if task.get('status') and status:
            if isinstance(task.get("msDetail")[0].get('symbolList'), list):
                symbol_list = task.get("msDetail")[0].get('symbolList')
            elif isinstance(task.get("msDetail")[0].get('symbolList'), str):
                symbol_list = task.get("msDetail")[0].get('symbolList').split(",")

            payload = {
                "capital": task.get('amountAdded'),
                "symbols": symbol_list,
                "timeframe": task.get("msDetail")[0].get('timeFrame'),
                "exchange": task.get('exchangeName'),
                "ms_id": task.get('msId'),
                "user_id": task.get('userId'),
            }

            logger.info(payload)
            run_strategy.apply_async(
                queue="user-strategy",
                priority=7,
                args=[TaskType.RUN_USER_STRATEGY],
                kwargs=payload,
                eta=schedule_time
            )


celery.conf.beat_schedule = {
    'run_every_10_min': {
        'task': 'push_task_in_queue',
        'schedule': crontab(minute="*/10"),
        'args': [],
        'kwargs': [],
        'options': {'queue': 'task-queue'}
    }
}
