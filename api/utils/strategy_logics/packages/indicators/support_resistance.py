import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score
from api.utils.strategy_logics.packages.helper.helper import cuts, atr, true_range
from api.utils.strategy_logics.packages.indicators.trend_indicators import ema, rising_adx, adx
from kneed import KneeLocator


def is_support(df, n):
    """Returns True if a DOWN fractal is formed else returns False after n candles

    Args:
        df ([pd.DataFrame]): [symbol data]
        i ([int]): [fractal length]

    Returns:
        [Bool]: [Returns True if a DOWN fractal is formed else returns False]
    """
    down_fractals = find_minima(df, n)
    if df.iloc[-n - 1].name == down_fractals.index[-1]:
        return True
    else:
        return False


def is_resistance(df, n):
    """Returns True if a UP fractal is formed else returns False after n candles

    Args:
        df ([pd.DataFrame]): [symbol data]
        i ([int]): [fractal length]

    Returns:
        [Bool]: [Returns True if a UP fractal is formed else returns False]
    """
    up_fractals = find_maxima(df, n)
    if df.iloc[-n - 1].name == up_fractals.index[-1]:
        return True
    else:
        return False


def find_maxima(df, n):
    """returns a series of last up fractals

    Args:
        df ([pd.Dataframe]): [symbol data]
        n ([int]): [fractals length]

    Returns:
        [pd.Series]: [subset series of dataframe having up fratals]
    """
    rolling_period = 2 * n + 1
    bear_fractal = (
        df["High"]
        .rolling(rolling_period, center=True)
        .apply(lambda x: x[n] == max(x), raw=True)
    )
    return bear_fractal[bear_fractal == 1]


def find_minima(df, n):
    """returns a series of last down fractals

    Args:
        df ([pd.Dataframe]): [symbol data]
        n ([int]): [fractals length]

    Returns:
        [pd.Series]: [subset series of dataframe having down fratals]
    """
    rolling_period = 2 * n + 1
    bull_fractal = (
        df["Low"]
        .rolling(rolling_period, center=True)
        .apply(lambda x: x[n] == min(x), raw=True)
    )
    return bull_fractal[bull_fractal == 1]


def fractals(df, n=2):
    """Returns William Fractals for a given n,
    Outputs a tuple(up_fracals[pd.series], down_fractals[pd.series]),
    This series contains all indexes having values 1 and 0

    Args:
        df ([pd.DataFrame]): [symbol Data]
        n (int, optional): [fractal length]. Defaults to 2.

    Returns:
        [tuple]: [up fractals series,down fractals series]
    """
    rolling_period = 2 * n + 1
    bear_fractal = (
        df["High"]
        .rolling(rolling_period, center=True)
        .apply(lambda x: x[n] == max(x), raw=True)
    )
    bull_fractal = (
        df["Low"]
        .rolling(rolling_period, center=True)
        .apply(lambda x: x[n] == min(x), raw=True)
    )
    return bear_fractal, bull_fractal


def order_block_full1(df, fractal_period=2, period_adx=14):
    """Order Block on full data without the atr condition

    Args:
        df (pd.DataFrame): Full Data
        fractal_period (int, optional): fractal period. Defaults to 2.
        period_atr (int, optional): atr period. Defaults to 14.

    Returns:
        tuple(List,List): returns list of orderblocks min and max
    """
    a, b = fractals(df, fractal_period)
    up_fractals = a[a == 1].index
    down_fractals = b[b == 1].index
    df["ADX"] = adx(df, period_adx)
    r_adx = rising_adx(df).index
    order_block_max = []
    for i in range(len(up_fractals) - 1):
        start, end = up_fractals[i : i + 2]
        breakout_region = df.loc[start:end].iloc[1:-1]
        for j in breakout_region.iterrows():
            if cuts(df, j[0], df.loc[start].High):
                if j[0] in r_adx:
                    gen = breakout_region.loc[: j[0]].iloc[::-1].iterrows()
                    while True:
                        try:
                            k = next(gen)[0]
                            if df.loc[k].Open > df.loc[k].Close:
                                order_block_max.append(k)
                                break

                            else:
                                continue
                        except StopIteration:
                            break
                    break
    order_block_min = []
    for i in range(len(down_fractals) - 1):
        start, end = down_fractals[i : i + 2]
        breakout_region = df.loc[start:end].iloc[1:-1]
        for j in breakout_region.iterrows():
            if cuts(df, j[0], df.loc[start].Low):
                if j[0] in r_adx:
                    gen = breakout_region.loc[: j[0]].iloc[::-1].iterrows()
                    while True:
                        try:
                            k = next(gen)[0]
                            if df.loc[k].Open < df.loc[k].Close:
                                order_block_min.append(k)
                                break

                            else:
                                continue
                        except StopIteration:
                            break
                    break
    return order_block_min, order_block_max


