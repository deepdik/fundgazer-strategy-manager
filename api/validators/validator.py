from datetime import date, datetime, time, timedelta
from typing import List

from pydantic import BaseModel, validator
from pydantic.class_validators import root_validator
from pydantic.config import Enum
from pydantic.fields import Field

from api.utils.datetime_convertor import convert_utc_to_local



