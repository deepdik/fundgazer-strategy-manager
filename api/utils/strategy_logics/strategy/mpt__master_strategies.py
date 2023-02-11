import pandas as pd
import operator

from api.utils.strategy_logics.port.mpt_helper import (
    calculate_portfolio_value,
    calculate_returns,
    redistribute_tangency_portfolio,
)
from api.utils.strategy_logics.port.mpt_index import Index4
from api.utils.strategy_logics.port.filtering_condition import filtering_by_conditions
from api.models.strategy_model import CONDITION_TYPE,FILTERING_TYPE,MPT_STRATEGIES_VARIABLES
from api.utils.strategy_logics.packages.indicators.trend_indicators import ema

MIN_ORDER_SIZE_CRYPTO = 20  # Min order size for exchange in dollars


class Strategy_direct_comparision_index3:

    def __init__(
            self,
            data,
            index_cls,
            filtering_type="Breakout",
            condition_type="Breakout",
            db_saved_data=None
    ):
        self.data = data
        self.index_sharpe = None
        self.portfolio_sharpe = []
        self.index = index_cls

        if db_saved_data:
            self._use_db_saved_data(db_saved_data)
        else:
            self.index = index_cls(data.symbol_list, data)
            self.index_sortino = None
            self.yesterday_stocks_list = []
            self.filtered_stocks = None
            self.portfolio_weights = []
            self.portfolio_value = None
            self.portfolio_daily_returns = []
            self.portfolio_sortino = []
            self.counter = 0

        if filtering_type == "Breakout":
            self.filtering_function = operator.ge
        else:
            self.filtering_function = operator.le

        self.condition_type = condition_type

    def find_symbol_sharpe(self, number_of_candles=50):
        "To be used by filter_stocks_by_index"
        sharpe_symbol_mean = {}
        for symbol in self.data.symbol_list:
            daily_return = (
                self.data.latest_symbol_data[symbol].Close.iloc[-2:].pct_change()[-1]
            )
            sigma = self.data.latest_symbol_data[symbol].iloc[-number_of_candles:].Close.pct_change().std()
            sharpe = (daily_return - 0.00023) / sigma
            sharpe_symbol_mean[symbol] = dict(
                daily_return=daily_return, sigma=sigma, sharpe=sharpe
            )
        return sharpe_symbol_mean

    def filter_stocks_by_index(self):
        "filter stocks every 3rd day"
        # print("self.index_sharpe: ",self.index_sharpe)
        if self.index_sharpe != 0:
            self.filtered_stocks = {}
            if self.index_sharpe:
                self.symbol_sharpe = self.find_symbol_sharpe()
                # print("self.symbol_sharpe: ",self.symbol_sharpe)
                for symbol in self.data.symbol_list:
                    symbol_sharpe_value = self.symbol_sharpe[symbol]["sharpe"]
                    if self.filtering_function(symbol_sharpe_value, self.index_sharpe):
                        self.filtered_stocks[symbol] = self.symbol_sharpe[symbol]
                return self.filtered_stocks
        return {}

    def redistribute_filtered_stocks(self, filtered_stocks):
        "make portfolio on filtered stocks every 3rd day"
        stocks = list(filtered_stocks)
        _, expected_returns, covariance_matrix = calculate_returns(stocks, self.data)
        tangency_sol = redistribute_tangency_portfolio(
            stocks, covariance_matrix, expected_returns
        )
        self.portfolio_weights = tangency_sol.x
        self.portfolio_value = calculate_portfolio_value(
            self.portfolio_weights, stocks, self.data
        )
        self.yesterday_stocks_list = list(filtered_stocks)

    def calculate_daily_return(self):
        "calculate change in portfolio value every day, to calculate sharpe"
        new_portfolio_value = calculate_portfolio_value(
            self.portfolio_weights, self.yesterday_stocks_list, self.data
        )
        daily_return = (new_portfolio_value / self.portfolio_value) - 1
        sigma = pd.Series(self.portfolio_daily_returns).std()
        sharpe = (daily_return - 0.00023) / sigma
        self.portfolio_sharpe.append(sharpe)
        self.portfolio_daily_returns.append(daily_return)
        self.portfolio_value = new_portfolio_value

    def master_find_entry(self):
        sharpe_index = self.index.calculate_sharpe()
        # print("SHARPE INDEX: ",sharpe_index)
        self.index_sharpe = sharpe_index[-1]
        if len(self.portfolio_weights) > 0:
            self.calculate_daily_return()
        filtered_stocks = self.filter_stocks_by_index()
        # print("FILTERED STOCKS-1: ",filtered_stocks)

        filtered_stocks_2 = []
        if len(filtered_stocks) > 0:
            filtered_stocks_2 = filtering_by_conditions(
                filtered_stocks, self.data, self.condition_type
            )
            self.redistribute_filtered_stocks(filtered_stocks_2)

        return filtered_stocks_2

    def user_find_entry(self, capital, filtered_stocks_2):  # 1000, 7
        """
        """
        # filtered_stocks_2 - > ms - sym list,  strg data,  days, capital
        self.redistribute_filtered_stocks(filtered_stocks_2)

        # Filtering to remove lower weighted stocks
        while True:

            if len(filtered_stocks_2) == 1:
                break
            quantity_amount = capital * self.portfolio_weights

            # drop symbols having amount lesser than 10 dollars.
            symbols_to_drop = [
                symbol
                for idx, symbol in enumerate(filtered_stocks_2)
                if quantity_amount[idx] < MIN_ORDER_SIZE_CRYPTO
            ]
            filtered_stocks_2 = [
                symbol
                for symbol in filtered_stocks_2
                if symbol not in symbols_to_drop
            ]
            if len(filtered_stocks_2) == 0:
                break
            self.redistribute_filtered_stocks(filtered_stocks_2)

            if len(symbols_to_drop) == 0 or len(filtered_stocks_2) == 0:
                break
        #
        # if len(filtered_stocks_2) > 0:
        #     signal = SignalEvent(
        #         symbols=filtered_stocks_2,
        #         datetime=self.data.get_latest_bar_datetime(
        #             filtered_stocks_2[0]
        #         ),
        #         weightage=self.portfolio_weights,
        #     )
        #
        #     # self.events.put(signal)
        #     print(signal)

        return dict(zip(filtered_stocks_2, self.portfolio_weights))

    def get_data_to_save(self):

        data = {
            #"daily_sharpe": self.daily_sharpe,
            "yesterday_stocks_list": self.yesterday_stocks_list,
            "portfolio_weights": self.portfolio_weights,
            "portfolio_daily_returns": self.portfolio_daily_returns,
            "portfolio_value": self.portfolio_value,
            "portfolio_sharpe": self.portfolio_sharpe,
            "counter": self.counter,
            "index_data": self.index.get_data_to_save(),
        }
        return data

    def _use_db_saved_data(self, db_saved_data):
        if not db_saved_data:
            return

        #self.daily_sharpe = db_saved_data["daily_sharpe"]
        self.yesterday_stocks_list = db_saved_data["yesterday_stocks_list"]
        self.portfolio_weights = db_saved_data["portfolio_weights"]
        self.portfolio_daily_returns = db_saved_data["portfolio_daily_returns"]
        self.portfolio_value = db_saved_data["portfolio_value"]
        self.portfolio_sharpe = db_saved_data["portfolio_sharpe"]
        self.counter = db_saved_data["counter"]

        self.index = self.index(
            self.data.symbol_list, self.data, db_saved_data=db_saved_data["index_data"]
        )