def order_block_full(df, fractal_period=2, period_atr=14, period_adx=14):
    """Order Block on full data with the original ATR condition

    Args:
        df (pd.DataFrame): Full data
        fractal_period (int, optional): fractal period. Defaults to 2.
        period_atr (int, optional): atr period. Defaults to 14.

    Returns:
        tuple(List,List): returns list of orderblocks min and max
    """
    a, b = fractals(df, fractal_period)
    up_fractals = a[a == 1].index
    down_fractals = b[b == 1].index
    df["TR"] = true_range(df)
    df["ATR"] = atr(df, period_atr)
    df["ADX"] = adx(df, period_adx)
    r_adx = rising_adx(df).index
    order_block_max = []
    for i in range(len(up_fractals) - 1):
        start, end = up_fractals[i : i + 2]
        breakout_region = df.loc[start:end].iloc[1:-1]
        for j in breakout_region.iterrows():
            if cuts(df, j[0], df.loc[start].High) and (
                df.loc[j[0] :].iloc[:2].eval("TR > ATR").sum() > 1
            ):
                if j[0] in r_adx:
                    gen = breakout_region.loc[: j[0]].iloc[::-1].iterrows()
                    while True:
                        try:
                            k = next(gen)[0]
                            if df.loc[k].Open > df.loc[k].Close:
                                order_block_max.append(k)
                                break

                            else:
                                continue
                        except StopIteration:
                            break
                    break
    order_block_min = []
    for i in range(len(down_fractals) - 1):
        start, end = down_fractals[i : i + 2]
        breakout_region = df.loc[start:end].iloc[1:-1]
        for j in breakout_region.iterrows():
            if cuts(df, j[0], df.loc[start].Low) and (
                df.loc[j[0] :].iloc[:2].eval("TR > ATR").sum() > 1
            ):
                if j[0] in r_adx:
                    gen = breakout_region.loc[: j[0]].iloc[::-1].iterrows()
                    while True:
                        try:
                            k = next(gen)[0]
                            if df.loc[k].Open < df.loc[k].Close:
                                order_block_min.append(k)
                                break

                            else:
                                continue
                        except StopIteration:
                            break
                    break
    return order_block_min, order_block_max


class OrderBlock_Indicator_Simple:
    def __init__(self, events, data):
        self.events = events
        self.data = data
        self.symbol_list = data.symbol_list
        self.breakout_max = None
        self.breakout_min = None
        self.last_min = None
        self.last_max = None
        self.last_ob_buy = None
        self.last_ob_sell = None
        self.register = pd.DataFrame(
            columns=["breakout", "ob_candle", "fractal"]
        ).set_index("ob_candle")

    def find_pivots(self):
        for symbol in self.symbol_list:
            if is_resistance(self.data.latest_symbol_data[symbol], 2):
                self.last_max = self.data.latest_symbol_data[symbol].index[-3]
                self.last_ob_buy = None
            if is_support(self.data.latest_symbol_data[symbol], 2):
                self.last_min = self.data.latest_symbol_data[symbol].index[-3]
                self.last_ob_sell = None

    def find_breakout(self):

        for symbol in self.symbol_list:
            df = self.data.latest_symbol_data[symbol]

            # UP BREAKOUT OF ORDERBLOCK
            if (
                self.last_ob_buy is None
                and self.last_max is not None
                and self.last_max not in self.register.fractal.values
            ):
                high = df.loc[self.last_max]
                cur_idx = self.data.get_latest_bar_datetime(symbol)
                # print('Fractal:',high.name,' Current: ',cur_idx)
                if df.loc[cur_idx].Close > high.High:
                    #                     for j in df.iloc[-2 : self.last_max + 1 : -1].iterrows():
                    for j in (
                        df.iloc[:-2].loc[self.last_max :].iloc[1:].iloc[::-1].iterrows()
                    ):
                        if j[1].Open > j[1].Close:
                            self.breakout_max = True
                            self.register.loc[j[0], "breakout"] = cur_idx
                            self.register.loc[j[0], "fractal"] = self.last_max
                            self.last_ob_buy = j[0]
                            # print('UP: ',df.iloc[self.last_max].name,self.last_ob_buy,cur_idx,sep='|')
                            return True
                    break

            # DOWN BREAKOUT FOR ORDERBLOCK
            if (
                self.last_ob_sell is None
                and self.last_min is not None
                and self.last_min not in self.register.fractal.values
            ):
                low = df.loc[self.last_min]
                cur_idx = self.data.get_latest_bar_datetime(symbol)
                # print('Fractal:',low.name,' Current: ',cur_idx)
                if df.loc[cur_idx].Close < low.Low:
                    #                     for j in df.iloc[-2 : self.last_min + 1 : -1].iterrows():
                    for j in (
                        df.iloc[:-2].loc[self.last_min :].iloc[1:].iloc[::-1].iterrows()
                    ):
                        if j[1].Open < j[1].Close:
                            self.breakout_min = True
                            self.register.loc[j[0], "breakout"] = cur_idx
                            self.register.loc[j[0], "fractal"] = self.last_min
                            self.last_ob_sell = j[0]
                            # print('UP: ',df.iloc[self.last_min].name,self.last_ob_sell,cur_idx,sep='|')
                            return True
                    break

    def find_ob(self):
        self.find_pivots()
        if self.find_breakout():
            return self.last_ob_buy, self.last_ob_sell
        else:
            return False


# class OrderBlock_Indicator:
#     def __init__(self, events, data):
#         self.events = events
#         self.data = data
#         self.symbol_list = data.symbol_list
#         self.breakout_max = None
#         self.breakout_min = None
#         self.last_min = None
#         self.last_max = None
#         self.last_ob_buy = None
#         self.last_ob_sell = None
#         self.register = pd.DataFrame(
#             columns=["breakout", "ob_candle", "fractal"]
#         ).set_index("ob_candle")

#     def find_pivots(self):
#         for symbol in self.symbol_list:
#             price = self.data.latest_symbol_data[symbol].Close

#         try:
#             max_idx = list(argrelextrema(price.values, np.greater, order=3)[0])
#             if self.last_max != max_idx[-1]:
#                 self.last_max = max_idx[-1]
#                 self.last_ob_buy = None
#         except IndexError:
#             pass

