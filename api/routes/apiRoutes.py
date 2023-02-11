from fastapi import APIRouter

from api.controllers import strategy_controller, task_schedular

routers = APIRouter()
routers.include_router(strategy_controller.router)
routers.include_router(task_schedular.router)
