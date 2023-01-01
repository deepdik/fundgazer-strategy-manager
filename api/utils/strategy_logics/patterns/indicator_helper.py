# from utils.utils import get_indicator_name_map
from api.utils.strategy_logics.packages.helper.helper import atr, true_range
from api.utils.strategy_logics.packages.indicators.momentum import (
    william_percentage_R,
    cci,
    crsi,
    mfi,
    rsi,
    awesome_oscillator,
    acceleration_oscillator,
    ultimate_oscilator,
    stochastic,
)
from api.utils.strategy_logics.packages.indicators.trend_indicators import (
    ema,
    adx,
    sma,
    choppiness_index,
    ravi,
    trix,
)
from api.utils.strategy_logics.packages.indicators.volume import (
    accumulation_distribution,
    obv,
    stochastic_volume,
    volume_oscillator,
)
from api.utils.strategy_logics.packages.indicators.support_resistance import (
    bolinger_bands,
    find_maxima,
    find_minima,
    keltner_channel,
    order_block_full,
)

INDICATORS_NAME_MAPPING = {
    "mfi": "MFI",
    "stochastic_volume": "STOCHASTIC_VOLUME",
    "ema": "EMA",
    "sma": "SMA",
    "awesome_oscillator": "AO",
    "ultimate_oscilator": "UO",
    "trix": "TRIX",
    "accumulation_distribution": "AD",
    "atr": "ATR",
    "true_range": "TR",
    "bolinger_bands": ["BB_M", "BB_U", "BB_L"],
    "stochastic": "STOCHASTIC",
    "acceleration_oscillator": "AC",
    "obv": "OBV",
    "cci": "CCI",
    "volume_oscillator": "VOLUME_OSCILLATOR",
    "adx": "ADX",
    "ravi": "RAVI",
    "rsi": "RSI",
    "choppiness_index": "CHOPPINESS_INDEX",
    "keltner_channel": ["KC_UL", "KC_LL"],
    "william_percentage_R": "WILLIAM_PERCENTAGE",
    "crsi": "CRSI",
}


ALL_INDICATOR_FUNC_LIST = [
    atr,
    true_range,
    william_percentage_R,
    cci,
    crsi,
    mfi,
    rsi,
    awesome_oscillator,
    acceleration_oscillator,
    ultimate_oscilator,
    stochastic,
    ema,
    adx,
    sma,
    choppiness_index,
    ravi,
    trix,
    accumulation_distribution,
    obv,
    stochastic_volume,
    volume_oscillator,
    bolinger_bands,
    keltner_channel,
]


def run_indicators(df, indicator_func_name, indicator_params_dict):
    if indicator_func_name == "ultimate_pattern_param":
        return df

    func_found = False
    for indicator_func in ALL_INDICATOR_FUNC_LIST:
        if indicator_func.__qualname__ == indicator_func_name:
            col_name = INDICATORS_NAME_MAPPING.get(indicator_func.__qualname__)
            # col_name = get_indicator_name_map(indicator_func.__qualname__)
            value = indicator_func(df, **indicator_params_dict)
            if isinstance(col_name, list):
                for num, col in enumerate(col_name):
                    df[col] = value[num]
                func_found = True
            else:
                df[col_name] = value
                func_found = True
            break
    if not func_found:
        raise Exception(f"Indicator function not found by name: {indicator_func_name}")
    return df


def run_ultimate_pattern_param(df, indicator_func_name, indicator_params_dict):
    if (
        indicator_func_name == "ultimate_pattern_param"
        and "n" in indicator_params_dict
        and indicator_params_dict["n"]
    ):
        n = indicator_params_dict["n"]
        df.loc[find_maxima(df, n).index, "Up_Fractal"] = True
        df.loc[find_minima(df, n).index, "Down_Fractal"] = True
        df_down = df[df.Down_Fractal == True]
        df_up = df[df.Up_Fractal == True]
        ob = order_block_full(df)
        df.loc[ob[0], "Ob_green"] = True
        df.loc[ob[1], "Ob_red"] = True

        for i in range(2, len(df_down)):
            if df_down.iloc[i].Low < df_down.iloc[i - 1].Low:
                df.loc[df_down.iloc[i].name, "L1"] = True
                df.loc[df_down.iloc[i].name, "L2"] = df_down.iloc[i - 1].name

        for i in range(2, len(df_up)):
            if df_up.iloc[i].High > df_up.iloc[i - 1].High:
                df.loc[df_up.iloc[i].name, "H1"] = True
                df.loc[df_up.iloc[i].name, "H2"] = df_up.iloc[i - 1].name
        df["bullish_gartley"] = False
        df["bearish_gartley"] = False
        df["bullish_crab"] = False
        df["bearish_crab"] = False
        df["bullish_butterfly"] = False
        df["bearish_butterfly"] = False
        df["bullish_cypher"] = False
        df["bearish_cypher"] = False

    return df
