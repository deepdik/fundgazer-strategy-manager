from datetime import datetime, timedelta

from fastapi import APIRouter

from api.service.service import run_user_strategy, first_time_run_strategy, test_async, run_master_strategy
from dotenv import load_dotenv

from api.utils.celery_tasks.test import test_celery, run_first_time_strategy
from config.database.mongo import MongoManager

router = APIRouter(
    prefix="/api/v1",
    tags=["strategy"],
    responses={404: {"description": "Not found"}},
)

load_dotenv('config/environ/.env')


@router.get("/task", response_description="")
async def save_symbol_price_ticker():
    tomorrow = datetime.utcnow() + timedelta(days=1)
    #test_celery.apply_async(queue='master-strategy', priority=9, args=[1, 2], eta=tomorrow)
    #
    one_m = datetime.utcnow() + timedelta(minutes=.1)
    run_first_time_strategy.apply_async(queue='custom-strategy', priority=9, args=[], eta=one_m)

    # run_first_time_strategy.apply_async(
    #     queue='master-strategy',
    #     priority=9,
    #     args=[],
    #     eta=one_m
    # )
    return True


@router.get("/test", response_description="")
async def test(symbols:str):
    # API call
    print("------")

    # await test_async()
    # ADAUSDT,SOLUSDT,XRPUSDT,DOTUSDT,LTCUSDT,UNIUSDT,LINKUSDT,BCHUSDT,MATICUSDT,XLMUSDT,VETUSDT,ETCUSDT,XMRUSDT,EOSUSDT,QTUMUSDT,ICXUSDT,NULSUSDT,SUSHIUSDT,AAVEUSDT,OXTUSDT,BTCUSDT,GRTUSDT,BATUSDT,ZECUSDT,THETAUSDT,DASHUSDT,IOTAUSDT,SNXUSDT,RENUSDT,INJUSDT,COTIUSDT,1INCHUSDT,KNCUSDT,UMAUSDT,STXUSDT,BNTUSDT,CAKEUSDT,NMRUSDT,CRVUSDT,CELOUSDT,COMPUSDT,MKRUSDT,DCRUSDT,ATOMUSDT,BANDUSDT,EGLDUSDT,KAVAUSDT,NEARUSDT,ROSEUSDT
    # symbols_list = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "LTCUSDT", "ADAUSDT",
    #           "LINKUSDT", "MATICUSDT", "UNIUSDT", "XRPUSDT", "BNBUSDT"]

    symbols_list = symbols.split(",")
    # Q-12:01
    await first_time_run_strategy(symbols_list, '1d', 'binance')
    # 12:02 -> per days 7 days, last
    await run_master_strategy(symbols_list, '1d', 'binance')
    # 12:05 -> 7 days
    await run_user_strategy(symbols_list, '1d', 'binance')

    # await first_time_run_strategy(
    #     ["BTCUSDT", "ETHUSDT", "SOLUSDT", "LTCUSDT", "ADAUSDT",
    #      "LINKUSDT", "MATICUSDT", "UNIUSDT", "XRPUSDT", "BNBUSDT"], '1d', 'binance'
    #
    # )

    # return JSONResponse(status_code=200, content={"message": "401"})

