import json

from api.models.strategy_model import MasterPresetDataModel, FilteredStocksModel, UserPresetDataModel, PresetDataVersion
from api.repository.strategy_repo import save_user_preset_data, save_master_preset_data, save_filtered_stocks, \
    get_master_preset_data, get_user_preset_data, get_filtered_stocks
from api.utils.datetime_convertor import get_current_local_time
from api.utils.strategy_logics.data_handler.data import Live_DataHandler
from api.utils.strategy_logics.port.mpt_index import Index3
from api.utils.strategy_logics.strategy.mpt_strategies import Strategy_direct_comparision_index3
from api.utils.utils import create_symbol_hash, NumpyEncoder
from config.database.mongo import MongoManager
from utils.logger import logger_config

logger = logger_config(__name__)


async def first_time_run_strategy(symbols: list, timeframe: str,
                                  exchange: str, ms_id="0", preset_count=20, index_cls=Index3):
    """
    """
    try:
        data = Live_DataHandler(symbols, timeframe, exchange)
        await data.init_data()
        data.preset_data(preset_count=preset_count)
        strategy = Strategy_direct_comparision_index3(data, index_cls)
        strategy.master_find_entry()
        # run the strategy on preset data
        for i in range(preset_count, 1, -1):
            data.preset_data(preset_count=i)
            strategy.master_find_entry()

        # Store master-id day -1
        preset_strategy_data = strategy.get_data_to_save()
        #print(preset_strategy_data)
        validated_data = MasterPresetDataModel(
            date=get_current_local_time(),
            version=PresetDataVersion.VERSION_0,
            ms_id=ms_id,
            preset_data=json.dumps(preset_strategy_data, cls=NumpyEncoder)
        )

        await save_master_preset_data(validated_data)
        return True
        #return preset_strategy_data
    except Exception as e:
        logger.error(e)
        return False


async def run_master_strategy(symbols: list, timeframe: str, exchange: str, ms_id="0",
                              preset_count=20, index_cls=Index3):
    data = Live_DataHandler(symbols, timeframe, exchange)
    await data.init_data()
    data.preset_data(preset_count=preset_count)

    # get preset data and run the strategy on preset data
    local_date = get_current_local_time()
    version = PresetDataVersion(local_date.weekday())
    preset_data = await get_master_preset_data(ms_id, version)
    if preset_data:
        preset_data = json.loads(preset_data["preset_data"])
    else:
        raise ValueError("No preset data found...")

    #preset_data = await first_time_run_strategy(symbols, timeframe, exchange)
    strategy = Strategy_direct_comparision_index3(data, index_cls, db_saved_data=preset_data)
    filter_stocks = strategy.master_find_entry()
    preset_strategy_data = strategy.get_data_to_save()
    logger.debug(f"-----filter stock {filter_stocks}")
    stocks_obj = FilteredStocksModel(
        date=local_date,
        version=version,
        ms_id=ms_id,
        filtered_stocks=filter_stocks
    )
    # save filtered stocks
    await save_filtered_stocks(stocks_obj)
    # save preset strategy data
    validated_data = MasterPresetDataModel(
        date=local_date,
        version=version,
        ms_id=ms_id,
        preset_data=json.dumps(preset_strategy_data, cls=NumpyEncoder)
    )
    await save_master_preset_data(validated_data)
    #return preset_strategy_data, filter_stocks


async def run_user_strategy(symbols: list, timeframe: str,
                            exchange: str,  user_id: str, ms_id: str='0', index_cls=Index3,
                            capital=10000):

    logger.info(f"Started user strategies with {symbols} {timeframe}")
    local_date = get_current_local_time()
    version = PresetDataVersion(local_date.weekday())
    # first day will pick the latest master preset_strategy_data
    preset_strategy_data = await get_user_preset_data(
        ms_id, user_id, version
    )
    if preset_strategy_data:
        preset_strategy_data = json.loads(preset_strategy_data["preset_data"])
    else:
        logger.error("No filtered stock...")
        raise ValueError("No preset data found...")

    #preset_strategy_data, filter_stocks = await run_master_strategy(symbols, timeframe, exchange)
    filter_stocks = []
    filter_stocks_obj = await get_filtered_stocks(ms_id, version)
    if filter_stocks_obj:
        filter_stocks = filter_stocks_obj.get("filtered_stocks", [])

    if not filter_stocks:
        logger.error("No filtered stock...")
        #raise ValueError("No filtered stock...")
        filter_stocks = ["ICXUSDT"]

    data = Live_DataHandler(symbols, timeframe, exchange)
    await data.init_data()
    strategy = Strategy_direct_comparision_index3(
        data=data,
        index_cls=index_cls,
        db_saved_data=preset_strategy_data,
    )
    stocks_weightage = strategy.user_find_entry(capital, filter_stocks)
    preset_data = strategy.get_data_to_save()

    validated_data = UserPresetDataModel(
        user_id=user_id,
        ms_id=ms_id,
        date=get_current_local_time(),
        version=version,
        preset_data=json.dumps(preset_data, cls=NumpyEncoder)
    )
    # save preset data
    await save_user_preset_data(validated_data)
    # TODO: send stock weightage
    logger.info(f"Stock weightage ----->{stocks_weightage}")
