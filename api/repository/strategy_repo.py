from typing import List, Union

from fastapi.encoders import jsonable_encoder

from api.models.strategy_model import MasterPresetDataModel, FilteredStocksModel, UserPresetDataModel, PresetDataVersion
from config.database.mongo import MongoManager


async def save_master_preset_data(data: MasterPresetDataModel):
    print(data)
    database = await MongoManager.get_instance()
    query = {
        "symbols": data.symbols,
        "exchange": data.exchange,
        "timeframe": data.timeframe,
        "index_cls": data.index_cls,
        "version": data.version
    }
    json_data = jsonable_encoder(data)
    update = {"$set": json_data}
    # await database.master_preset_data.drop()
    await database.master_preset_data.update_one(query, update, upsert=True)


async def get_master_preset_data(symbols: str, exchange: str,
                                 timeframe: str, index_cls: str, version: PresetDataVersion):
    database = await MongoManager.get_instance()
    query = {
        "symbols": symbols,
        "exchange": exchange,
        "timeframe": timeframe,
        "index_cls": index_cls,
        "version": version
    }
    # return await database.master_preset_data.find(query).sort([('date', 1), ]).limit(1).to_list(10)
    preset_data = await database.master_preset_data.find_one(query, {'_id': False})
    if preset_data:
        return preset_data
    else:
        # get first time run version
        query["version"] = PresetDataVersion.VERSION_0.value
        return await database.master_preset_data.find_one(query, {'_id': False})


async def save_filtered_stocks(data: FilteredStocksModel):
    database = await MongoManager.get_instance()
    query = {
        "symbols": data.symbols,
        "exchange": data.exchange,
        "timeframe": data.timeframe,
        "index_cls": data.index_cls,
        "version": data.version
    }
    update = {"$set": jsonable_encoder(data)}
    # await database.filtered_stocks.drop()
    await database.filtered_stocks.update_one(query, update, upsert=True)


async def get_filtered_stocks(symbols: str, exchange: str,
                              timeframe: str, index_cls: str, version: PresetDataVersion):
    database = await MongoManager.get_instance()
    query = {
        "symbols": symbols,
        "exchange": exchange,
        "timeframe": timeframe,
        "index_cls": index_cls,
        "version": version
    }
    # await database.filtered_stocks.drop()
    return await database.filtered_stocks.find_one(query, {'_id': False})


async def save_user_preset_data(data: UserPresetDataModel):
    database = await MongoManager.get_instance()
    query = {
        "symbols": data.symbols,
        "exchange": data.exchange,
        "timeframe": data.timeframe,
        "index_cls": data.index_cls,
        "version": data.version
    }
    update = {"$set": jsonable_encoder(data)}
    # await database.filtered_stocks.drop()
    await database.user_preset_data.update_one(query, update, upsert=True)


async def get_user_preset_data(symbols: str, exchange: str,
                               timeframe: str, index_cls: str, version: PresetDataVersion):
    database = await MongoManager.get_instance()
    query = {"symbols": symbols,
             "exchange": exchange,
             "timeframe": timeframe,
             "index_cls": index_cls,
             "version": version
             }
    data = await database.user_preset_data.find_one(query, {'_id': False})
    if not data:
        return await get_master_preset_data(symbols, exchange, timeframe, index_cls, version)
    return data
