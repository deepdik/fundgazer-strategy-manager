# import importlib

# strategy = "mpt_strategies"

# module = importlib.import_module(f"api.utils.strategy_logics.strategy.{strategy}")

# print(module.MIN_ORDER_SIZE_CRYPTO)


# import asyncio

# from api.repository.task_schedular import get_task_list


# tasks = asyncio.run(get_task_list())
# print(tasks)

MONGO_SCHEMA = {
    "MASTER_STRATEGY_COLLECTION": [
        {
            "_id": {"$oid": "63e7f64c6862301cb452aba4"},
            "mscId": "1",
            "msName": "Strategy_relative_comparision_index4_holdings_Index4_Reversal_Breakout",
            "noOfDays": "7",
            "portfolioId": "portId1",
            "runTime": "30 0 * * *",
            "timeFrame": "D",
        },
    ],
    "MASTER_STRATEGIES": [
        {
            "_id": "6378997a66903230ec5f8363",
            "minimumAmount": {"$numberLong": "10"},
            "msId": "msId123",
            "msName": "msName",
            "noOfDays": "23",
            "portfolioId": "portId123",
            "runTime": "30 0 * * *",
            "startDate": "12-09-2022",
            "status": "active",
            "supportedExchangeId": "exch123",
            "symbolList": "ICXUSDT,XMRUSDT,EOSUSDT,QTUMUSDT,ETCUSDT,VETUSDT,XLMUSDT,ETHUSDT,ADAUSDT,SOLUSDT,XRPUSDT,DOTUSDT,LTCUSDT,UNIUSDT,LINKUSDT,BCHUSDT,MATICUSDT,BTCUSDT,SNXUSDT,AAVEUSDT,RENUSDT,COMPUSDT,IOTAUSDT,KAVAUSDT,ATOMUSDT,MKRUSDT",
            "timeFrame": "1d",
            "isFirstTime": False,
        }
    ],
    "STRATEGIES": [
        {
            "_id": {"$oid": "63c267b0c2d07371729291d6"},
            "amountAdded": {"$numberLong": "303175"},
            "exchangeName": "fyers",
            "expiryDate": "13-10-2022",
            "fmId": "fmid130",
            "msId": "msId124",
            "orderId": "order123",
            "portfolioId": "port123",
            "startDate": "12-10-2022",
            "status": "active",
            "strategyId": "edcrfvb4321",
            "userId": "user123",
            "watchList": "false",
            "runTime": "0 1 * * *",
            "fmWatchListId": "",
        }
    ],
}
