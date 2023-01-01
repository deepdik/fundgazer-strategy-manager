import numpy as np


def volume_oscillator(df):
    """Volume Oscillator

    Args:
        df (pd.DataFrame): Data symbol

    Returns: pd.Series
    """

    sma5 = df["Volume"].rolling(5).mean()
    sma34 = df["Volume"].rolling(34).mean()

    VO = 100 * ((sma5 - sma34) / sma34)
    return VO


def obv(Df):
    """On-Balance Volume

    Args:
        Df (pd.DataFrame): Data Symbol

    Returns: pd.Series
    """
    df = Df.copy()
    df["OBV"] = np.where(
        df["Close"] > df["Close"].shift(1),
        df["Volume"],
        np.where(df["Close"] < df["Close"].shift(1), -df["Volume"], 0),
    ).cumsum()

    return df["OBV"]


def accumulation_distribution(Df):
    """Accumulation Distribution

    Args:
        Df (pd.DataFrame): Data symbol

    Returns: pd.Series
    """
    df = Df.copy()
    MFM = ((df["Close"] - df["Low"]) - (df["High"] - df["Close"])) / (
        df["High"] - df["Low"]
    )
    MFV = MFM * df["Volume"]
    df["A/D"] = MFV.rolling(2).sum()
    df["A/D"][0] = MFV[0]
    return df["A/D"]


def stochastic_volume(df, n):
    """Stochastic Volume

    Args:
        df (pd.DataFrame): Data
        n (Int): period

    Returns: pd.Series
    """
    df_c = df.copy(deep=True)
    df_c["VOL_L14"] = df_c["Volume"].rolling(window=n).min()
    df_c["VOL_H14"] = df_c["Volume"].rolling(window=n).max()
    n = df_c["Volume"] - df_c["VOL_L14"]
    d = df_c["VOL_H14"] - df_c["VOL_L14"]
    # df_c['%D'] = df_c['%K'].rolling(window=3).mean()
    return 100 * (n / d)