from datetime import datetime

from croniter import croniter
from pydantic import validator
from pydantic.main import BaseModel

from api.models.general_models import DataRefreshType, TaskDueType
from api.models.task_schedular_model import TaskType
from api.utils.datetime_convertor import get_current_local_time


class TaskSchedulerValidator(BaseModel):
    refresh_type: DataRefreshType
    run_after: TaskDueType
    run_after_val: int
    data: dict


class TaskValidator(BaseModel):
    payload_data: dict
    cron_syntax: str
    task_type: TaskType
    @validator('cron_syntax')
    def cron_syntax_validate(cls, value):
        if not croniter.is_valid(value):
            raise ValueError("Invalid Cron Syntax")
        return value
