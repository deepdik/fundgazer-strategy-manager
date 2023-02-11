## <u>`Clean & fix code, fix circular imports, fix error handling`.</u>


</br>

## Refractor-Steps
* populate master strategy schema from MSC collection programatically.
* `run_first_time()` function , test and validate.
* `run_master_startegy()` function , test and validate.
* `run_user_startegy()` function , test and validate.

</br> 

## ToDo
* cron syntax is unable to accomodate stock market holidays.
    * create a collection object {"Trading Holidays": [<list of holidays to be updated manually]>]}
    * `last_executed`, `next_execution` (if now < next_execution < now + cron_sleep then add to queue).
    * after strategy execution `find_next_execution()` and update `last_executed`. 

    ```python
            """MASTER_STRATEGIES (it will inherit name, run_time, portfolio_id, timeframe from MASTER_STRATEGY_COLLECTION) need
        not reference MASTER_STRATEGY_COLLECTION (this is needed just to create the list of master strategies that
        are to be deployed to the system)"""

        "We should put MASTER_STRATEGY_COLLECTION in a new database INTERNAL_USE_ONLY"
        "Create a function create_master_strategies(msc_id, exchange_id,start_date, supported_exchange_id : list, symbol_list: list)"


        def get_msc_details():
            pass


        def get_trading_days():
            pass


        def create_master_strategies(
            msc_id, start_date, supported_exchange_id: list, symbol_list: list
        ) -> list:
            now = datetime.datetime.now()
            msc_data = get_msc_details(msc_id)
            n_days = msc_data["no_of_days"]
            master_strategies = [
                {
                    "version": i,
                    "supported_exchange": supported_exchange_id,
                    "symbol_list": symbol_list,
                }
                for i in range(n_days)
            ]
            if start_date:
                dates = get_trading_days(start=start_date, number_of_trading_days=n_days)
            else:
                dates = get_trading_days(start=now, number_of_trading_days=n_days)

            for idx, date in enumerate(dates):
                master_strategies[idx]["start_date"] = date

            return master_strategies
    ```