#         try:
#             min_idx = list(argrelextrema(price.values, np.less, order=3)[0])
#             if self.last_min != min_idx[-1]:
#                 self.last_min = min_idx[-1]
#                 self.last_ob_sell = None
#         except IndexError:
#             pass

#     def find_breakout(self):

#         for symbol in self.symbol_list:
#             df = self.data.latest_symbol_data[symbol]

#             # For up breakout
#             if (
#                 self.last_ob_buy is None
#                 and self.last_max is not None
#                 and self.last_max not in self.register.fractal.values
#             ):
#                 high = df.iloc[self.last_max]
#                 cur_idx = df.iloc[-1].name
#                 # print('Fractal:',high.name,' Current: ',cur_idx)
#                 if df.loc[cur_idx].Close > high.High:
#                     for j in df.iloc[-3 : self.last_max + 1 : -1].iterrows():
#                         indx = df.index.get_loc(j[0])
#                         if is_support(df, indx):
#                             # print('Support:',j[0])                              ## j is support
#                             for k in df.iloc[indx + 1 :].loc[:cur_idx].iterrows():
#                                 if k[1].Open > k[1].Close:
#                                     self.breakout_max = True
#                                     self.register.loc[j[0], "breakout"] = cur_idx
#                                     self.register.loc[j[0], "fractal"] = self.last_max
#                                     self.last_ob_buy = k[0]
#                                     # print('UP: ',df.iloc[self.last_max].name,self.last_ob_buy,cur_idx,sep='|')
#                                     return True

#                             for k in df.iloc[indx : self.last_max : -1].iterrows():
#                                 if k[1].Open > k[1].Close:
#                                     self.breakout_max = True
#                                     self.register.loc[j[0], "breakout"] = cur_idx
#                                     self.register.loc[j[0], "fractal"] = self.last_max
#                                     self.last_ob_buy = k[0]
#                                     # print('UP: ',df.iloc[self.last_max].name,self.last_ob_buy,cur_idx,sep='|')
#                                     return True
#                             break

#             # For down breakout
#             if (
#                 self.last_ob_sell is None
#                 and self.last_min is not None
#                 and self.last_min not in self.register.fractal.values
#             ):
#                 low = df.iloc[self.last_min]
#                 cur_idx = df.iloc[-1].name
#                 # print('Fractal:',low.name,' Current: ',cur_idx)
#                 if df.loc[cur_idx].Close < low.Low:
#                     for j in df.iloc[-3 : self.last_min + 1 : -1].iterrows():
#                         indx = df.index.get_loc(j[0])
#                         if is_resistance(df, indx):
#                             # print('Resistance:',j[0])                              ## j is resistance
#                             for k in df.iloc[indx + 1 :].loc[:cur_idx].iterrows():
#                                 if k[1].Open < k[1].Close:
#                                     self.breakout_min = True
#                                     self.register.loc[j[0], "breakout"] = cur_idx
#                                     self.register.loc[j[0], "fractal"] = self.last_min
#                                     self.last_ob_sell = k[0]
#                                     # print('UP: ',df.iloc[self.last_min].name,self.last_ob_sell,cur_idx,sep='|')
#                                     return True

#                             for k in df.iloc[indx : self.last_min : -1].iterrows():
#                                 if k[1].Open < k[1].Close:
#                                     self.breakout_min = True
#                                     self.register.loc[j[0], "breakout"] = cur_idx
#                                     self.register.loc[j[0], "fractal"] = self.last_min
#                                     self.last_ob_sell = k[0]
#                                     # print('UP: ',df.iloc[self.last_min].name,self.last_ob_sell,cur_idx,sep='|')
#                                     return True
#                             break

#     def find_ob(self):
#         self.find_pivots()
#         if self.find_breakout():
#             return self.last_ob_buy, self.last_ob_sell
#         else:
#             return False


