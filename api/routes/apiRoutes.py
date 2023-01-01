from fastapi import APIRouter

from api.controllers import controller

routers = APIRouter()
routers.include_router(controller.router)
