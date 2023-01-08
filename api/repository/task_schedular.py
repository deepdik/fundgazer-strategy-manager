from fastapi.encoders import jsonable_encoder

from api.models.task_schedular_model import TaskModel
from config.database.mongo import MongoManager
from main import settings


async def save_task_schedular_data(data: TaskModel):
    database = await MongoManager.get_instance()
    await database.scheduled_task.insert_one(jsonable_encoder(data))


async def get_task_list():
    database = await MongoManager.get_instance_by_database(settings.STRATEGIES_DATABASE)

    query1 = {
        "$lookup":
             {
                "from": "exchanges",
                "localField": "supportedExchangeId",
                "foreignField": "exchangeId",
                "as": "exchangeDetail"
             }
       }
    query2 = {"$match": {"status": 'active'}}
    task = {"master_strategy": await database.masterstrategies.aggregate([query1, query2]).to_list(1000)}
    # get master strategies

    query1 = {
        "$lookup":
             {
                "from": "masterstrategies",
                "localField": "msId",
                "foreignField": "msId",
                "as": "msDetail"
             }
       }

    # get user strategies
    task["user_strategy"] = await database.strategies.aggregate([query1, query2]).to_list(1000)
    return task


async def update_strategies(ms_id: str):
    database = await MongoManager.get_instance_by_database(settings.STRATEGIES_DATABASE)
    query = {
        "msId": ms_id,
    }
    update = {"$set": {"isFirstTime": False}}
    return await database.masterstrategies.update_one(query, update)
