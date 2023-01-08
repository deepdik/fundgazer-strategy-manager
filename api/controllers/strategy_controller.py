from datetime import datetime, timedelta

from fastapi import APIRouter

from api.repository.task_schedular import get_task_list
from api.service.strategy_service import run_user_strategy, first_time_run_strategy, run_master_strategy
from dotenv import load_dotenv

from api.utils.celery_tasks.task_schedular import push_task_in_queue
from api.utils.celery_tasks.test import test_celery, run_first_time_strategy
from config.database.mongo import MongoManager
from main import celery

router = APIRouter(
    prefix="/api/v1",
    tags=["Strategy"],
    responses={404: {"description": "Not found"}},
)


@router.get("/task", response_description="")
async def testing():
    # tomorrow = datetime.utcnow() + timedelta(days=1)
    one_m = datetime.utcnow() + timedelta(minutes=.1)

    result = test_celery.apply_async(queue='master-strategy', priority=9, args=[1, 2], eta=one_m)
    print(result.id, "+++++++++++")
    #result = celery.control.revoke(result.id)
    #print(result)


    # one_m = datetime.utcnow() + timedelta(minutes=.1)
    # run_first_time_strategy.apply_async(queue='custom-strategy', priority=9, args=[], eta=one_m)

    # run_first_time_strategy.apply_async(
    #     queue='master-strategy',
    #     priority=9,
    #     args=[],
    #     eta=one_m
    # )
    return True


@router.get("/test", response_description="")
async def test(symbols: str):
    # API call
    # await test_async()
    # ADAUSDT,SOLUSDT,XRPUSDT,DOTUSDT,LTCUSDT,UNIUSDT,LINKUSDT,BCHUSDT,MATICUSDT,XLMUSDT,VETUSDT,ETCUSDT,XMRUSDT,EOSUSDT,QTUMUSDT,ICXUSDT,NULSUSDT,SUSHIUSDT,AAVEUSDT,OXTUSDT,BTCUSDT,GRTUSDT,BATUSDT,ZECUSDT,THETAUSDT,DASHUSDT,IOTAUSDT,SNXUSDT,RENUSDT,INJUSDT,COTIUSDT,1INCHUSDT,KNCUSDT,UMAUSDT,STXUSDT,BNTUSDT,CAKEUSDT,NMRUSDT,CRVUSDT,CELOUSDT,COMPUSDT,MKRUSDT,DCRUSDT,ATOMUSDT,BANDUSDT,EGLDUSDT,KAVAUSDT,NEARUSDT,ROSEUSDT
    # symbols_list = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "LTCUSDT", "ADAUSDT",
    #           "LINKUSDT", "MATICUSDT", "UNIUSDT", "XRPUSDT", "BNBUSDT"]

    symbols_list = symbols.split(",")

    #await push_task_in_queue()
    await first_time_run_strategy(symbols_list, '1d', 'binance')
    #await run_master_strategy(symbols_list, '1d', 'binance')
    #await run_user_strategy(symbols_list, '1d', 'binance')

    # return JSONResponse(status_code=200, content={"message": "401"})