class OrderBlock_Indicator_unknown:
    def __init__(self, data):
        self.symbol = data.symbol_list
        self.data = data
        book = pd.DataFrame(columns=["Fractal", "OB", "Breakout", "Type"]).set_index(
            "Fractal"
        )
        self.ob = dict((a, book) for a in self.symbol)
        self.latest = {}
        for s in self.symbol:
            self.latest[s] = {
                "maxima": None,
                "minima": None,
                "maxima_br": None,
                "minima_br": None,
            }

    def _make_data(self, dt):
        dt["TR"] = true_range(dt)
        dt["ATR"] = atr(dt, 14)
        dt["ADX"] = adx(dt, 14)

    def find_ob(self):
        for s in self.symbol:
            if not self.data.latest_symbol_data[s].empty:
                self._make_data(self.data.latest_symbol_data[s])
                self._find_fractals(s)
                self._find_breakout(s)
                return self._backtrace_to_ob(s)

    def _find_fractals(self, symbol):
        if self.ob[symbol].query('Type == "Minima"').empty:
            if is_support(
                self.data.latest_symbol_data[symbol],
                self.data.get_latest_bar_index(symbol) - 2,
            ):  # Index Error
                minima = (
                    self.data.latest_symbol_data[symbol]
                    .iloc[self.data.get_latest_bar_index(symbol) - 2]
                    .name
                )
                self.ob[symbol] = self.ob[symbol].append(
                    pd.Series({"Type": "Minima"}, name=minima)
                )
                self.latest["minima"] = minima

        if self.ob[symbol].query('Type == "Maxima"').empty:
            if is_resistance(
                self.data.latest_symbol_data[symbol],
                self.data.get_latest_bar_index(symbol) - 2,
            ):  # IndexERROR
                maxima = (
                    self.data.latest_symbol_data[symbol]
                    .iloc[self.data.get_latest_bar_index(symbol) - 2]
                    .name
                )
                self.ob[symbol] = self.ob[symbol].append(
                    pd.Series({"Type": "Maxima"}, name=maxima)
                )
                self.latest[symbol]["maxima"] = maxima
        else:
            self._update_fractals(symbol)

    def _update_fractals(self, symbol):
        if is_support(
            self.data.latest_symbol_data[symbol],
            self.data.get_latest_bar_index(symbol) - 2,
        ):  # Index Error
            minima = (
                self.data.latest_symbol_data[symbol]
                .iloc[self.data.get_latest_bar_index(symbol) - 2]
                .name
            )
            self.ob[symbol] = self.ob[symbol].append(
                pd.Series({"Type": "Minima"}, name=minima)
            )
            self.latest[symbol]["minima"] = minima
            self.latest[symbol]["minima_br"] = None

        if is_resistance(
            self.data.latest_symbol_data[symbol],
            self.data.get_latest_bar_index(symbol) - 2,
        ):  # IndexERROR
            maxima = (
                self.data.latest_symbol_data[symbol]
                .iloc[self.data.get_latest_bar_index(symbol) - 2]
                .name
            )
            self.ob[symbol] = self.ob[symbol].append(
                pd.Series({"Type": "Maxima"}, name=maxima)
            )
            self.latest[symbol]["maxima"] = maxima
            self.latest[symbol]["maxima_br"] = None

    def _find_breakout(self, s):

        if (self.latest[s]["maxima_br"] is None) & (
            self.latest[s]["maxima"] is not None
        ):
            if (
                self.data.get_latest_bar_datetime(s) - self.latest[s]["maxima"]
            ).days < 2:
                if cuts(
                    self.data.latest_symbol_data[s],
                    self.data.latest_symbol_data[s]
                    .iloc[self.data.get_latest_bar_index(s) - 1]
                    .name,
                    self.data.latest_symbol_data[s].loc[self.latest[s]["maxima"]].High,
                ):
                    if (
                        self.data.latest_symbol_data[s]
                        .iloc[self.data.get_latest_bar_index(s) - 1]
                        .TR
                        > self.data.latest_symbol_data[s]
                        .iloc[self.data.get_latest_bar_index(s) - 1]
                        .ATR
                    ) or (
                        self.data.get_latest_bar_value(s, "TR")
                        > self.data.get_latest_bar_value(s, "ATR")
                    ):
                        if (
                            self.data.latest_symbol_data[s]
                            .iloc[self.data.get_latest_bar_index(s) - 1]
                            .ADX
                            > self.data.latest_symbol_data[s]
                            .iloc[self.data.get_latest_bar_index(s) - 11]
                            .ADX
                        ):
                            maxima_bk = (
                                self.data.latest_symbol_data[s]
                                .iloc[self.data.get_latest_bar_index(s) - 1]
                                .name
                            )
                            self.latest[s]["maxima_br"] = maxima_bk

        if (self.latest[s]["minima_br"] is None) & (
            self.latest[s]["minima"] is not None
        ):
            if (
                self.data.get_latest_bar_datetime(s) - self.latest[s]["minima"]
            ).days < 2:
                if cuts(
                    self.data.latest_symbol_data[s],
                    self.data.latest_symbol_data[s]
                    .iloc[self.data.get_latest_bar_index(s) - 1]
                    .name,
                    self.data.latest_symbol_data[s].loc[self.latest[s]["minima"]].Low,
                ):
                    if (
                        self.data.latest_symbol_data[s]
                        .iloc[self.data.get_latest_bar_index(s) - 1]
                        .TR
                        > self.data.latest_symbol_data[s]
                        .iloc[self.data.get_latest_bar_index(s) - 1]
                        .ATR
                    ) or (
                        self.data.get_latest_bar_value(s, "TR")
                        > self.data.get_latest_bar_value(s, "ATR")
                    ):
                        if (
                            self.data.latest_symbol_data[s]
                            .iloc[self.data.get_latest_bar_index(s) - 1]
                            .ADX
                            > self.data.latest_symbol_data[s]
                            .iloc[self.data.get_latest_bar_index(s) - 11]
                            .ADX
                        ):
                            minima_bk = (
                                self.data.latest_symbol_data[s]
                                .iloc[self.data.get_latest_bar_index(s) - 1]
                                .name
                            )
                            self.latest[s]["minima_br"] = minima_bk
                            # print('Breakout_MINIMA:',minima_bk,self.latest['minima'])

    def _backtrace_to_ob(self, s):
        if (self.latest[s]["maxima_br"] is not None) & (
            self.latest[s]["maxima"] is not None
        ):
            start = self.data.latest_symbol_data[s].index.get_loc(
                self.latest[s]["maxima"]
            )
            end = self.data.latest_symbol_data[s].index.get_loc(
                self.latest[s]["maxima_br"]
            )
            back_data_maxima = (
                self.data.latest_symbol_data[s]
                .iloc[start + 1 : end]
                .iloc[::-1]
                .iterrows()
            )
            # print('BACK_DATA_MAX:',self.latest['maxima'],":",self.latest['maxima_br'])
            for i in back_data_maxima:
                if (
                    self.data.latest_symbol_data[s].loc[i[0]].Open
                    > self.data.latest_symbol_data[s].loc[i[0]].Close
                ):
                    # RED OB
                    self.ob[s] = self.ob[s].append(
                        pd.Series(
                            {
                                "Fractal": self.latest[s]["maxima"],
                                "Type": "Red",
                                "Breakout": self.latest[s]["maxima_br"],
                            },
                            name=i[0],
                        )
                    )
                    # print('RED:',i[0])
                    return "Red", i[0], self.latest[s]["maxima_br"]
                    self.latest[s]["maxima"] = None
                    self.latest[s]["maxima_br"] = None
                    break
                else:
                    pass  # Remove this Breakout or Move to next fractal
            self.latest[s]["maxima_br"] = None

        if (self.latest[s]["minima_br"] is not None) & (
            self.latest[s]["minima"] is not None
        ):
            start = self.data.latest_symbol_data[s].index.get_loc(
                self.latest[s]["minima"]
            )
            end = self.data.latest_symbol_data[s].index.get_loc(
                self.latest[s]["minima_br"]
            )
            back_data_minima = (
                self.data.latest_symbol_data[s]
                .iloc[start + 1 : end]
                .iloc[::-1]
                .iterrows()
            )
            # print('BACK_DATA_MIN:',self.latest['minima'],":",self.latest['minima_br'])
            for j in back_data_minima:
                if (
                    self.data.latest_symbol_data[s].loc[j[0]].Open
                    < self.data.latest_symbol_data[s].loc[j[0]].Close
                ):
                    self.ob[s] = self.ob[s].append(
                        pd.Series(
                            {
                                "Fractal": self.latest[s]["minima"],
                                "Type": "Green",
                                "Breakout": self.latest[s]["minima_br"],
                            },
                            name=j[0],
                        )
                    )
                    # print('Green:',j[0])
                    return "Green", j[0], self.latest[s]["minima_br"]
                    self.latest[s]["minima_br"] = None
                    self.latest[s]["minima"] = None
                    break
                else:
                    pass
            self.latest[s]["minima_br"] = None


