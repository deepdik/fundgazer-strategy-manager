import numpy as np
import pandas as pd
from queue import deque
from api.utils.strategy_logics.packages.helper.helper import atr, true_range


def psar(barsdata, iaf=0.02, maxaf=0.2):
    """Parabolic SAR

    Args:
        barsdata (pd.DataFrame): Data Symbol
        iaf (float, optional): _description_. Defaults to 0.02.
        maxaf (float, optional): _description_. Defaults to 0.2.

    Returns:
        pd.DataFrame: Three Columns psar, psa_bear, psar_bull
    """
    length = len(barsdata)
    dates = list(barsdata.index)
    high = list(barsdata["High"])
    low = list(barsdata["Low"])
    close = list(barsdata["Close"])
    psar = close[0 : len(close)]
    psarbull = [None] * length
    psarbear = [None] * length
    bull = True
    af = iaf
    ep = low[0]
    hp = high[0]
    lp = low[0]
    for i in range(2, length):
        if bull:
            psar[i] = psar[i - 1] + af * (hp - psar[i - 1])
        else:
            psar[i] = psar[i - 1] + af * (lp - psar[i - 1])
        reverse = False
        if bull:
            if low[i] < psar[i]:
                bull = False
                reverse = True
                psar[i] = hp
                lp = low[i]
                af = iaf
        else:
            if high[i] > psar[i]:
                bull = True
                reverse = True
                psar[i] = lp
                hp = high[i]
                af = iaf
        if not reverse:
            if bull:
                if high[i] > hp:
                    hp = high[i]
                    af = min(af + iaf, maxaf)
                if low[i - 1] < psar[i]:
                    psar[i] = low[i - 1]
                if low[i - 2] < psar[i]:
                    psar[i] = low[i - 2]
            else:
                if low[i] < lp:
                    lp = low[i]
                    af = min(af + iaf, maxaf)
                if high[i - 1] > psar[i]:
                    psar[i] = high[i - 1]
                if high[i - 2] > psar[i]:
                    psar[i] = high[i - 2]
        if bull:
            psarbull[i] = psar[i]
        else:
            psarbear[i] = psar[i]
        psar_dict = {
            "dates": dates,
            "high": high,
            "low": low,
            "close": close,
            "psar": psar,
            "psar_bear": psarbear,
            "psar_bull": psarbull,
        }
        return pd.DataFrame(psar_dict).set_index("dates")


def ema(series, period):
    """Exponential moving average

    Args:
        series (pd.Series): Close series
        period (Int): period

    Returns: pd.Series
    """
    if isinstance(series, pd.DataFrame):
        s = series.Close
    else:
        s = series
    span = period
    sma_series = s.rolling(window=span, min_periods=span).mean()[:span]
    rest = s[span:]
    return pd.concat([sma_series, rest]).ewm(span=span, adjust=False).mean()


def sma(series, period):
    """Simple moving average

    Args:
        series (pd.Series): Close of symbol
        period (Int): period

    Returns: pd.Series
    """
    if isinstance(series, pd.DataFrame):
        s = series.Close
    else:
        s = series
    return s.rolling(window=period).mean()


