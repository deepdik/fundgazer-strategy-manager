import multiprocessing
import pandas as pd
import concurrent.futures

from api.models.general_models import Exchange
from api.utils.api_client.internal.data_handler import fyers_kline_data_client, kline_data_client

PICKLE_DATA_FOLDER = "PickledData"

resample_conversion = {
    "Open": "first",
    "High": "max",
    "Low": "min",
    "Close": "last",
    "Volume": "sum",
}


class Live_DataHandler:
    def __init__(self, symbol_list, timeframe, exchange):
        self.ohlcv_db_func = None
        self.symbol_list = list(set(symbol_list))
        self.symbol_data = {}
        self.symbol_dataframe = {}
        self.timeframe = timeframe
        self.latest_symbol_data = {}
        self.continue_backtest = True
        self.bar_index = -1
        self.exchange = exchange

        self.column_rename = {
            "open_time": "Date",
            "open_price": "Open",
            "high_price": "High",
            "low_price": "Low",
            "close_price": "Close",
            "volume": "Volume",
        }
        self.start_previous_candle_index = None

    async def init_data(self, latest_candle_index=None):
        resp, status = None, False
        if self.exchange.lower() == Exchange.BINANCE:
            print(f"Start getting data for {self.symbol_list} timeframe => {self.timeframe} exchange => {self.exchange}")
            resp, status = await kline_data_client(self.symbol_list, self.timeframe)
        elif self.exchange.lower() == Exchange.ZERODHA:
            resp, status = await kline_data_client(self.symbol_list, self.timeframe)
        elif self.exchange.lower() == Exchange.FYERS:
            resp, status = await fyers_kline_data_client(self.symbol_list, self.timeframe)
        else:
            raise ValueError("Invalid Exchange")

        if status:
            self.ohlcv_db_func = resp
            print(f"Successfully got data from data-handler =>>>>>status-{status}")
        else:
            raise ValueError("No kline data found")

        self._get_candle_from_db(latest_candle_index)

    def preset_data(self, preset_count=20):
        for symbol in self.symbol_list:
            self.latest_symbol_data[symbol] = (
                self.symbol_dataframe[symbol].iloc[:-preset_count].copy(deep=True)
            )

    def undo_preset(self):
        for symbol in self.symbol_list:
            self.latest_symbol_data[symbol] = self.symbol_dataframe[symbol]

    def _get_candle_from_db(self, candle_count=500):
        self.candle_count = candle_count
        
        with concurrent.futures.ThreadPoolExecutor(
                max_workers=multiprocessing.cpu_count() * 5
        ) as executor:
            futures = []
            for s in self.symbol_list:
                futures.append(executor.submit(self._get_symbol_data, s))
            for future in concurrent.futures.as_completed(futures):
                result: dict = future.result()
                s = list(result.keys())[0]
                df = list(result.values())[0]
                if df is None:
                    print("WARNING: DATA NOT FOUND, SYMBOL WILL BE IGNORED:", s)
                    continue

                if isinstance(df,pd.DataFrame) and df.empty:
                    print("WARNING: DATA NOT FOUND, SYMBOL WILL BE IGNORED:", s)
                    continue

                self.latest_symbol_data[s] = pd.DataFrame(
                    columns=["Date", "Open", "High", "Low", "Close", "Volume"]
                ).set_index("Date")

                self.latest_symbol_data[s] = self.latest_symbol_data[s].append(df)
                self.symbol_dataframe[s] = self.latest_symbol_data[s]

        self.symbol_list = list(self.latest_symbol_data.keys())

        # check if latest candle for all symbols have the same timestamp
        t_list = []
        s_list = []
        for symbol in self.symbol_list:
            latest_timestamp = self.latest_symbol_data[symbol].index[-1]
            t_list.append(latest_timestamp)
            s_list.append(symbol)
        if len(list(set(t_list))) > 1:
            error_list = dict(zip(s_list, t_list))
            raise Exception(
                "Latest candlestick for all symbols does not match for timestamp "
                + str(error_list)
            )
        # check over

        self.symbol_list.sort()

    def _get_symbol_data(self, s):

        db_data = None
        for k_data in self.ohlcv_db_func:
            if k_data["symbol"] == s:
                db_data = k_data
                break

        if not db_data:
            print(f"No data found for {s}")  # we can raise an error here
            return {s: []}

        if self.start_previous_candle_index:
            # spliting the data so that last candle is based on latest_candle_index
            db_data = db_data[: self.start_previous_candle_index]

        df = pd.DataFrame.from_records(
            db_data["kline_data"],
            columns=["open_time", "open_price", "high_price", "low_price", "close_price", "volume"],
            index="open_time",
        )
        df.rename(columns=self.column_rename, inplace=True)
        # df.index = pd.to_datetime(df.index / 1000, unit="s")

        # df = df.resample(self.timeframe).apply(resample_conversion).dropna()
        return {s: df}

    def get_latest_bar(self, symbol):
        """
        Returns the last bar from the latest_symbol list.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
            return bars_list.iloc[-1]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise

    def get_latest_bars(self, symbol, N=1):
        """
        Returns the last N bars from the latest_symbol list,
        or N-k if less available.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
            return bars_list.iloc[-N:]

        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise

    def get_latest_bar_index(self, symbol):
        """Get integer index for last bar wrt bars in latest_symbol_data"""
        try:
            bars_list = self.latest_symbol_data[symbol].reset_index().iloc[-1].name
        except KeyError:
            print("This symbol is not available")
            raise
        except IndexError:
            print("No latest data available")
            return None
        else:
            return bars_list

    def get_latest_bar_datetime(self, symbol):
        """
        Returns a Python datetime object for the last bar.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return bars_list.iloc[-1].name

    def get_latest_bar_value(self, symbol, val_type):
        """
        Returns one of the Open, High, Low, Close, Volume or OI
        values from the pandas Bar series object.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return getattr(bars_list.iloc[-1], val_type)

    def get_latest_bars_values(self, symbol, val_type, N=1):
        """
        Returns the last N bar values from the
        latest_symbol list, or N-k if less available.
        """
        try:
            bars_list = self.get_latest_bars(symbol, N)
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return getattr(bars_list.iloc[-N:], val_type)

    def update_bars(self):
        raise NotImplementedError("Cant be called for live data")