class Strategy_relative_comparision_index4_holdings_Index4_Reversal_Breakout:
    def __init__(
        self,
        data
    ):
        self.data = data
        self.index = Index4(symbol_list=data.symbol_list, data=data)
        self.daily_sortino = {symbol: [] for symbol in data.symbol_list}
        self.yesterday_stocks_list = []
        self.portfolio_weights = []
        self.portfolio_daily_returns = []
        self.portfolio_value = None
        self.portfolio_sortino = []
        self.counter = 0

    def find_symbol_sortino(self):
        "To be used by filter_stocks_by_index"
        sortino_symbol_mean = {}
        for symbol in self.data.symbol_list:
            daily_return = (
                self.data.latest_symbol_data[symbol].Close.iloc[-2:].pct_change()[-1]
            )
            sigma = (
                self.data.latest_symbol_data[symbol]
                .iloc[-MPT_STRATEGIES_VARIABLES.number_of_candles:]
                .Close.pct_change()
                .where(lambda x: x < 0)
                .dropna()
                .std()
            )
            sortino = (daily_return - 0.00023) / sigma
            sortino_symbol_mean[symbol] = dict(
                daily_return=daily_return, sigma=sigma, sortino=sortino
            )
        return sortino_symbol_mean

    def find_daily_sortino(self, data):
        symbol_sortino = self.find_symbol_sortino()
        [
            self.daily_sortino[symbol].append(symbol_sortino[symbol]["sortino"])
            for symbol in data.symbol_list
        ]

    def filter_stocks_by_index(self):
        filtered_list = []
        if len(self.index.sortino) > 2:
            for symbol in self.data.symbol_list:
                relative_strength = pd.Series(self.daily_sortino[symbol]) / pd.Series(
                    self.index.sortino
                )
                ema_strength = ema(relative_strength, 20)
                if (relative_strength.iloc[-1] > ema_strength.iloc[-1]
                ) and (relative_strength.iloc[-1] > relative_strength.iloc[-2]):
                    filtered_list.append(symbol)
        return filtered_list

    def redistribute_filtered_stocks(self, filtered_stocks):
        "make portfolio on filtered stocks every 3rd day"
        stocks = list(filtered_stocks)
        _, expected_returns, covariance_matrix = calculate_returns(stocks, self.data)
        tangency_sol = redistribute_tangency_portfolio(
            stocks, covariance_matrix, expected_returns
        )
        self.portfolio_weights = tangency_sol.x
        self.portfolio_value = calculate_portfolio_value(
            self.portfolio_weights, stocks, self.data
        )
        self.yesterday_stocks_list = list(filtered_stocks)

    def calculate_daily_return(self):
        "calculate change in portfolio value every day, to calculate sortino"
        new_portfolio_value = calculate_portfolio_value(
            self.portfolio_weights, self.yesterday_stocks_list, self.data
        )
        daily_return = (new_portfolio_value / self.portfolio_value) - 1
        sigma = pd.Series(self.portfolio_daily_returns).std()
        sortino = (daily_return - 0.00023) / sigma
        self.portfolio_sortino.append(sortino)
        self.portfolio_daily_returns.append(daily_return)
        self.portfolio_value = new_portfolio_value

    def find_entry(self, capital, n_days):
        send_empty_signal = False
        self.find_daily_sortino(self.data)
        sortino_index = self.index.calculate_sortino()
        self.index_sortino = sortino_index[-1]
        if len(self.portfolio_weights) > 0:
            self.calculate_daily_return()
        if self.counter % n_days == 0:
            filtered_stocks = self.filter_stocks_by_index()
            if len(filtered_stocks) > 0:
                filtered_stocks_2 = filtering_by_conditions(
                    filtered_stocks, self.data, CONDITION_TYPE.breakout
                )
                if len(filtered_stocks_2) > 0:
                    self.redistribute_filtered_stocks(filtered_stocks_2)
                    prices = [
                        self.data.get_latest_bar_value(symbol, "Close")
                        for symbol in filtered_stocks_2
                    ]
                    # Filtering to remove lower weighted stocks
                    while True:
                        if len(filtered_stocks_2) == 1:
                            break
                        quantity_amount = capital * self.portfolio_weights

                        symbols_to_drop = [
                            symbol
                            for idx, symbol in enumerate(filtered_stocks_2)
                            if quantity_amount[idx] < prices[idx]
                        ]  # drop symbols having amount lesser than 10 dollars or stock price.
                        filtered_stocks_2 = [
                            symbol
                            for symbol in filtered_stocks_2
                            if symbol not in symbols_to_drop
                        ]
                        if len(filtered_stocks_2) == 0:
                            break
                        self.redistribute_filtered_stocks(filtered_stocks_2)
                        if len(symbols_to_drop) == 0 or len(filtered_stocks_2) == 0:
                            break
                    if len(filtered_stocks_2) > 0:
                        signal = SignalEvent(
                            symbols=filtered_stocks_2,
                            datetime=self.data.get_latest_bar_datetime(
                                filtered_stocks_2[0]
                            ),
                            weightage=self.portfolio_weights,
                        )
                        self.events.put(signal)
                    else:
                        send_empty_signal = True
                else:  # If no filtered stocks 2
                    send_empty_signal = True
            else:  # If no filtered stocks 1
                send_empty_signal = True
        if send_empty_signal:
            signal = SignalEvent(
                symbols=[],
                datetime=self.data.get_latest_bar_datetime(self.data.symbol_list[0]),
                weightage=[],
            )
            self.yesterday_stocks_list = []
            self.portfolio_weights = []
            self.portfolio_value = None
            self.portfolio_sortino.append(0)
            self.events.put(signal)
        self.counter = self.counter + 1

    def find_entry_crypto(self, capital, n_days):
        send_empty_signal = False
        self.find_daily_sortino(self.data)
        sortino_index = self.index.calculate_sortino()
        self.index_sortino = sortino_index[-1]
        if len(self.portfolio_weights) > 0:
            self.calculate_daily_return()
        if self.counter % n_days == 0:
            filtered_stocks = self.filter_stocks_by_index()
            if len(filtered_stocks) > 0:
                filtered_stocks_2 = filtering_by_conditions(
                    filtered_stocks, self.data, "Breakout"
                )
                if len(filtered_stocks_2) > 0:
                    self.redistribute_filtered_stocks(filtered_stocks_2)
                    # Filtering to remove lower weighted stocks
                    while True:
                        if len(filtered_stocks_2) == 1:
                            break
                        quantity_amount = capital * self.portfolio_weights

                        symbols_to_drop = [
                            symbol
                            for idx, symbol in enumerate(filtered_stocks_2)
                            if quantity_amount[idx] < MIN_ORDER_SIZE_CRYPTO
                        ]  # drop symbols having amount lesser than 10 dollars or stock price.
                        filtered_stocks_2 = [
                            symbol
                            for symbol in filtered_stocks_2
                            if symbol not in symbols_to_drop
                        ]
                        if len(filtered_stocks_2) == 0:
                            break
                        self.redistribute_filtered_stocks(filtered_stocks_2)
                        if len(symbols_to_drop) == 0 or len(filtered_stocks_2) == 0:
                            break
                    if len(filtered_stocks_2) > 0:
                        signal = SignalEvent(
                            symbols=filtered_stocks_2,
                            datetime=self.data.get_latest_bar_datetime(
                                filtered_stocks_2[0]
                            ),
                            weightage=self.portfolio_weights,
                        )
                        self.events.put(signal)
                    else:
                        send_empty_signal = True
                else:  # If no filtered stocks 2
                    send_empty_signal = True
            else:  # If no filtered stocks 1
                send_empty_signal = True
        if send_empty_signal:
            signal = SignalEvent(
                symbols=[],
                datetime=self.data.get_latest_bar_datetime(self.data.symbol_list[0]),
                weightage=[],
            )
            self.yesterday_stocks_list = []
            self.portfolio_weights = []
            self.portfolio_value = None
            self.portfolio_sortino.append(0)
            self.events.put(signal)
        self.counter = self.counter + 1