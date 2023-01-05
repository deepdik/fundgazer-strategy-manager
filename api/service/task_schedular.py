from datetime import datetime, timedelta

from requests import request

from api.models.general_models import TaskDueType, DataRefreshType
from api.models.task_schedular_model import TaskModel
from api.repository.task_schedular import save_task_schedular_data
from api.validators.task_schedular import TaskSchedulerValidator, TaskValidator
from utils.exception_handler import value_error_exception_handler
from utils.logger import logger_config
from utils.response_handler import response

logger = logger_config(__name__)


async def task_scheduler(data: TaskSchedulerValidator):
    delta_time = {}
    if data.run_after == TaskDueType.DAYS:
        delta_time[TaskDueType.DAYS] = data.run_after_val
    elif data.run_after == TaskDueType.HOURS:
        delta_time[TaskDueType.HOURS] = data.run_after_val
    elif data.run_after == TaskDueType.WEEKS:
        delta_time[TaskDueType.WEEKS] = data.run_after_val
    elif data.run_after == TaskDueType.MINUTES:
        delta_time[TaskDueType.MINUTES] = data.run_after_val
    elif data.run_after == TaskDueType.SECONDS:
        delta_time[TaskDueType.SECONDS] = data.run_after_val

    eta = datetime.utcnow() + timedelta(**delta_time)
    exp = eta + timedelta(minutes=5)

    print(eta, data, exp)
    # write Data save

    # save data to DB

    return True


async def add_task_service(data: TaskValidator):
    data_model = TaskModel(payload_data=data.payload_data,
                           cron_syntax=data.cron_syntax,
                           task_type=data.task_type)

    await save_task_schedular_data(data_model)


