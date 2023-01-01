import pandas as pd
from api.utils.strategy_logics.port.mpt_helper import (
    calculate_portfolio_value,
    calculate_returns,
    calculate_returns_negetive_only,
    redistribute_tangency_portfolio,
    redistribute_tangency_portfolio2,
)


class Index3:
    """For Day1: historical expected rate of return is used for calculating sharpe,
    Day2: Onwards portfolio's daily change is used for calculating sharpe"
    """
    def __init__(self, symbol_list, data, db_saved_data=None):
        self.symbol_list = symbol_list
        self.data = data

        if db_saved_data:
            self._use_db_saved_data(db_saved_data)
        else:
            self.sharpe = []  # db
            self.portfolio_weight = []  # db
            self.portfolio_value = None  # db
            self.portfolio_daily_returns = []  # db

    def _use_db_saved_data(self, db_saved_data):
        if not db_saved_data:
            return
        self.sharpe = db_saved_data["sharpe"]
        self.portfolio_weight = db_saved_data["portfolio_weight"]
        self.portfolio_value = db_saved_data["portfolio_value"]
        self.portfolio_daily_returns = db_saved_data["portfolio_daily_returns"]

    def get_data_to_save(self):

        return {
            "sharpe": self.sharpe,
            "portfolio_weight": self.portfolio_weight,
            "portfolio_value": self.portfolio_value,
            "portfolio_daily_returns": self.portfolio_daily_returns,
        }

    def calculate_sharpe(self):
        if self.sharpe:
            new_portfolio_value = calculate_portfolio_value(
                self.portfolio_weight, self.symbol_list, self.data
            )
            daily_return = (new_portfolio_value / self.portfolio_value) - 1
            self.portfolio_daily_returns.append(daily_return)
            # Calculate Sharpe
            sigma = pd.Series(self.portfolio_daily_returns).std()
            sharpe = (daily_return - 0.00023) / sigma
            self.sharpe.append(sharpe)
            # Also Redistribute the Portfolio
            _, _, covariance_matrix = calculate_returns(self.symbol_list, self.data)
            tangency_sol = redistribute_tangency_portfolio2(
                self.symbol_list, covariance_matrix, daily_return
            )
            self.portfolio_weight = tangency_sol.x
            self.portfolio_value = calculate_portfolio_value(
                self.portfolio_weight, self.symbol_list, self.data
            )
        else:
            rate_of_returns, expected_returns, covariance_matrix = calculate_returns(
                self.symbol_list, self.data
            )
            tangency_sol = redistribute_tangency_portfolio(
                self.symbol_list, covariance_matrix, expected_returns
            )
            self.portfolio_value = calculate_portfolio_value(
                tangency_sol.x, self.symbol_list, self.data
            )
            self.portfolio_weight = tangency_sol.x
            self.sharpe.append(0)
        return self.sharpe


class Index3_v2:
    "Historical Sharpe is used for calculating the sharpe value"
    def __init__(self, symbol_list, data):
        self.symbol_list = symbol_list
        self.data = data
        self.sharpe = []
        self.x0 = None
        self.portfolio_weight = []
        self.portfolio_value = None
        self.portfolio_daily_returns = []

    def calculate_sharpe(self):
        if self.sharpe:
            new_portfolio_value = calculate_portfolio_value(
                self.portfolio_weight, self.symbol_list, self.data
            )
            daily_return = (new_portfolio_value / self.portfolio_value) - 1
            self.portfolio_daily_returns.append(daily_return)
            # Calculate Sharpe
            sigma = pd.Series(self.portfolio_daily_returns).std()
            sharpe = (daily_return - 0.00023) / sigma
            self.sharpe.append(sharpe)
            # Also Redistribute the Portfolio
            _, expected_returns, covariance_matrix = calculate_returns(
                self.symbol_list, self.data
            )
            tangency_sol = redistribute_tangency_portfolio(
                self.symbol_list, covariance_matrix, expected_returns
            )
            self.portfolio_weight = tangency_sol.x
            self.portfolio_value = calculate_portfolio_value(
                self.portfolio_weight, self.symbol_list, self.data
            )
        else:
            rate_of_returns, expected_returns, covariance_matrix = calculate_returns(
                self.symbol_list, self.data
            )
            tangency_sol = redistribute_tangency_portfolio(
                self.symbol_list, covariance_matrix, expected_returns
            )
            self.portfolio_value = calculate_portfolio_value(
                tangency_sol.x, self.symbol_list, self.data
            )
            self.portfolio_weight = tangency_sol.x
            self.sharpe.append(0)
        return self.sharpe


