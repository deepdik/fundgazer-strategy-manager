# from Packages.indicators.support_resistance import (
#     find_maxima,
#     find_minima,
#     order_block_full,
# )


def bull_gap(df):
    return df.High.iloc[-2] < df.Open.iloc[-1] and df.High.iloc[-2] < df.Low.iloc[-1]


def bear_gap(df):
    return df.Low.iloc[-2] > df.Open.iloc[-1] and df.Low.iloc[-2] > df.High.iloc[-1]


def atr(DF, n):
    """function to calculate Average True Range
    DataFrame,Period(mostly 14)
    returns Series ATR"""
    df = DF.copy()
    df["H-L"] = abs(df["High"] - df["Low"])
    df["H-PC"] = abs(df["High"] - df["Close"].shift(1))
    df["L-PC"] = abs(df["Low"] - df["Close"].shift(1))
    df["TR"] = df[["H-L", "H-PC", "L-PC"]].max(axis=1, skipna=False)
    # df['ATR'] = df['TR'].ewm(com=n,min_periods=n).mean()
    df["ATR"] = df["TR"].rolling(n).mean()
    return df["ATR"]


def true_range(DF):
    """function to calculate true Range
    Dataframe,Period
    returns Series TR"""
    df = DF.copy()
    df["H-L"] = abs(df["High"] - df["Low"])
    df["H-PC"] = abs(df["High"] - df["Close"].shift(1))
    df["L-PC"] = abs(df["Low"] - df["Close"].shift(1))
    df["TR"] = df[["H-L", "H-PC", "L-PC"]].max(axis=1, skipna=False)
    return df["TR"]


def cuts(df_d, x, price):
    """Tells whether a candle cuts a price or Not
    (dataframe, point in index(date), price)
    returns Bool"""
    if (df_d.loc[x, "High"] > price) and (df_d.loc[x, "Low"] < price):
        return True
    elif (
        bear_gap(df_d.loc[:x])
        and (price < df_d.loc[:x, "Low"].iloc[-2])
        and (price > df_d.loc[:x, "High"].iloc[-1])
    ):
        return True
    elif (
        bull_gap(df_d.loc[:x])
        and (price > df_d.loc[:x, "High"].iloc[-2])
        and (price < df_d.loc[:x, "Low"].iloc[-1])
    ):
        return True
    else:
        return False


# def setup_ul(df, n=2):
#     """Run to generate all L1,H1 and orderblock values for enitre data,
#     at the start

#     Args:
#         df (pd.DataFrame): All Data
#         n (int, optional): fractal parameter. Defaults to 2.

#     Returns:
#         pd.DataFrame: data containing all the values as new columns
#     """
#     df.loc[find_maxima(df, n).index, "Up_Fractal"] = True
#     df.loc[find_minima(df, n).index, "Down_Fractal"] = True
#     df_down = df[df.Down_Fractal == True]
#     df_up = df[df.Up_Fractal == True]
#     ob = order_block_full(df)
#     df.loc[ob[0], "Ob_green"] = True
#     df.loc[ob[1], "Ob_red"] = True
#     for i in range(2, len(df_down)):
#         if df_down.iloc[i].Low < df_down.iloc[i - 1].Low:
#             df.loc[df_down.iloc[i].name, "L1"] = True
#             df.loc[df_down.iloc[i].name, "L2"] = df_down.iloc[i - 1].name
#     for i in range(2, len(df_up)):
#         if df_up.iloc[i].High > df_up.iloc[i - 1].High:
#             df.loc[df_up.iloc[i].name, "H1"] = True
#             df.loc[df_up.iloc[i].name, "H2"] = df_up.iloc[i - 1].name
#     return df