# def order_block_full(data):
#     a, b = Pivots(data, 2)  # Pivotup#pivotdown
#     data["TR"] = true_range(data)
#     data["ATR"] = atr(data, 14)
#     data["ADX"] = adx(data, 14)
#     RA = Rising_ADX(data)

#     order_block_min = []
#     for i in range(1, len(b)):
#         start = data.iloc[b[i - 1]].name
#         start = data.index.get_loc(start) + 1
#         end = data.iloc[b[i]].name
#         end = data.index.get_loc(end) - 1

#         breakout_region = data.iloc[start:end].iterrows()
#         for j in breakout_region:
#             if cuts(data, j[1].name, data.iloc[start - 1].Low) and (
#                 (data.loc[j[1].name].TR > data.loc[j[1].name].ATR)
#                 or (
#                     data.iloc[data.index.get_loc(j[1].name) + 1].TR
#                     > data.iloc[data.index.get_loc(j[1].name) + 1].ATR
#                 )
#             ):
#                 if j[1].name in RA.index:
#                     back = data.iloc[start - 1].name
#                     gen = data.loc[j[0] : back : -1].iterrows()
#                     # print(j[1].name)
#                     while True:
#                         try:
#                             k = next(gen)[0]
#                             if data.loc[k].Open < data.loc[k].Close:
#                                 # print(f"ORDER BLOCK: {k}")
#                                 order_block_min.append(k)
#                                 break

#                             else:
#                                 continue
#                         except StopIteration:
#                             # print('No OB Found for this fractal')
#                             break

#                     break

#     order_block_max = []
#     for i in range(1, len(a)):
#         start = data.iloc[a[i - 1]].name
#         start = data.index.get_loc(start) + 1
#         end = data.iloc[a[i]].name
#         end = data.index.get_loc(end) - 1

#         breakout_region = data.iloc[start:end].iterrows()
#         for j in breakout_region:
#             if cuts(data, j[1].name, data.iloc[start - 1].High) and (
#                 (data.loc[j[1].name].TR > data.loc[j[1].name].ATR)
#                 or (
#                     data.iloc[data.index.get_loc(j[1].name) + 1].TR
#                     > data.iloc[data.index.get_loc(j[1].name) + 1].ATR
#                 )
#             ):
#                 if j[1].name in RA.index:
#                     back = data.iloc[start - 1].name
#                     gen = data.loc[j[0] : back : -1].iterrows()
#                     # print(j[1].name)
#                     while True:
#                         try:
#                             k = next(gen)[0]
#                             if data.loc[k].Open > data.loc[k].Close:
#                                 # print(f"ORDER BLOCK: {k}")
#                                 order_block_max.append(k)
#                                 break

#                             else:
#                                 continue
#                         except StopIteration:
#                             # print('No OB Found for this fractal')
#                             break

#                     break

#     return order_block_min, order_block_max


# def order_block_detailed(data):
#     """Returns Min, Max Ob set, with [OB,Breakout]"""
#     a, b = pivots(data, 2)  # Pivotup#pivotdown
#     data["TR"] = true_range(data)
#     data["ATR"] = atr(data, 14)
#     data["ADX"] = adx(data, 14)
#     RA = rising_adx(data)

#     order_block_min = []
#     for i in range(1, len(b)):
#         start = data.iloc[b[i - 1]].name
#         start = data.index.get_loc(start) + 1
#         end = data.iloc[b[i]].name
#         end = data.index.get_loc(end) - 1

#         breakout_region = data.iloc[start:end].iterrows()
#         for j in breakout_region:
#             if cuts(data, j[1].name, data.iloc[start - 1].Low) and (
#                 (data.loc[j[1].name].TR > data.loc[j[1].name].ATR)
#                 or (
#                     data.iloc[data.index.get_loc(j[1].name) + 1].TR
#                     > data.iloc[data.index.get_loc(j[1].name) + 1].ATR
#                 )
#             ):
#                 if j[1].name in RA.index:
#                     back = data.iloc[start - 1].name
#                     gen = data.loc[j[0] : back : -1].iterrows()
#                     # print(j[1].name)
#                     while True:
#                         try:
#                             k = next(gen)[0]
#                             if data.loc[k].Open < data.loc[k].Close:
#                                 # print(f"ORDER BLOCK: {k}")
#                                 order_block_min.append([k, j[1].name])
#                                 break

