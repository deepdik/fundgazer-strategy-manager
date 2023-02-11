from dotenv import load_dotenv
import os
import pymongo

from datetime import datetime

from api.utils.strategy_logics import constants

# cached_client = MongoClient(os.getenv("MONGO_URL"))
# cached_db = cached_client[os.getenv("MONGO_DB")]

load_dotenv("/config/environ/.env")
DATA_HANDLER_BASE = os.environ["DATA_HANDLER_BASE"]
KLINE_DATA = os.environ["DATA_HANDLER_KLINE"]


def _convert_to_ohlcv(ohlcv):
    return {
        "Date": ohlcv["t"],
        "Open": ohlcv["o"],
        "High": ohlcv["h"],
        "Low": ohlcv["l"],
        "Close": ohlcv["c"],
        "Volume": ohlcv["v"],
    }


class DbManager:
    def __init__(self, platform):
        self.platform = platform
        self.client = ""

        self.db = ""

    def close(self):
        self.client.close()
        self.client = None
        self.db = None

    def get_strategy_data(self, strategy_name, platform):
        doc = self.db[constants.MONGO_STRATEGY_SAVED_DATA].find_one(
            {
                "strategy_name": strategy_name,
                "platform": platform,
            }
        )

        bin_data = None
        if doc and doc["bin_data"]:
            bin_data = doc["bin_data"]

        return bin_data

    def save_strategy_data(self, strategy_name, platform, bin_data):
        doc = {
            "strategy_name": strategy_name,
            "platform": platform,
            "bin_data": bin_data,
        }

        return self.db[constants.MONGO_STRATEGY_SAVED_DATA].update_one(
            {
                "strategy_name": strategy_name,
                "platform": platform,
            },
            {"$set": doc},
            upsert=True,
        )

    def get_ohlcv_config(self, platform, timeframe):
        return self.db[constants.MONGO_OHLCV_DATA_CONFIG_COLLECTION].find_one(
            {"platform": platform, "timeframe": timeframe}
        )

    async def _get_candles(self, symbol, timeframe, n):
        return []

    def get_1m_candles(self, symbol, n=3000):
        return self._get_candles(symbol, "1m", n=n)

    def get_5m_candles(self, symbol, n=1000):
        return self._get_candles(symbol, "5m", n=n)

    def get_1h_candles(self, symbol, n=400):
        return self._get_candles(symbol, "1h", n=n)

    async def get_1d_candles(self, symbol, n=400):
        return await self._get_candles(symbol, "1d", n=n)

    def update_pattern_backtest_progress(
        self,
        config_file_name,
        config_id,
        indicator_file_name,
        status: str,
        error_msg: str = None,
    ):
        crrent_time = datetime.now()
        save_data = {
            "status": status,
            "error_msg": error_msg,
            "update_time": crrent_time,
        }

        if status == "INITIALIZING":
            save_data["start_time"] = crrent_time

        self.db["patternBacktest"].update_one(
            {
                "config_file_name": config_file_name,
                "config_id": config_id,
                "indicator_file_name": indicator_file_name,
            },
            {"$set": save_data},
            upsert=False,
        )

    def update_indicator_job(
        self,
        config_file_name,
        indicator_file_name,
        status: str,
        error_msg: str = None,
    ):
        crrent_time = datetime.now()
        save_data = {
            "status": status,
            "error_msg": error_msg,
            "update_time": crrent_time,
        }

        self.db["patternIndicatorBacktest"].update_one(
            {
                "config_file_name": config_file_name,
                "indicator_file_name": indicator_file_name,
            },
            {"$set": save_data},
            upsert=False,
        )

    def queue_pattern_backtest_job(
        self,
        config_file_name,
        indicator_file_name,
    ):
        crrent_time = datetime.now()
        save_data = {
            "status": "QUEUED",
            "update_time": crrent_time,
        }

        self.db["patternBacktest"].update_many(
            {
                "config_file_name": config_file_name,
                "indicator_file_name": indicator_file_name,
            },
            {"$set": save_data},
            upsert=False,
        )

    def delete_pattern_backtest_job(
        self,
        config_file_name,
        indicator_file_name,
    ):
        self.db["patternBacktest"].delete_many(
            {
                "config_file_name": config_file_name,
                "indicator_file_name": indicator_file_name,
            },
        )

    def add_pattern_backtest_job(
        self, pattern_jobs: list, status="GENERATING_INDICATOR_PICKLE"
    ):
        crrent_time = datetime.now()
        for job in pattern_jobs:
            job["status"] = status
            job["update_time"] = crrent_time

        self.db["patternBacktest"].insert_many(pattern_jobs)

    def get_next_indicator_job(self):
        return self.db["patternIndicatorBacktest"].find_one_and_update(
            filter={"status": "QUEUED"},
            update={"$set": {"status": "IN_PROGRESS"}},
            upsert=False,
        )

    def get_next_pattern_job(self, number_of_jobs=1):
        jobs = []
        for _ in range(number_of_jobs):
            job = self.db["patternBacktest"].find_one_and_update(
                filter={"status": "QUEUED"},
                update={"$set": {"status": "IN_PROGRESS"}},
                upsert=False,
            )

            if job:
                jobs.append(job)
            else:
                # if any iteration is null that means there are no jobs so return the current jobs
                return jobs

        return jobs


class Transaction_Functor(object):
    """
    Wrap a function so we can pass in a pymongo session object
    """

    def __init__(self, func, *args, **kwargs):
        self._func = func
        self._args = args
        self._kwargs = kwargs
        self._session = None

    def __call__(self, session=None):
        if session is None:
            return self._func(*self._args, **self._kwargs)
        else:
            self._kwargs["session"] = session
            return self._func(*self._args, **self._kwargs)


def commit_with_retry(session):
    while True:
        try:
            # Commit uses write concern set at transaction start.
            session.commit_transaction()
            print("Transaction committed.")
            break
        except (
            pymongo.errors.ConnectionFailure,
            pymongo.errors.OperationFailure,
        ) as exc:
            # Can retry commit
            if exc.has_error_label("UnknownTransactionCommitResult"):
                print(
                    "UnknownTransactionCommitResult, retrying " "commit operation ..."
                )
                continue
            else:
                print("Error during commit ...")
                raise


def run_transaction_with_retry(functor, session):
    assert isinstance(functor, Transaction_Functor)
    while True:
        try:
            with session.start_transaction():
                result = functor(session)  # performs transaction
                commit_with_retry(session)
            break
        except (
            pymongo.errors.ConnectionFailure,
            pymongo.errors.OperationFailure,
        ) as exc:
            # If transient error, retry the whole transaction
            if exc.has_error_label("TransientTransactionError"):
                print("TransientTransactionError, retrying " "transaction ...")
                continue
            else:
                raise

    return result
