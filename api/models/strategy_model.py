from datetime import datetime, date
from enum import Enum
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field, json
from api.utils.py_object import PyObjectId


class PresetDataVersion(int, Enum):
    """Monday is 0 and Sunday is 6"""
    VERSION_0 = -1
    VERSION_1 = 0
    VERSION_2 = 1
    VERSION_3 = 2
    VERSION_4 = 3
    VERSION_5 = 4
    VERSION_6 = 5
    VERSION_7 = 6


class BaseDataModel(BaseModel):
    date: datetime
    version: PresetDataVersion
    ms_id: str

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class FilteredStocksModel(BaseDataModel):
    filtered_stocks: list


class UserPresetDataModel(BaseDataModel):
    preset_data: str
    user_id: str


class MasterPresetDataModel(BaseDataModel):
    preset_data: str


class CONDITION_TYPE(Enum):
    breakout = "Breakout"
    reversal = "Reversal"

class FILTERING_TYPE(Enum):
    breakout = "Breakout"
    reversal = "Reversal"

class MPT_STRATEGIES_VARIABLES(Enum):
    number_of_candles = 200