#                             else:
#                                 continue
#                         except StopIteration:

#                             break

#                     break

#     order_block_max = []
#     for i in range(1, len(a)):
#         start = data.iloc[a[i - 1]].name
#         start = data.index.get_loc(start) + 1
#         end = data.iloc[a[i]].name
#         end = data.index.get_loc(end) - 1

#         breakout_region = data.iloc[start:end].iterrows()
#         for j in breakout_region:
#             if cuts(data, j[1].name, data.iloc[start - 1].High) and (
#                 (data.loc[j[1].name].TR > data.loc[j[1].name].ATR)
#                 or (
#                     data.iloc[data.index.get_loc(j[1].name) + 1].TR
#                     > data.iloc[data.index.get_loc(j[1].name) + 1].ATR
#                 )
#             ):
#                 if j[1].name in RA.index:
#                     back = data.iloc[start - 1].name
#                     gen = data.loc[j[0] : back : -1].iterrows()
#                     # print(j[1].name)
#                     while True:
#                         try:
#                             k = next(gen)[0]
#                             if data.loc[k].Open > data.loc[k].Close:
#                                 # print(f"ORDER BLOCK: {k}")
#                                 order_block_max.append([k, j[1].name])
#                                 break

#                             else:
#                                 continue
#                         except StopIteration:
#                             # print('No OB Found for this fractal')
#                             break

#                     break

#     return order_block_min, order_block_max


def pivot_point_standard(DF):
    df = DF.copy()

    df["P"] = df.eval("High + Low + Close") / 3
    df["R1"] = df.eval("P * 2 - Low")
    df["R2"] = df.eval("P +( High - Low)")
    df["S1"] = df.eval("(P*2) - High")
    df["S2"] = df.eval("P- (High - Low)")
    return df


def bolinger_bands(df, window_size, num_of_std):
    """(Dataframe,Windows_size,Sigma)
    Returns dataframe
    """

    stock_price = df.Close
    rolling_mean = stock_price.rolling(window=window_size).mean()
    rolling_std = stock_price.rolling(window=window_size).std()
    upper_band = rolling_mean + (rolling_std * num_of_std)
    lower_band = rolling_mean - (rolling_std * num_of_std)
    return rolling_mean, upper_band, lower_band


def keltner_channel(DF, period_ema, n_atr):
    """1.keltner channel:
    Keltner Channels have a middle line, also known as a basis, and upper and lower channel lines collectively referred to
    as the envelope.
    The formulas for each component are below.
    Middle Line (Basis) = EMA\\Upper Channel Line = EMA + 2 * ATR\\Lower Channel Line = EMA - 2 * ATR

    """
    df = DF.copy()
    df["ATR"] = atr(df, n_atr)
    EMA = ema(df.Close, period_ema)
    df["KC_UL"] = EMA + 2 * df["ATR"]
    df["KC_LL"] = EMA - 2 * df["ATR"]
    return df["KC_UL"], df["KC_LL"]


def donchian_channel(DF, n):
    """3.Donchian channel
    The Formula for Donchian Channels Is
    UC = Highest High in Last N Periods
    Middle Channel=((UC-LC)/2)
    LC = Lowest Low in Last N periods
    where:
    UC=Upper channel
    N=Number of minutes, hours, days, weeks,
     months
    Period=Minutes, hours, days, weeks, months
    LC=Lower channel
    How To Calculate Donchian Channels
    Channel High:
    Choose time period (N minutes/hours/days/weeks/months).
    Compare the high print for each minute, hour, day, week or month over that period.
    Choose the highest print.
    Plot the result.

    Channel Low:
    Choose time period (N minutes/hours/days/weeks/months).
    Compare the low print for each minute, hour, day, week or month over that period.
    Choose the lowest print.
    Plot the result.

    Center Channel:
    Choose time period (N minutes/hours/days/weeks/months).
    Compare high and low prints for each minute, hour, day, week or month over that period.
    Subtract the highest high print from lowest low print and divide by 2.
    Plot the result."""
    df = DF.copy()
    df["UC"] = df["High"].rolling(n).max()
    df["LC"] = df["Low"].rolling(n).min()
    df["MC"] = df.eval("(High - Low)/2")
    return df


def support_resistance_area(df):
    u, d = pivots(df, 2)
    fractals = _maxima(u, d, df) + _minima(d, u, df)
    x = df.loc[fractals][["High", "Low"]]
    X = x.reset_index(drop=True)
    inertia = []
    ss = []
    for i in range(2, 15):
        km = KMeans(n_clusters=i)
        km.fit(X)
        inertia.append(km.inertia_)
        ss.append(silhouette_score(X, km.labels_))
    kneedle = KneeLocator(
        list(range(2, 15)), inertia, direction="decreasing", curve="convex"
    )
    km = KMeans(n_clusters=list(kneedle.all_knees)[0])
    km.fit(X)
    # Sort by Volume Mean
    x = df.loc[fractals]
    x["label"] = km.labels_
    stat = x.groupby("label").mean()
    stat["C1"] = km.cluster_centers_[:, 0]
    stat["C2"] = km.cluster_centers_[:, 1]
    stat = stat.sort_values("Volume", ascending=False)
    return stat[["C1", "C2"]]


