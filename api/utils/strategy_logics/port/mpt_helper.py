import numpy as np
import pandas as pd
from scipy.optimize import minimize


def calculate_returns(stocks_list, data, number_of_days=200):
    # entry_prices = {}
    expected_returns = {}
    # volatility = {}
    rate_of_returns = {}
    for symbol in stocks_list:
        rate_of_returns[symbol] = data.latest_symbol_data[symbol].iloc[-number_of_days:].Close.pct_change()
        expected_returns[symbol] = (
            data.latest_symbol_data[symbol].iloc[-number_of_days:].Close.pct_change().mean()
        )
    rate_of_returns_portfolio = pd.DataFrame(rate_of_returns, columns=stocks_list)
    covariance_matrix_portfolio = rate_of_returns_portfolio.cov()
    return rate_of_returns, expected_returns, covariance_matrix_portfolio


def calculate_returns_negetive_only(stocks_list, data, number_of_days=200):
    expected_returns = {}
    rate_of_returns = {}
    for symbol in stocks_list:
        rate_of_returns[symbol] = (
            data.latest_symbol_data[symbol].iloc[-number_of_days:]
            .Close.pct_change()
            .where(lambda x: x < 0)
            .dropna()
        )
        expected_returns[symbol] = (
            data.latest_symbol_data[symbol].iloc[-number_of_days:].Close.pct_change().mean()
        )
    rate_of_returns_portfolio = pd.DataFrame(rate_of_returns, columns=stocks_list)
    covariance_matrix_portfolio = rate_of_returns_portfolio.cov()
    return rate_of_returns, expected_returns, covariance_matrix_portfolio


def redistribute_tangency_portfolio(
        stocks_list, covariance_matrix, expected_returns) -> dict:

    x_len = len(stocks_list)
    weight0 = [1 / x_len] * x_len

    def objective(weights):
        daily_returns = list(expected_returns.values())
        returns = np.dot(weights, daily_returns)
        variance = (
            covariance_matrix.mul(weights, axis=0).mul(weights, axis=1).sum().sum()
        )
        sigma = np.sqrt(variance)
        maximize_variable = (returns - 0.00023) / sigma
        return -maximize_variable * np.sqrt(252)

    def constraint(x):
        return 1 - sum(x)

    # Main Optimization
    b = (0, 1)
    bounds = [b] * x_len
    cons = {"type": "eq", "fun": constraint}
    sol = minimize(objective, weight0, method="SLSQP", bounds=bounds, constraints=cons)
    return sol


def redistribute_tangency_portfolio2(
        stocks_list, covariance_matrix, daily_returns
) -> dict:
    x_len = len(stocks_list)
    weight0 = [1 / x_len] * x_len

    def objective(weights):
        returns = daily_returns
        variance = (
            covariance_matrix.mul(weights, axis=0).mul(weights, axis=1).sum().sum()
        )
        sigma = np.sqrt(variance)
        maximize_variable = (returns - 0.00023) / sigma
        return -maximize_variable * np.sqrt(252)

    def constraint(x):
        return 1 - sum(x)

    # Main Optimization
    b = (0, 1)
    bounds = [b] * x_len
    cons = {"type": "eq", "fun": constraint}
    sol = minimize(objective, weight0, method="SLSQP", bounds=bounds, constraints=cons)
    return sol


def redistribute_min_risk_portfolio(
        stocks_list, covariance_matrix, expected_returns
) -> dict:
    x_len = len(stocks_list)
    weight0 = [1 / x_len] * x_len

    def objective(weights, expected_returns, covariance_matrix):
        # daily_returns = list(expected_returns.values())
        # returns = np.dot(weights, daily_returns)
        variance = (
            covariance_matrix.mul(weights, axis=0).mul(weights, axis=1).sum().sum()
        )
        sigma = np.sqrt(variance)
        return sigma

    def constraint(x):
        return 1 - sum(x)

    # Main Optimization
    b = (0, 1)
    bounds = [b] * x_len
    cons = {"type": "eq", "fun": constraint}
    sol = minimize(
        fun=objective,
        x0=weight0,
        args=(expected_returns, covariance_matrix),
        method="SLSQP",
        bounds=bounds,
        constraints=cons,
    )
    daily_return = list(expected_returns.values())
    returns = np.dot(sol.x, daily_return)
    y = (returns - 0.00023) / sol.fun
    return y * np.sqrt(252)


def calculate_current_portfolio_sharpe(expected_returns, weights, covariance_matrix):
    daily_returns = list(expected_returns.values())
    returns = np.dot(weights, daily_returns)
    variance = covariance_matrix.mul(weights, axis=0).mul(weights, axis=1).sum().sum()
    sigma = np.sqrt(variance)
    return np.sqrt(252) * (returns - 0.00023) / sigma


def calculate_portfolio_value(weights, stocks, data):
    prices = [data.get_latest_bar_value(i, "Close") for i in stocks]
    return np.dot(weights, prices)
