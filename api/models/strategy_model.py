from datetime import datetime, date
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field, json
from api.utils.py_object import PyObjectId


class BaseDataModel(BaseModel):
    symbols: str
    date: datetime
    index_cls: str
    exchange: str
    timeframe: str

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class FilteredStocksModel(BaseDataModel):
    filtered_stocks: list


class UserPresetDataModel(BaseDataModel):
    preset_data: str


class MasterPresetDataModel(BaseDataModel):
    preset_data: str