def support_resistance_lines(df):
    u, d = pivots(df, 2)
    fractals = _maxima(u, d, df) + _minima(d, u, df)
    df = df.loc[fractals][["High", "Low"]]
    df_c = df.copy(deep=True)
    df_c.columns = ["Open", "Low", "High", "Close", "Volume"]
    df_lines = df.append(df_c, ignore_index=False, sort=True)
    X = df_lines[["High", "Low"]]
    x = X.reset_index(drop=True)
    ss = []
    inertia = []
    for i in range(2, 11):
        km = KMeans(n_clusters=i)
        km.fit(x)
        inertia.append(km.inertia_)
        ss.append(silhouette_score(x, km.labels_))

    kneedle = KneeLocator(
        list(range(2, 11)), inertia, direction="decreasing", curve="convex"
    )
    km = KMeans(n_clusters=list(kneedle.all_knees)[0])
    km.fit(x)
    # Sort
    X = df_lines
    X["label"] = km.labels_
    stat = X.groupby("label").mean()
    stat["centre"] = km.cluster_centers_[:, 0]
    stat = stat.sort_values("Volume", ascending=False)
    return stat["centre"]


def support_resistance_dbscan_area(df):
    u, d = pivots(df, 2)
    fractals = _maxima(u, d, df) + _minima(d, u, df)
    points = df.loc[fractals]
    full = points.drop("Volume", axis=1)
    points = full[["High", "Low"]]
    points = points.drop_duplicates()
    # Finding Epsilon and K
    a = (points["High"] - points["Low"]).mean()
    e = round(a, 2)
    dbscan_opt = DBSCAN(eps=e, min_samples=3)
    dbscan_opt.fit(points)
    points["label"] = dbscan_opt.labels_
    new = points.iloc[dbscan_opt.core_sample_indices_].sort_values("label")

    return new


def support_resistance_dbscan_area_pivot(df):
    u, d = pivots(df, 2)
    # fractals = Maxima(u,d,df) + Minima(d,u,df)
    points = df.iloc[u + d]
    full = points.drop("Volume", axis=1)
    points = full[["High", "Low"]]
    points = points.drop_duplicates()
    # Finding Epsilon and K
    a = (points["High"] - points["Low"]).mean()
    e = round(a, 2)
    dbscan_opt = DBSCAN(eps=e, min_samples=3)
    dbscan_opt.fit(points)
    points["label"] = dbscan_opt.labels_
    new = points.iloc[dbscan_opt.core_sample_indices_].sort_values("label")

    return new.groupby("label").agg({"High": "max", "Low": "min"})


def support_resistance_pivots_lines(df):
    u, d = pivots(df, 2)
    dF = df.iloc[u + d]
    df_c = dF.copy(deep=True)
    df_c.columns = ["Open", "Low", "High", "Close", "Volume"]
    df_lines = df.append(df_c, ignore_index=False, sort=True)
    X = df_lines[["High", "Low"]]
    x = X.reset_index(drop=True)
    ss = []
    inertia = []
    for i in range(2, 11):
        km = KMeans(n_clusters=i)
        km.fit(x)
        inertia.append(km.inertia_)
        ss.append(silhouette_score(x, km.labels_))

    kneedle = KneeLocator(
        list(range(2, 11)), inertia, direction="decreasing", curve="convex"
    )
    km = KMeans(n_clusters=list(kneedle.all_knees)[0])
    km.fit(x)
    # Sort
    X = df_lines
    X["label"] = km.labels_
    stat = X.groupby("label").mean()
    stat["centre"] = km.cluster_centers_[:, 0]
    stat = stat.sort_values("Volume", ascending=False)
    return stat["centre"]


def support_resistance_pivots_area(df):
    u, d = pivots(df, 2)
    x = df.iloc[u + d][["High", "Low"]]
    X = x.reset_index(drop=True)
    inertia = []
    ss = []
    for i in range(2, 15):
        km = KMeans(n_clusters=i)
        km.fit(X)
        inertia.append(km.inertia_)
        ss.append(silhouette_score(X, km.labels_))
    kneedle = KneeLocator(
        list(range(2, 15)), inertia, direction="decreasing", curve="convex"
    )
    km = KMeans(n_clusters=list(kneedle.all_knees)[0])
    km.fit(X)
    # Sort by Volume Mean
    x = df.iloc[u + d]
    x["label"] = km.labels_
    stat = x.groupby("label").mean()
    stat["C1"] = km.cluster_centers_[:, 0]
    stat["C2"] = km.cluster_centers_[:, 1]
    stat = stat.sort_values("Volume", ascending=False)
    return stat[["C1", "C2"]]


def support_reistance_new_kmean(df):
    price = df.Close.iloc[-500:]
    max_idx = list(argrelextrema(price.values, np.greater, order=5)[0])
    min_idx = list(argrelextrema(price.values, np.less, order=5)[0])
    idx = max_idx + min_idx
    idx.sort()
    X = price[idx].reset_index(drop=True)
    X = X.to_numpy()
    X = X.reshape(-1, 1)
    inertia = []
    ss = []
    for i in range(2, 10):
        km = KMeans(n_clusters=i)
        km.fit(X)
        inertia.append(km.inertia_)
        ss.append(silhouette_score(X, km.labels_))
    kneedle = KneeLocator(
        list(range(2, 10)), inertia, direction="decreasing", curve="convex"
    )
    km = KMeans(n_clusters=list(kneedle.all_knees)[0])
    km.fit(X)
    data_idx = pd.DataFrame(price).iloc[idx]
    data_idx["label"] = km.labels_
    data_idx = data_idx.astype(float)
    stat = data_idx.groupby("label").mean()
    return stat.Close


