import datetime
from api.utils.datetime_convertor import get_business_days

# import asyncio
# from config.database.mongo import MongoManager

# from main import settings


# asyncio.run(get_holdidays())


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


start = datetime.datetime.now()
end = start + datetime.timedelta(days=30)

print("Next trading day: ", get_business_days(start=start, end=end)[1])
# print("Total: ", get_business_days(start=start, end=end))
