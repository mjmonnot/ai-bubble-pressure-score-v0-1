# src/aibps/normalize.py
"""
Normalization utilities for AIBPS pillars.

All functions take a pandas Series and return a Series aligned to the
original index, generally scaled to a 0–100 range (when appropriate).

Key methods:
- expanding_percentile: percentile vs ENTIRE past history (can saturate).
- rolling_percentile: percentile vs a ROLLING window.
- rolling_z: rolling z-score (abnormality vs recent mean).
- sigmoid_z: rolling z-score passed through a logistic to get 0–100.
- minmax_scale_0_100: simple min-max scaling to 0–100.

Use `normalize_series(series, method=..., **kwargs)` as the main entry point.
"""

from __future__ import annotations

from typing import Literal

import numpy as np
import pandas as pd


def _align_output(orig: pd.Series, core: pd.Series) -> pd.Series:
    """
    Take an original Series and a computed Series (on non-null subset),
    and return a full Series aligned to the original index.
    """
    out = pd.Series(np.nan, index=orig.index, dtype="float64")
    out.loc[core.index] = core.astype(float)
    return out


def expanding_percentile(series: pd.Series) -> pd.Series:
    """
    Percentile of each value vs. all previous non-null values, scaled 0–100.

    Interpretation:
        0  = lower than anything seen before
        100= highest value seen so far

    This can saturate near 100 when the underlying series trends upward.
    """
    s = series.dropna()
    if s.empty:
        return series.astype(float) * np.nan

    vals = []
    idxs = []
    for i in range(len(s)):
        window = s.iloc[: i + 1]
        pct = window.rank(pct=True).iloc[-1] * 100.0
        vals.append(float(pct))
        idxs.append(s.index[i])

    core = pd.Series(vals, index=idxs)
    core = core.clip(0.0, 100.0)
    return _align_output(series, core)


def rolling_percentile(series: pd.Series, window: int = 60, min_periods: int | None = None) -> pd.Series:
    """
    Percentile of each value vs. a rolling window of past values, scaled 0–100.

    Interpretation:
        "How extreme is the current value vs. the recent window?"
    """
    s = series.dropna()
    if s.empty:
        return series.astype(float) * np.nan

    if min_periods is None:
        min_periods = max(10, window // 4)

    def _rank_last(x):
        xx = pd.Series(x)
        return float(xx.rank(pct=True).iloc[-1] * 100.0)

    core = s.rolling(window=window, min_periods=min_periods).apply(_rank_last, raw=False)
    core = core.clip(0.0, 100.0)
    return _align_output(series, core)


def rolling_z(series: pd.Series, window: int = 24, min_periods: int | None = None) -> pd.Series:
    """
    Rolling z-score: (x_t - mean_{t-window}) / std_{t-window}.

    Interpretation:
        "How many standard deviations away from recent average?"

    This is unbounded; useful as an intermediate step.
    """
    s = series.dropna()
    if s.empty:
        return series.astype(float) * np.nan

    if min_periods is None:
        min_periods = max(6, window // 4)

    roll_mean = s.rolling(window, min_periods=min_periods).mean()
    roll_std = s.rolling(window, min_periods=min_periods).std()

    z = (s - roll_mean) / roll_std
    z = z.replace([np.inf, -np.inf], np.nan)
    return _align_output(series, z)


def minmax_scale_0_100(series: pd.Series, lower_quantile: float = 0.01, upper_quantile: float = 0.99) -> pd.Series:
    """
    Scale series to 0–100 using empirical quantiles for robustness.

    By default:
        - 1st percentile -> 0
        - 99th percentile -> 100
        Values outside are clipped.
    """
    s = series.dropna()
    if s.empty:
        return series.astype(float) * np.nan

    q_low = s.quantile(lower_quantile)
    q_high = s.quantile(upper_quantile)

    if q_high <= q_low:
        core = pd.Series(50.0, index=s.index)
        return _align_output(series, core)

    scaled = (s - q_low) / (q_high - q_low) * 100.0
    scaled = scaled.clip(0.0, 100.0)
    return _align_output(series, scaled)


def sigmoid_z(
    series: pd.Series,
    window: int = 24,
    min_periods: int | None = None,
    z_clip: float = 4.0,
) -> pd.Series:
    """
    Rolling z-score passed through a logistic transform to get 0–100.

    Steps:
        1. Compute rolling z.
        2. Clip z to [-z_clip, z_clip] to avoid extreme tails.
        3. Apply logistic: sig = 1 / (1 + exp(-z)).
        4. Scale sig to 0–100.

    Interpretation:
        ~ 0   = very low vs recent history
        ~ 50  = near recent mean
        ~ 100 = very high vs recent history
    """
    z = rolling_z(series, window=window, min_periods=min_periods)
    z_s = z.dropna()
    if z_s.empty:
        return series.astype(float) * np.nan

    z_s = z_s.clip(-z_clip, z_clip)
    sig = 1.0 / (1.0 + np.exp(-z_s))
    core = sig * 100.0
    core = core.clip(0.0, 100.0)
    return _align_output(series, core)


NormalizationMethod = Literal[
    "expanding_percentile",
    "rolling_percentile",
    "rolling_z_sigmoid",
    "minmax",
]


def normalize_series(series: pd.Series, method: NormalizationMethod = "expanding_percentile", **kwargs) -> pd.Series:
    """
    Generic entry point.

    Parameters
    ----------
    series : pd.Series
        Raw values.
    method : str
        One of:
            - "expanding_percentile"
            - "rolling_percentile"
            - "rolling_z_sigmoid" (rolling z -> logistic 0–100)
            - "minmax"
    kwargs : dict
        Extra keyword args passed to the underlying function.

    Returns
    -------
    pd.Series
        Normalized series aligned with the original index.
    """
    method = method.lower()

    if method == "expanding_percentile":
        return expanding_percentile(series)
    elif method == "rolling_percentile":
        window = int(kwargs.get("window", 60))
        min_periods = kwargs.get("min_periods", None)
        return rolling_percentile(series, window=window, min_periods=min_periods)
    elif method == "rolling_z_sigmoid":
        window = int(kwargs.get("window", 24))
        min_periods = kwargs.get("min_periods", None)
        z_clip = float(kwargs.get("z_clip", 4.0))
        return sigmoid_z(series, window=window, min_periods=min_periods, z_clip=z_clip)
    elif method == "minmax":
        lower_q = float(kwargs.get("lower_quantile", 0.01))
        upper_q = float(kwargs.get("upper_quantile", 0.99))
        return minmax_scale_0_100(series, lower_quantile=lower_q, upper_quantile=upper_q)
    else:
        raise ValueError(f"Unknown normalization method: {method}")