def hma(df, lookbackPeriod=20):
    """Hull moving average

    Args:
        df (pd.DataFrame): Data of symbol
        lookbackPeriod (int, optional): period, Defaults to 20.

    Returns: pd.Series
    """
    wma1 = wma(df["Close"], lookbackPeriod)
    wma2 = wma(df["Close"], lookbackPeriod // 2)
    result = 2 * wma2 - wma1
    hullMovingAvg = wma(result, int(np.sqrt(lookbackPeriod)))
    return hullMovingAvg


def wma(close_series, n=20):
    """Weighted moving average

    Args:
        close_series (pd.Series): Close of Symbol
        n (int, optional): period, Defaults to 20.

    Returns: pd.Series
    """
    weights = np.arange(1, n + 1)
    wmas = close_series.rolling(n).apply(
        lambda x: np.dot(x, weights) / weights.sum(), raw=True
    )
    return wmas


def SuperTrend(df, period=14, multiplier=3):
    """Supertrend

    Args:
        df (pd.DataFrame): Data of symbol
        period (Int): period of rsi
        multiplier (float): multiplier of atr

    Returns:
        tuple: (pd.Series, pd.Series)
    """
    ATR = atr(df, period)
    upper_line = (df["High"] + df["Low"]) / 2 + multiplier * ATR
    lower_line = (df["High"] + df["Low"]) / 2 - multiplier * ATR
    return upper_line, lower_line


def ichimoku(df):
    """Ichimoku Cloud

    Args:
        df (pd.DataFrame): Data Symbol

    Returns:
        pd.DataFrame: containing additional columns(tenkan_sen,kijun_sen,senkou_span_a,senkou_span_b,chikou_span)
    """
    df = df.copy(deep=True)
    nine_period_high = df["High"].rolling(window=9).max()
    nine_period_low = df["Low"].rolling(window=9).min()

    df["tenkan_sen"] = (nine_period_high + nine_period_low) / 2

    # Kijun-sen (Base Line): (26-period high + 26-period low)/2))
    period26_high = df["High"].rolling(window=26).max()
    period26_low = df["Low"].rolling(window=26).min()

    df["kijun_sen"] = (period26_high + period26_low) / 2

    # Senkou Span A (Leading Span A): (Conversion Line + Base Line)/2))
    df["senkou_span_a"] = ((df["tenkan_sen"] + df["kijun_sen"]) / 2).shift(26)

    # Senkou Span B (Leading Span B): (52-period high + 52-period low)/2))
    period52_high = df["High"].rolling(window=52).max()
    period52_low = df["Low"].rolling(window=52).min()

    df["senkou_span_b"] = ((period52_high + period52_low) / 2).shift(26)

    # The most current closing price plotted 22 time periods behind (optional)
    df["chikou_span"] = df["Close"].shift(-22)  # 22 according to investopedia

    return df


def adx(DF, n=14):
    """Adx

    Args:
        DF (pd.DataFrame): Data Symbol
        n (Int, optional): period ,defaults to 14

    Returns: pd.Series
    """
    df2 = DF.copy(deep=True)
    df2["H-L"] = abs(df2["High"] - df2["Low"])
    df2["H-PC"] = abs(df2["High"] - df2["Close"].shift(1))
    df2["L-PC"] = abs(df2["Low"] - df2["Close"].shift(1))
    df2["TR"] = df2[["H-L", "H-PC", "L-PC"]].max(axis=1, skipna=False)
    df2["DMplus"] = np.where(
        (df2["High"] - df2["High"].shift(1)) > (df2["Low"].shift(1) - df2["Low"]),
        df2["High"] - df2["High"].shift(1),
        0,
    )
    df2["DMplus"] = np.where(df2["DMplus"] < 0, 0, df2["DMplus"])
    df2["DMminus"] = np.where(
        (df2["Low"].shift(1) - df2["Low"]) > (df2["High"] - df2["High"].shift(1)),
        df2["Low"].shift(1) - df2["Low"],
        0,
    )
    df2["DMminus"] = np.where(df2["DMminus"] < 0, 0, df2["DMminus"])
    TRn = []
    DMplusN = []
    DMminusN = []
    TR = df2["TR"].tolist()
    DMplus = df2["DMplus"].tolist()
    DMminus = df2["DMminus"].tolist()
    for i in range(len(df2)):
        if i < n:
            TRn.append(np.NaN)
            DMplusN.append(np.NaN)
            DMminusN.append(np.NaN)
        elif i == n:
            TRn.append(df2["TR"].rolling(n).sum().tolist()[n])
            DMplusN.append(df2["DMplus"].rolling(n).sum().tolist()[n])
            DMminusN.append(df2["DMminus"].rolling(n).sum().tolist()[n])
        elif i > n:
            TRn.append(TRn[i - 1] - (TRn[i - 1] / n) + TR[i])
            DMplusN.append(DMplusN[i - 1] - (DMplusN[i - 1] / n) + DMplus[i])
            DMminusN.append(DMminusN[i - 1] - (DMminusN[i - 1] / n) + DMminus[i])
    df2["TRn"] = np.array(TRn)
    df2["DMplusN"] = np.array(DMplusN)
    df2["DMminusN"] = np.array(DMminusN)
    df2["DIplusN"] = 100 * (df2["DMplusN"] / df2["TRn"])
    df2["DIminusN"] = 100 * (df2["DMminusN"] / df2["TRn"])
    df2["DIdiff"] = abs(df2["DIplusN"] - df2["DIminusN"])
    df2["DIsum"] = df2["DIplusN"] + df2["DIminusN"]
    df2["DX"] = 100 * (df2["DIdiff"] / df2["DIsum"])
    ADX = []
    DX = df2["DX"].tolist()
    for j in range(len(df2)):
        if j < 2 * n - 1:
            ADX.append(np.NaN)
        elif j == 2 * n - 1:
            ADX.append(df2["DX"][j - n + 1 : j + 1].mean())
        elif j > 2 * n - 1:
            ADX.append(((n - 1) * ADX[j - 1] + DX[j]) / n)
    df2["ADX"] = np.array(ADX)
    return df2["ADX"]


def adoptive_ma_with_volatility(df, period=14):
    """Adoptive Moving Average with Volatility

    Args:
        df (pd.DataFrame): Data of Symbol
        period (int, optional): period, Defaults to 14.

    Returns: pd.Series
    """
    # M.A * ATR/TRUE RANGE
    MA = df["Close"].rolling(period).mean()
    ATR = atr(df, period)
    TR = true_range(df)
    mean = (ATR / TR).rolling(period).mean()
    return MA * mean


def ravi(d):
    """RAVI

    Args:
        d (pd.DataFrame): Data Symbol

    Returns:
        pd.DataFrame : containing three columns(MA_H, MA_L, RAVI)
    """
    d = d.copy(deep=True)
    d["MA_H"] = d["Close"].rolling(65).mean()
    d["MA_L"] = d["Close"].rolling(7).mean()
    d["RAVI"] = (abs(d["MA_L"] - d["MA_H"]) / d["MA_H"]) * 100
    return d["RAVI"]


def rising_adx(df):
    """Dataframe having adx column
    returns subset of input Dataframe"""
    radx = []
    for i in range(len(df)):
        if i > 50:
            if df.iloc[i].ADX > df.iloc[i - 10].ADX:
                radx.append(df.iloc[i].name)

    RA = df.loc[radx]
    return RA


def trix(data, period):
    """TRIX

    Args:
        data (pd.DataFrame): Data Symbol
        period (Int): Period of Ema

    Returns: pd.Series
    """
    ema1 = ema(data["Close"], period)
    ema2 = ema(ema1, period)
    ema3 = ema(ema2, period)

    return 10000 * (ema3 - ema3.shift()) / ema3.shift()


# def choppiness_Index(df, period):
#      return (100 * math.log((atr(df, 1)[-period:].sum() / (df['High'][-period:].max() - df['Low'][-period:].min())), 10) / math.log(period))


def choppiness_index(candlestick, tp):
    """Choppiness Index

    Args:
        candlestick (pd.DataFrame): Data Symbol
        tp (Int): period

    Returns: pd.Series
    """
    high = candlestick["High"]
    low = candlestick["Low"]
    # close = candlestick["Close"]
    ATR = atr(candlestick, tp)
    Timestamp = deque()
    CP = deque()
    for i in range(len(candlestick)):
        if i < tp * 2:
            Timestamp.append(candlestick.index[i])
            CP.append(0)
        else:
            nmrt = np.log10(
                np.sum(ATR[i - tp : i]) / (max(high[i - tp : i]) - min(low[i - tp : i]))
            )
            dnmnt = np.log10(tp)
            Timestamp.append(candlestick.index[i])
            CP.append(round(100 * nmrt / dnmnt))
    CP = pd.DataFrame({"CP": CP}, index=Timestamp)
    return CP.CP.shift(-1)