class Index4:
    def __init__(self, symbol_list, data, db_saved_data=None):
        self.symbol_list = symbol_list
        self.data = data

        if db_saved_data:
            self._use_db_saved_data(db_saved_data)
        else:
            self.sortino = []
            self.x0 = None
            self.portfolio_weight = []
            self.portfolio_value = None
            self.portfolio_daily_returns = []

    def _use_db_saved_data(self, db_saved_data):
        if not db_saved_data:
            return
        self.sortino = db_saved_data["sortino"]
        self.x0 = db_saved_data["x0"]
        self.portfolio_weight = db_saved_data["portfolio_weight"]
        self.portfolio_value = db_saved_data["portfolio_value"]
        self.portfolio_daily_returns = db_saved_data["portfolio_daily_returns"]

    def get_data_to_save(self):

        return {
            "sortino": self.sortino,
            "x0": self.x0,
            "portfolio_weight": self.portfolio_weight,
            "portfolio_value": self.portfolio_value,
            "portfolio_daily_returns": self.portfolio_daily_returns,
        }

    def calculate_sortino(self):
        if self.sortino:
            new_portfolio_value = calculate_portfolio_value(
                self.portfolio_weight, self.symbol_list, self.data
            )
            daily_return = (new_portfolio_value / self.portfolio_value) - 1
            self.portfolio_daily_returns.append(daily_return)
            # Calculate sortino
            sigma = (
                pd.Series(self.portfolio_daily_returns)
                .where(lambda x: x < 0)
                .dropna()
                .std()
            )
            sortino = (daily_return - 0.00023) / sigma
            self.sortino.append(sortino)
            # Also Redistribute the Portfolio
            _, _, covariance_matrix = calculate_returns_negetive_only(
                self.symbol_list, self.data
            )
            tangency_sol = redistribute_tangency_portfolio2(
                self.symbol_list, covariance_matrix, daily_return
            )
            self.portfolio_weight = tangency_sol.x
            self.portfolio_value = calculate_portfolio_value(
                self.portfolio_weight, self.symbol_list, self.data
            )
        else:
            (
                rate_of_returns,
                expected_returns,
                covariance_matrix,
            ) = calculate_returns_negetive_only(self.symbol_list, self.data)
            tangency_sol = redistribute_tangency_portfolio(
                self.symbol_list, covariance_matrix, expected_returns
            )
            self.portfolio_value = calculate_portfolio_value(
                tangency_sol.x, self.symbol_list, self.data
            )
            self.portfolio_weight = tangency_sol.x
            self.sortino.append(0)
        return self.sortino


class Index4_v2:
    def __init__(self, symbol_list, data):
        self.symbol_list = symbol_list
        self.data = data
        self.sortino = []
        self.x0 = None
        self.portfolio_weight = []
        self.portfolio_value = None
        self.portfolio_daily_returns = []

    def calculate_sortino(self):
        # Main Portfolio Redistribution
        if self.sortino:
            new_portfolio_value = calculate_portfolio_value(
                self.portfolio_weight, self.symbol_list, self.data
            )
            daily_return = (new_portfolio_value / self.portfolio_value) - 1
            self.portfolio_daily_returns.append(daily_return)
            # Calculate sortino
            sigma = (
                pd.Series(self.portfolio_daily_returns)
                .where(lambda x: x < 0)
                .dropna()
                .std()
            )
            sortino = (daily_return - 0.00023) / sigma
            self.sortino.append(sortino)
            # Also Redistribute the Portfolio
            _, expected_returns, covariance_matrix = calculate_returns_negetive_only(
                self.symbol_list, self.data
            )
            tangency_sol = redistribute_tangency_portfolio(
                self.symbol_list, covariance_matrix, expected_returns
            )
            self.portfolio_weight = tangency_sol.x
            self.portfolio_value = calculate_portfolio_value(
                self.portfolio_weight, self.symbol_list, self.data
            )
        # First Redistribution
        else:
            (
                rate_of_returns,
                expected_returns,
                covariance_matrix,
            ) = calculate_returns_negetive_only(self.symbol_list, self.data)
            tangency_sol = redistribute_tangency_portfolio(
                self.symbol_list, covariance_matrix, expected_returns
            )
            self.portfolio_value = calculate_portfolio_value(
                tangency_sol.x, self.symbol_list, self.data
            )
            self.portfolio_weight = tangency_sol.x
            self.sortino.append(0)
        return self.sortino


class Index3_pre_loaded:
    def __init__(self, symbol_list, data):
        self.symbol_list = symbol_list
        self.data = data
        self.sharpe_series = pd.read_csv(
            "PickledData/Index3_stocks.csv", index_col="Date", parse_dates=True
        )["Sharpe"]
        self.sharpe = []

    def calculate_sharpe(self):
        date = self.data.get_latest_bar_datetime(self.symbol_list[0])
        todays_sharpe = self.sharpe_series.loc[date]
        self.sharpe.append(todays_sharpe)
        return self.sharpe


class Index4_pre_loaded:
    def __init__(self, symbol_list, data):
        self.symbol_list = symbol_list
        self.data = data
        self.sortino_series = pd.read_csv(
            "PickledData/Index4_stocks.csv", index_col="Date", parse_dates=True
        )["Sortino"]
        self.sortino = []

    def calculate_sortino(self):
        date = self.data.get_latest_bar_datetime(self.symbol_list[0])
        todays_sortino = self.sortino_series.loc[date]
        self.sortino.append(todays_sortino)
        return self.sortino


class Index3_v2_pre_loaded:
    def __init__(self, symbol_list, data):
        self.symbol_list = symbol_list
        self.data = data
        self.sharpe_series = pd.read_csv(
            "PickledData/Index3_v2_stocks.csv", index_col="Date", parse_dates=True
        )["Sharpe"]
        self.sharpe = []

    def calculate_sharpe(self):
        date = self.data.get_latest_bar_datetime(self.symbol_list[0])
        todays_sharpe = self.sharpe_series.loc[date]
        self.sharpe.append(todays_sharpe)
        return self.sharpe


class Index4_v2_pre_loaded:
    def __init__(self, symbol_list, data):
        self.symbol_list = symbol_list
        self.data = data
        self.sortino_series = pd.read_csv(
            "PickledData/Index4_v2_stocks.csv", index_col="Date", parse_dates=True
        )["Sortino"]
        self.sortino = []

    def calculate_sortino(self):
        date = self.data.get_latest_bar_datetime(self.symbol_list[0])
        todays_sortino = self.sortino_series.loc[date]
        self.sortino.append(todays_sortino)
        return self.sortino
