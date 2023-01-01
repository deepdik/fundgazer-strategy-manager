import numpy as np
import pandas as pd
from api.utils.strategy_logics.packages.indicators.filters import roc
from api.utils.strategy_logics.packages.helper.helper import true_range


def stochastic(df, n):
    """
    Args:
        df (pd.DataFrame): Data symbol
        n (Int): parameter

    Returns: pd.Series
    """
    df_c = df.copy(deep=True)
    df_c["L14"] = df_c["Low"].rolling(window=n).min()
    df_c["H14"] = df_c["High"].rolling(window=n).max()
    df_c["ST"] = 100 * ((df_c["Close"] - df_c["L14"]) / (df_c["H14"] - df_c["L14"]))
    # df_c['%D'] = df_c['ST'].rolling(window=3).mean()
    return df_c["ST"]


def rsi(df, n):
    """
    Args:
        df (pd.DataFrame): Data symbol
        n (Int): period

    Returns: pd.Series
    """
    delta = df["Close"].diff().dropna()
    u = delta * 0
    d = u.copy()
    u[delta > 0] = delta[delta > 0]
    d[delta < 0] = -delta[delta < 0]
    u[u.index[n - 1]] = np.mean(u[:n])  # first value is average of gains
    u = u.drop(u.index[: (n - 1)])
    d[d.index[n - 1]] = np.mean(d[:n])  # first value is average of losses
    d = d.drop(d.index[: (n - 1)])
    rs = u.ewm(com=n - 1, min_periods=n).mean() / d.ewm(com=n - 1, min_periods=n).mean()
    return 100 - 100 / (1 + rs)


def crsi(df, rsiLength, updownLength, rocLength):
    """Connor Rsi

    Args:
        df (pd.DataFrame): Data Symbol
        rsiLength (Int): period rsi
        updownLength (Int): parameter rsi
        rocLength (Int): period roc

    Returns: pd.Series
    """
    rsi_rsiLength = rsi(df, rsiLength)
    rsi_updownLength = rsi(df, updownLength)
    roc_series = roc(df, rocLength)
    cummRSI = (rsi_rsiLength + rsi_updownLength + roc_series) / 3
    return cummRSI


def cci(Df, period):
    """Commodity channel index

    Args:
        Df (Int): pd.DataFrame
        period (Int): period

    Returns: pd.Series
    """
    df = Df.copy()
    LambertsConstant = 0.015
    high = df["High"]
    low = df["Low"]
    close = df["Close"]

    TP = (high + low + close) / 3
    SMA = TP.rolling(period).mean()
    MAD = TP.rolling(period).apply(lambda x: pd.Series(x).mad())
    df["CCI"] = (TP - SMA) / (LambertsConstant * MAD)
    return df["CCI"]


def william_percentage_R(df, period):
    """William percentage R

    Args:
        df (pd.DataFrame): Data Symbol
        period (Int): period

    Returns: pd.Series
    """
    return -(df["High"].rolling(period).max() - df["Close"]) / (
        df["High"].rolling(period).max() - df["Low"].rolling(period).min()
    )


def ultimate_oscilator(Df):
    """Ultimate Oscilator

    Args:
        Df (pd.DataFrame): Data Symbol

    Returns: pd.Series
    """
    df = Df.copy()
    df["BP"] = buying_pressure(df)
    df["TR"] = true_range(df)
    df["A7"] = df["BP"].rolling(7).sum() / df["TR"].rolling(7).sum()
    df["A14"] = df["BP"].rolling(14).sum() / df["TR"].rolling(14).sum()
    df["A28"] = df["BP"].rolling(28).sum() / df["TR"].rolling(28).sum()
    df["UO"] = ((4 * df["A7"]) + (2 * df["A14"]) + df["A28"]) * 100 / 7
    return df["UO"]


def mfi(df, period):
    """Money Flow Index

    Args:
        df (pd.DataFrame): Data
        period (Int): period

    Returns: np.array
    """
    typical_price = (df.Close + df.High + df.Low) / 3
    money_flow = typical_price * df.Volume
    # Get all of the positive and negative money flow
    positive_flow = []
    negative_flow = []
    # Loop through typical price calculations
    for i in range(1, len(typical_price)):
        if typical_price[i] > typical_price[i - 1]:
            positive_flow.append(money_flow[i - 1])
            negative_flow.append(0)
        elif typical_price[i] < typical_price[i - 1]:
            negative_flow.append(money_flow[i - 1])
            positive_flow.append(0)
        else:
            positive_flow.append(0)
            negative_flow.append(0)
    # Storage for the last period days
    positive_mf = []
    negative_mf = []
    for i in range(period - 1, len(positive_flow)):
        positive_mf.append(sum(positive_flow[i + 1 - period : i + 1]))
    for i in range(period - 1, len(negative_flow)):
        negative_mf.append(sum(negative_flow[i + 1 - period : i + 1]))
    # Calculate the money flow index
    MFI = 100 * (
        np.array(positive_mf) / (np.array(positive_mf) + np.array(negative_mf))
    )
    empty = pd.Series(index=df.index)
    empty.iloc[period:] = MFI
    return empty


def awesome_oscillator(df):
    """Awesome Oscillator

    Args:
        df (pd.DataFrame): Data

    Returns: pd.Series
    """
    sma5 = df["Close"].rolling(5).mean()
    sma34 = df["Close"].rolling(34).mean()
    return sma5 - sma34


def acceleration_oscillator(df):
    """Acceleration Oscillator

    Args:
        df (pd.DataFrame): Data

    Returns: pd.Series
    """
    AO = awesome_oscillator(df)
    sma5 = AO.rolling(5).mean()
    acc_Osc = AO - sma5
    return acc_Osc


def stress(df1, df2, period):
    """Stress for pair trading

    Args:
        df1 (pd.DataFrame): Data Symbol 1
        df2 (pd.DataFrame): Data Symbol 2
        period (Int): period

    Returns: pd.Series
    """
    raw_leg1 = (df1["Close"][-1] - df1["Low"][-period]) / (
        df1["High"][-period] - df1["Low"][-period]
    )
    raw_leg2 = (df2["Close"][-1] - df2["Low"][-period]) / (
        df2["High"][-period] - df2["Low"][-period]
    )

    diff = raw_leg1 - raw_leg2
    low_diff = df1["Low"] - df2["Low"]
    high_diff = df1["High"] - df2["High"]
    stress = (diff - low_diff[-period]) / (high_diff[-period] - low_diff[-period])
    return stress


def buying_pressure(DF):
    """Buying Pressure

    Args:
        DF (pd.DataFrame): Data Symbol

    Returns: pd.Series
    """
    df = DF.copy()
    df["C-L"] = df["Close"] - df["Low"]
    df["C-PC"] = df["Close"] - df["Close"].shift(1)
    df["BP"] = df[["C-L", "C-PC"]].max(axis=1, skipna=False)
    return df["BP"]
