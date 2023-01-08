import os
from functools import lru_cache

from pydantic import BaseSettings
from dotenv import load_dotenv

load_dotenv('config/environ/.env')


class Settings(BaseSettings):
    """app config settings"""

    PROJECT_NAME: str = "dataHandler"
    VERSION: str = "1.0"
    DESCRIPTION: str = "description"
    SECRET_KET: str = None
    # DEBUG: bool = bool(os.getenv("DEBUG", "False"))
    DB_URI: str = os.getenv("MONGODB_URI")
    DATE_FORMAT = "DD-MM-YYYY"
    LOCAL_TIME_ZONE = "Asia/Calcutta"
    STRATEGIES_DATABASE: str


    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    CELERY_ACKS_LATE: bool

    DATA_HANDLER_BASE: str
    DATA_HANDLER_KLINE: str
    DATA_HANDLER_TICKER: str

    HTTP_TOO_MANY_REQ_SLEEP: int
    HTTP_REQ_TIMEOUT_SLEEP: int
    ASYNC_TIMEOUT_SLEEP: int
    ERROR_RETRY_COUNT: int

    TASK_CRON_SLEEP: int


    class Config:
        case_sensitive = True
        env_file = "/config/environ/.env"


@lru_cache
def get_config():
    return Settings()
