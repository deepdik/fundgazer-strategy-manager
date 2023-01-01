import pandas as pd
from api.utils.strategy_logics.packages.indicators.momentum import rsi
from api.utils.strategy_logics.packages.indicators.trend_indicators import ema, adx
from api.utils.strategy_logics.packages.indicators.volume import obv
from api.utils.strategy_logics.packages.helper.helper import atr
from api.utils.strategy_logics.packages.indicators.support_resistance import fractals


def ema_condition(symbol, data, period_ema, trend="Breakout"):
    score = 0
    if trend == "Breakout":
        trend_factor = 1
    else:
        trend_factor = -1
    ema_value = ema(data.latest_symbol_data[symbol].Close, period_ema)[-1]
    price = data.latest_symbol_data[symbol].Close[-1]
    if not (ema_value == ema_value):
        return 0
    if price > ema_value:
        score += 1
    else:
        score -= 1
    return score * trend_factor


def rising_adx_condition(symbol, data, period_adx, rising_period, trend="Breakout"):
    score = 0
    if trend == "Breakout":
        trend_factor = 1
    else:
        trend_factor = -1
    adx_series = adx(data.latest_symbol_data[symbol], period_adx)
    if not adx_series[-rising_period] == adx_series[-rising_period]:
        return 0
    if adx_series[-rising_period] < adx_series[-1]:
        score += 1
    else:
        score -= 1
    return score * trend_factor


def adx_ema_condition(symbol, data, period_adx, period_ema, trend="Breakout"):
    score = 0
    if trend == "Breakout":
        trend_factor = 1
    else:
        trend_factor = -1
    adx_series = adx(data.latest_symbol_data[symbol], period_adx)
    ema_series = ema(adx_series, period_ema)
    if not (adx_series[-1] == adx_series[-1]) or not (ema_series[-1] == ema_series[-1]):
        return 0
    if ema_series[-1] < adx_series[-1]:
        score += 1
    else:
        score -= 1
    return score * trend_factor


def obv_ema_condition(symbol, data, period_ema, trend="Breakout"):
    score = 0
    if trend == "Breakout":
        trend_factor = 1
    else:
        trend_factor = -1
    obv_series = obv(data.latest_symbol_data[symbol])
    ema_series = ema(obv_series, period_ema)
    if not (obv_series[-1] == obv_series[-1]) or not (ema_series[-1] == ema_series[-1]):
        return 0
    if ema_series[-1] < obv_series[-1]:
        score += 1
    else:
        score -= 1
    return score * trend_factor


def long_rsi_condition(symbol, data, period_rsi, trend="Breakout"):
    score = 0
    if trend == "Breakout":
        trend_factor = 1
    else:
        trend_factor = -1
    rsi_series = rsi(data.latest_symbol_data[symbol], period_rsi)
    if not (rsi_series[-1] == rsi_series[-1]):
        return 0
    if rsi_series[-1] > 60:
        score += 1
    if rsi_series[-1] < 40:
        score -= 1
    return score * trend_factor


def short_rsi_condition(symbol, data, period_rsi, trend="Breakout"):
    score = 0
    if trend == "Breakout":
        trend_factor = 1
    else:
        trend_factor = -1
    rsi_series = rsi(data.latest_symbol_data[symbol], period_rsi)
    if not (rsi_series[-1] == rsi_series[-1]):
        return 0
    if rsi_series[-1] > 80:
        score += 1
    if rsi_series[-1] < 20:
        score -= 1
    return score * trend_factor


def standard_deviation_condition(symbol, data, median_std, trend="Breakout"):
    score = 0
    if trend == "Breakout":
        trend_factor = 1
    else:
        trend_factor = -1
    std = data.latest_symbol_data[symbol].Close.pct_change().std()
    if std > median_std:
        score += 1
    else:
        score -= 1
    return score * trend_factor


def standard_deviation_negetive_condition(symbol, data, median_std, trend="Breakout"):
    score = 0
    if trend == "Breakout":
        trend_factor = 1
    else:
        trend_factor = -1
    std = (
        data.latest_symbol_data[symbol]
        .Close.pct_change()
        .where(lambda x: x < 0)
        .dropna()
        .std()
    )
    if not std == std:
        return 0
    if std > median_std:
        score += 1
    else:
        score -= 1
    return score * trend_factor


def atr_ema_condition(symbol, data, period_atr, period_ema, trend="Breakout"):
    score = 0
    if trend == "Breakout":
        trend_factor = 1
    else:
        trend_factor = -1
    atr_series = atr(data.latest_symbol_data[symbol], period_atr)
    ema_series = ema(atr_series, period_ema)
    if not ema_series[-1] == ema_series[-1]:
        return 0
    if atr_series[-1] > ema_series[-1]:
        score += 1
    else:
        score -= 1
    return score * trend_factor


