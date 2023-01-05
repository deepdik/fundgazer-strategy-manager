import asyncio

from celery.schedules import crontab

from api.models.task_schedular_model import TaskType
from api.repository.task_schedular import get_task_list
from api.service.strategy_service import first_time_run_strategy
from api.utils.utils import is_required_scheduling
from main import celery, settings
from utils.logger import logger_config

logger = logger_config(__name__)


@celery.task(name='run_strategy', autoretry_for=(Exception,),
             max_retries=3, retry_backoff=True)
def run_strategy(*args, **kwargs):
    logger.info(args)
    logger.info(kwargs)
    if args[0] == TaskType.RUN_FIRST_TIME_STRATEGY:
        resp = asyncio.run(first_time_run_strategy(**kwargs))
    elif args[0] == TaskType.RUN_MASTER_STRATEGY:
        resp = asyncio.run(first_time_run_strategy(**kwargs))
    elif args[0] == TaskType.RUN_USER_STRATEGY:
        resp = asyncio.run(first_time_run_strategy(**kwargs))
    logger.info(resp)
    return resp


@celery.task(name='push_task_in_queue', autoretry_for=(Exception,),
             max_retries=3, retry_backoff=True)
async def push_task_in_queue():
    tasks = await get_task_list()
    for task in tasks:
        status, schedule_time = is_required_scheduling(task.get("cron_syntax"), settings.TASK_CRON_SLEEP)
        if task.get('is_active') and status:
            if task.get('task_type') == TaskType.RUN_FIRST_TIME_STRATEGY:
                queue = "master-strategy"
                priority = 9
            elif task.get('task_type') == TaskType.RUN_MASTER_STRATEGY:
                queue = "master-strategy"
                priority = 8
            elif task.get('task_type') == TaskType.RUN_USER_STRATEGY:
                queue = "user-strategy"
                priority = 7
            else:
                queue = "celery"
                priority = 5

            run_strategy.apply_async(
                queue=queue,
                priority=priority,
                args=[task.get('task_type')],
                kwargs=task.get('payload_data'),
                eta=schedule_time
            )



# celery.conf.beat_schedule = {
#     'run_every_9_min': {
#         'task': 'push_task_in_queue',
#         'schedule': crontab(minute="*/9"),
#         'args': [],
#         'kwargs': [],
#         'options': {'queue': 'task-queue'}
#     }
# }
