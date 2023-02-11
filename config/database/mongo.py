import asyncio
import os

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

# from pymongo import InsertOne, DeleteMany, ReplaceOne, UpdateOne

from config.config import get_config
from utils.logger import logger_config

logger = logger_config(__name__)

setting = get_config()


class MongoManager:
    """
    This class extends from ./database_manager.py
    which have the abstract methods to be re-used here.
    """

    __client: AsyncIOMotorClient = None
    __db: AsyncIOMotorDatabase = None
    __db_instances: dict = {}

    @classmethod
    async def get_instance(cls):
        if cls.__db is None:
            await cls.connect_to_database(setting.DB_URI)
        return cls.__db

    # database connect and close connections
    @classmethod
    async def connect_to_database(cls, path: str, database_name=None):
        # logger.info("Connecting to MongoDB")
        print(path, "path")
        if cls.__client is None:
            cls.__client = AsyncIOMotorClient(
                path,
                # in milliseconds
                maxIdleTimeMS=8000,
                # minimal pool size
                minPoolSize=10,
                # maximal pool size
                maxPoolSize=500,
                # connection timeout in miliseconds
                connectTimeoutMS=30000,
                # boolean
                retryWrites=True,
                # wait queue in miliseconds
                waitQueueTimeoutMS=30000,
                # in miliseconds
                serverSelectionTimeoutMS=30000,
            )

        cls.__client.get_io_loop = asyncio.get_running_loop

        if database_name == setting.STRATEGIES_DATABASE:
            logger.info("Connecting to database..." + database_name)
            cls.__db_instances[database_name] = cls.__client.fundgazer
        else:
            logger.info("Connecting to default database...")
            # for default database
            if os.getenv("ENVIRONMENT") == "PRD":
                cls.__db = cls.__client.prod_strategy_manager
            elif os.getenv("ENVIRONMENT") == "STG":
                cls.__db = cls.__client.stage_strategy_manager
            else:
                cls.__db = cls.__client.devdb

        logger.info("Connected to MongoDB -  %s environment!", os.getenv("ENV"))

    @classmethod
    async def get_instance_by_database(cls, database_name: str):
        if cls.__db_instances.get(database_name, None) is None:
            await cls.connect_to_database(setting.DB_URI, database_name)
        return cls.__db_instances.get(database_name)

    @classmethod
    async def close_database_connection(cls):
        logger.info("Closing connection to MongoDB")
        cls.__client.close()
        logger.info("MongoDB connection closed")
