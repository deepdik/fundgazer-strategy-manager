from fastapi.encoders import jsonable_encoder

from api.models.task_schedular_model import TaskModel
from config.database.mongo import MongoManager


async def save_task_schedular_data(data: TaskModel):
    database = await MongoManager.get_instance()
    await database.scheduled_task.insert_one(jsonable_encoder(data))


async def get_task_list():
    database = await MongoManager.get_instance()
    return await database.scheduled_task.find({}).to_list(1000)


async def save_imidiate_task_schedular_data(data: TaskModel):
    database = await MongoManager.get_instance()
    json_data = jsonable_encoder(data)
    await database.scheduled_task.insert_one(json_data)
