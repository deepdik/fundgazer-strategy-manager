from datetime import datetime
from enum import Enum

from bson import ObjectId
from pydantic import BaseModel, Field, json

from api.utils.datetime_convertor import get_current_local_time


class TaskType(str, Enum):
    RUN_MASTER_STRATEGY = "run_user_strategy"
    RUN_USER_STRATEGY = 'run_master_strategy'
    RUN_FIRST_TIME_STRATEGY = "run_first_time_strategy"


class TaskDueType(str, Enum):
    WEEKS = 'weeks'
    DAYS = 'days'
    MINUTES = 'minutes'
    HOURS = 'hours'
    SECONDS = 'seconds'


class TaskModel(BaseModel):
    created_at: datetime = get_current_local_time()
    payload_data: dict
    cron_syntax: str
    is_active: bool = True
    task_type: TaskType

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class TaskSchedularHistoryModel(BaseModel):
    task_id: str
    created_at: datetime
    run_at: datetime
    payload_data: dict

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