def support_resistance_new_dbscan(df):
    e = df.iloc[-500:].eval("High - Low").mean()
    price = df.Close.iloc[-500:]
    max_idx = list(argrelextrema(price.values, np.greater, order=5)[0])
    min_idx = list(argrelextrema(price.values, np.less, order=5)[0])
    idx = max_idx + min_idx
    idx.sort()
    X = price[idx].reset_index(drop=True)
    X = X.to_numpy()
    X = X.reshape(-1, 1)

    dbscan_opt = DBSCAN(eps=e, min_samples=3)
    dbscan_opt.fit(X)
    data_idx = pd.DataFrame(price).iloc[idx]
    data_idx["labels"] = dbscan_opt.labels_
    lines = data_idx.groupby("labels").mean()
    return lines[lines.index >= 0].values


# def Pivots(df, i):
#     # Pivots for Day candle
#     def isSupport(df, i):
#         support = (
#             df["Low"][i] < df["Low"][i - 1]
#             and df["Low"][i] < df["Low"][i + 1]
#             and df["Low"][i] < df["Low"][i + 2]
#             and df["Low"][i] < df["Low"][i - 2]
#         )  # and df['TR'][i]>df['ATR'][i]

#         return support

#     def isResistance(df, i):
#         resistance = (
#             df["High"][i] > df["High"][i - 1]
#             and df["High"][i] > df["High"][i + 1]
#             and df["High"][i] > df["High"][i + 2]
#             and df["High"][i] > df["High"][i - 2]
#         )  # and df['TR'][i]>df['ATR'][i]

#         return resistance

#     pivot_down = []
#     pivot_up = []
#     for i in range(2, df.shape[0] - 2):
#         if isSupport(df, i):
#             # l = df_d['Low'][i]
#             pivot_down.append(i)
#         if isResistance(df, i):
#             # l = df_d['High'][i]
#             pivot_up.append(i)

#     return (pivot_up, pivot_down)

# def minima(pivot_down, pivot_up, df):
#     """Finds Down Fractals having"""
#     minima = []
#     for i in pivot_down:

#         for j in range(len(pivot_up) - 1):
#             if df.iloc[i].name == df.iloc[pivot_up[j]].name:
#                 if (df.iloc[pivot_up[j]].High < df.iloc[pivot_up[j + 1]].High) or (
#                     df.iloc[pivot_up[j - 1]].High < df.iloc[pivot_up[j]].High
#                 ):
#                     minima.append(df.iloc[i].name)

#             elif (df.iloc[i].name > df.iloc[pivot_up[j]].name) & (
#                 df.iloc[i].name <= df.iloc[pivot_up[j + 1]].name
#             ):

#                 if df.iloc[pivot_up[j + 1]].High > df.iloc[pivot_up[j]].High:
#                     minima.append(df.iloc[i].name)
#     return minima


# def maxima(pivot_up, pivot_down, df):
#     maxima = []
#     for i in pivot_up:

#         for j in range(len(pivot_down) - 1):
#             if df.iloc[i].name == df.iloc[pivot_down[j]].name:
#                 if (df.iloc[pivot_down[j]].Low > df.iloc[pivot_down[j + 1]].Low) or (
#                     df.iloc[pivot_down[j - 1]].Low > df.iloc[pivot_down[j]].Low
#                 ):
#                     maxima.append(df.iloc[i].name)
#             elif (df.iloc[i].name > df.iloc[pivot_down[j]].name) and (
#                 df.iloc[i].name < df.iloc[pivot_down[j + 1]].name
#             ):
#                 if df.iloc[pivot_down[j]].Low > df.iloc[pivot_down[j + 1]].Low:
#                     maxima.append(df.iloc[i].name)
#     return maxima

# def Minima(pivot_down, pivot_up, df):
#     """Finds Down Fractals having"""
#     minima = []
#     for i in pivot_down:

#         for j in range(len(pivot_up) - 1):
#             if df.iloc[i].name == df.iloc[pivot_up[j]].name:
#                 if (df.iloc[pivot_up[j]].High < df.iloc[pivot_up[j + 1]].High) or (
#                     df.iloc[pivot_up[j - 1]].High < df.iloc[pivot_up[j]].High
#                 ):
#                     minima.append(df.iloc[i].name)

#             elif (df.iloc[i].name > df.iloc[pivot_up[j]].name) & (
#                 df.iloc[i].name <= df.iloc[pivot_up[j + 1]].name
#             ):

#                 if df.iloc[pivot_up[j + 1]].High > df.iloc[pivot_up[j]].High:
#                     minima.append(df.iloc[i].name)
#     return minima


# def _maxima(pivot_up, pivot_down, df):
#     maxima = []
#     for i in pivot_up:

#         for j in range(len(pivot_down) - 1):
#             if df.iloc[i].name == df.iloc[pivot_down[j]].name:
#                 if (df.iloc[pivot_down[j]].Low > df.iloc[pivot_down[j + 1]].Low) or (
#                     df.iloc[pivot_down[j - 1]].Low > df.iloc[pivot_down[j]].Low
#                 ):
#                     maxima.append(df.iloc[i].name)
#             elif (df.iloc[i].name > df.iloc[pivot_down[j]].name) and (
#                 df.iloc[i].name < df.iloc[pivot_down[j + 1]].name
#             ):
#                 if df.iloc[pivot_down[j]].Low > df.iloc[pivot_down[j + 1]].Low:
#                     maxima.append(df.iloc[i].name)

#     return maxima
