from api.exception.api_call_wrapper import async_api_caller
from api.models.general_models import APIMethodEnum
from main import settings


async def kline_data_client(symbols, interval):
    print(symbols, interval, settings.DATA_HANDLER_BASE+settings.DATA_HANDLER_KLINE)
    url = settings.DATA_HANDLER_BASE+settings.DATA_HANDLER_KLINE
    params = {"symbols": ",".join(symbols), "interval": interval}
    return await async_api_caller(url, APIMethodEnum.GET, params)


async def fyers_kline_data_client(symbols, interval):
    print(symbols, interval, settings.DATA_HANDLER_BASE+settings.FLYPER_CANDLE)
    url = settings.DATA_HANDLER_BASE+settings.FLYPER_CANDLE
    params = {"symbols": ",".join(symbols), "interval": interval}
    return await async_api_caller(url, APIMethodEnum.GET, params)