def calculate_index_price(daily_returns, base_price=100):
    prices = []
    for i, j in enumerate(daily_returns):
        if i < 1:
            prices.append(base_price * (1 + j))
        else:
            prices.append(prices[i - 1] * (1 + j))
    return prices


def relative_strength_with_index(
        symbol, data, ema_period, index_prices, trend="Breakout"
):
    score = 0
    if trend == "Breakout":
        trend_factor = 1
    else:
        trend_factor = -1
    relative_strength = data.latest_symbol_data[symbol].Close / index_prices
    ema_strength = ema(relative_strength, ema_period)
    if not ema_strength[-1] == ema_strength[-1]:
        return 0
    if relative_strength[-1] > ema_strength[-1]:
        score += 1
    else:
        score -= 1
    return score * trend_factor


def fractal_condition(symbol, data, trend="Breakout"):
    score = 0
    if trend == "Breakout":
        trend_factor = 1
    else:
        trend_factor = -1
    up, down = fractals(data.latest_symbol_data[symbol])
    up_fractals = up[up == 1]
    down_fractals = down[down == 1].index

    if len(down_fractals) == 0:
        return score

    if len(up_fractals) == 0:
        return score

    last_up = up_fractals.index[-1]
    last_down = down_fractals[-1]

    price = data.get_latest_bar_value(symbol, "Close")
    if price > data.latest_symbol_data[symbol].loc[last_up].High:
        score += 1
    if price < data.latest_symbol_data[symbol].loc[last_down].Low:
        score += 1
    return score * trend_factor


def calculate_median_std(filtered_stocks, data):
    std = []
    for symbol in filtered_stocks:
        std.append(data.latest_symbol_data[symbol].Close.pct_change().std())
    return pd.Series(std).median()


class pattern_pre_loaded:

    def __init__(self, symbol, data, nDays):
        self.symbol = symbol
        self.data = data
        self.divergence_series = pd.read_csv(f'divergence_new/rsi_{symbol}_list.csv', index_col="Date", parse_dates=True
                                             )["divergence"]
        self.nDays = nDays

    def pattern_condition(self, trend="Breakout"):
        score = 0
        if trend == "Breakout":
            trend_factor = 1
        else:
            trend_factor = -1

        date = self.data.get_latest_bar_datetime(self.symbol)
        # print("this is date")
        # print(date)
        divergence_series = self.divergence_series.loc[:date]
        nDays_div_series = divergence_series.iloc[-self.nDays:]
        # print(nDays_div_series)
        nDays_list = nDays_div_series.values.tolist()

        flagBull = False
        flagBear = False

        if "Bullish" in nDays_list:
            flagBull = True
            # print("flagBull=True")

        if "Bearish" in nDays_list:
            flagBear = True
            # print("flagBull=True")

        if flagBull == True:
            score += 1

        if flagBear == True:
            score -= 1

        return score * trend_factor

    def single_Bullish_pattern_condition(self, trend="Breakout"):
        score = 0
        if trend == "Breakout":
            trend_factor = 1
        else:
            trend_factor = -1

        date = self.data.get_latest_bar_datetime(self.symbol)
        # print("this is date")
        # print(date)
        divergence_series = self.divergence_series.loc[:date]
        nDays_div_series = divergence_series.iloc[-self.nDays:]
        # print(nDays_div_series)
        nDays_list = nDays_div_series.values.tolist()

        flagBull = False
        flagBear = False

        if "Bullish" in nDays_list:
            flagBull = True
            # print("flagBull=True")

        if flagBull == True:
            score += 1

        return score * trend_factor

    def single_Bearish_pattern_condition(self, trend="Breakout"):
        score = 0
        if trend == "Breakout":
            trend_factor = 1
        else:
            trend_factor = -1

        date = self.data.get_latest_bar_datetime(self.symbol)
        # print("this is date")
        # print(date)
        divergence_series = self.divergence_series.loc[:date]
        nDays_div_series = divergence_series.iloc[-self.nDays:]
        # print(nDays_div_series)
        nDays_list = nDays_div_series.values.tolist()

        flagBull = False
        flagBear = False

        if "Bearish" in nDays_list:
            flagBear = True
            # print("flagBull=True")

        if flagBear == True:
            score -= 1

        return score * trend_factor

    def double_pattern_condition(self, trend="Breakout"):
        score = 0
        if trend == "Breakout":
            trend_factor = 1
        else:
            trend_factor = -1

        date = self.data.get_latest_bar_datetime(self.symbol)
        # print("this is date")
        # print(date)
        divergence_series = self.divergence_series.loc[:date]
        nDays_div_series = divergence_series.iloc[-self.nDays:]
        # print(nDays_div_series)
        nDays_list = nDays_div_series.values.tolist()

        flagBull = False
        flagBear = False

        if "Bullish" in nDays_list:
            flagBull = True
            # print("flagBull=True")

        if "Bearish" in nDays_list:
            flagBear = True
            # print("flagBull=True")

        if flagBull == True:
            score += 1

        if flagBear == True:
            score -= 1

        return score * trend_factor