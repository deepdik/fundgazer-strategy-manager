import datetime
from api.utils.datetime_convertor import get_business_days

import asyncio
from config.database.mongo import MongoManager

from main import settings


async def get_master_startegy_collection(
    strategy_id: int,
    min_amount: float,
    suppported_exchange: str,
    symbol_list: str,
    run_time: str = "08:00",
):
    database = await MongoManager.get_instance_by_database(settings.STRATEGIES_DATABASE)
    task = await database["master-strategy-collection"].find_one({"msId": strategy_id})
    print(task)
    {
        "_id": "63e7f64c6862301cb452aba4",
        "msId": 1,
        "msName": "Strategy_relative_comparision_index4_holdings_Index4_Reversal_Breakout",
        "noOfDays": 7,
        "portfolioId": "port1",
        "runTime": "30 0 * * *",
        "timeFrame": "D",
    }
    today = datetime.datetime.now()
    business_days = iter(get_business_days(start=today))

    # Then insert 7 iterations
    for version in range(task["noOfDays"]):
        date = next(business_days)
        print(version, date)
        doc = {
            "minimumAmount": min_amount,
            "msId": strategy_id,
            "version": version,
            "msName": task["msName"],
            "noOfDays": task["noOfDays"],
            "active_days": 0,
            "portfolioId": task["portfolioId"],
            "runTime": run_time,
            "startDate": str(date),
            "last_run": None,
            "next_run": None,
            "status": "active",
            "supportedExchangeId": suppported_exchange,
            "symbolList": symbol_list,
            "timeFrame": task["timeFrame"],
            "isFirstTime": True,
        }
        await database["masterstrategies"].insert_one(doc)


params = {
    "strategy_id": 2,
    "min_amount": 100000,
    "run_time": "08:00",
    "suppported_exchange": "exch123",
    "symbol_list": "NSE:AXISBANK-EQ,NSE:BPCL-EQ,NSE:TATAMOTORS-EQ,NSE:KOTAKBANK-EQ,NSE:RELIANCE-EQ,NSE:ICICIBANK-EQ,NSE:TATASTEEL-EQ,NSE:HDFCBANK-EQ,NSE:SBIN-EQ,NSE:BHARTIARTL-EQ,NSE:INDUSINDBK-EQ,NSE:BAJFINANCE-EQ,NSE:INFY-EQ,NSE:HDFC-EQ,NSE:GRASIM-EQ,NSE:UPL-EQ,NSE:ADANIPORTS-EQ,NSE:TCS-EQ,NSE:LT-EQ,NSE:HCLTECH-EQ,NSE:WIPRO-EQ,NSE:MARUTI-EQ,NSE:ITC-EQ,NSE:HINDALCO-EQ,NSE:ASIANPAINT-EQ,NSE:HINDUNILVR-EQ,NSE:ONGC-EQ,NSE:BAJAJFINSV-EQ,NSE:GAIL-EQ,NSE:M&M-EQ,NSE:IOC-EQ,NSE:TECHM-EQ,NSE:SUNPHARMA-EQ,NSE:DRREDDY-EQ,NSE:NTPC-EQ,NSE:CIPLA-EQ,NSE:COALINDIA-EQ,NSE:JSWSTEEL-EQ,NSE:BRITANNIA-EQ,NSE:BAJAJ-AUTO-EQ,NSE:HEROMOTOCO-EQ,NSE:EICHERMOT-EQ,NSE:DIVISLAB-EQ,NSE:POWERGRID-EQ,NSE:TITAN-EQ,NSE:GOLDBEES-EQ,NSE:HDFCMFGETF-EQ,NSE:SBILIFE-EQ,NSE:HDFCLIFE-EQ",
}

asyncio.run(get_master_startegy_collection(**params))


def get_msc_details():
    pass


def get_trading_days():
    pass


# def create_master_strategies(
#     msc_id, start_date, supported_exchange_id: list, symbol_list: list
# ) -> list:
#     now = datetime.datetime.now()
#     msc_data = get_msc_details(msc_id)
#     n_days = msc_data["no_of_days"]
#     master_strategies = [
#         {
#             "version": i,
#             "supported_exchange": supported_exchange_id,
#             "symbol_list": symbol_list,
#         }
#         for i in range(n_days)
#     ]
#     if start_date:
#         dates = get_trading_days(start=start_date, number_of_trading_days=n_days)
#     else:
#         dates = get_trading_days(start=now, number_of_trading_days=n_days)

#     for idx, date in enumerate(dates):
#         master_strategies[idx]["start_date"] = date

#     return master_strategies


# start = datetime.datetime.now()
# end = start + datetime.timedelta(days=30)

# print("Next trading day: ", get_business_days(start=start, end=end)[1])
# print("Total: ", get_business_days(start=start, end=end))
