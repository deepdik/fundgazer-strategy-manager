from api.utils.strategy_logics.port.mpt_scoring_conditions import (
    adx_ema_condition,
    atr_ema_condition,
    calculate_median_std,
    ema_condition,
    fractal_condition,
    long_rsi_condition,
    obv_ema_condition,
    rising_adx_condition,
    short_rsi_condition,
    standard_deviation_condition,
    standard_deviation_negetive_condition,
    # relative_strength_with_index,
)

import numpy as np


def filtering_by_conditions(filtered_stocks, data, condition_type):
    condition_scores = {}
    for symbol in filtered_stocks:
        score = 0
        # pattern=pattern_pre_loaded(symbol,data,nDays=10)
        # score+=pattern.pattern_condition(trend=condition_type)
        score += ema_condition(symbol, data, period_ema=20, trend=condition_type)
        score += ema_condition(symbol, data, period_ema=50, trend=condition_type)
        score += rising_adx_condition(
            symbol, data, period_adx=14, rising_period=5, trend=condition_type
        )
        score += adx_ema_condition(
            symbol, data, period_adx=14, period_ema=20, trend=condition_type
        )
        score += obv_ema_condition(symbol, data, period_ema=20, trend=condition_type)
        score += long_rsi_condition(symbol, data, period_rsi=14, trend=condition_type)
        score += short_rsi_condition(symbol, data, period_rsi=3, trend=condition_type)
        median_std = calculate_median_std(filtered_stocks, data)
        score += standard_deviation_condition(
            symbol, data, median_std, trend=condition_type
        )
        score += standard_deviation_negetive_condition(
            symbol, data, median_std, trend=condition_type
        )
        score += atr_ema_condition(
            symbol, data, period_atr=14, period_ema=20, trend=condition_type
        )
        #     score += relative_strength_with_index(symbol, data, 20, index_price,trend=condition_type)
        score += fractal_condition(symbol, data, trend=condition_type)

        condition_scores[symbol] = score
    x = np.median(list(condition_scores.values()))
    return [k for k, v in condition_scores.items() if v >= x]
