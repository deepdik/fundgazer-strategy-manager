from fastapi import APIRouter

from api.service.task_schedular import task_scheduler
from api.utils.celery_tasks.task_schedular import push_task_in_queue
from api.validators.task_schedular import TaskSchedulerValidator, TaskValidator
from main import celery
from utils.response_handler import response

# APIRouter creates path operations for product module
router = APIRouter(
    prefix="/api/v1",
    tags=["Task Manager"],
    responses={404: {"description": "Not found"}},
)


@router.post("/add/immediate-task", response_description="")
async def add_immediate_task(data: TaskSchedulerValidator):
    await task_scheduler(data)
    return True


@router.post("/add/task", response_description="")
async def add_refresh_task(data: TaskValidator):
    await push_task_in_queue()
    # await add_task_service(data)
    return response(message="successfully created", success=200)


@router.get("revoke/task", response_description="revoke-task")
async def revoke_task(task_id: str):
    """"""
    try:
        celery.control.revoke(task_id)
        return True
    except Exception as e:
        return e
