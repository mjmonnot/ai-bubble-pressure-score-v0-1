# src/aibps/fetch_macro_capex.py
# Macro Capex pillar (real data via FRED)
# - Uses Private Nonresidential Fixed Investment (PNFI) as a broad capex proxy.
# - Converts to monthly, computes percentile (0–100).
# - Outputs data/processed/macro_capex_processed.csv with column "Capex_Supply_Macro".

import os
import sys
import time
import pandas as pd
import numpy as np

from fredapi import Fred

OUT = os.path.join("data", "processed", "macro_capex_processed.csv")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

# FRED series ID: Private Nonresidential Fixed Investment (billions, SAAR, quarterly)
# https://fred.stlouisfed.org/series/PNFI
CAPEX_SERIES = "PNFI"


def _expanding_pct(series: pd.Series) -> pd.Series:
    out_vals = []
    vals = series.values
    for i in range(len(vals)):
        s = pd.Series(vals[: i + 1])
        out_vals.append(float(s.rank(pct=True).iloc[-1] * 100.0))
    return pd.Series(out_vals, index=series.index)


def rolling_pct_rank_flexible(series: pd.Series, window: int = 40) -> pd.Series:
    """
    For shorter histories: expanding percentile.
    For longer histories: rolling window percentile.
    """
    series = series.dropna()
    n = len(series)
    if n == 0:
        return series
    if n < 24:
        return _expanding_pct(series)

    def _rank_last(x):
        s = pd.Series(x)
        return float(s.rank(pct=True).iloc[-1] * 100.0)

    minp = max(24, window // 4)
    return series.rolling(window, min_periods=minp).apply(_rank_last, raw=False)


def main():
    t0 = time.time()
    api_key = os.getenv("FRED_API_KEY")
    if not api_key:
        print("ℹ️ FRED_API_KEY not set; writing empty macro_capex_processed.csv")
        pd.DataFrame(columns=["Capex_Supply_Macro"]).to_csv(OUT)
        return

    fred = Fred(api_key=api_key)

    try:
        ser = fred.get_series(CAPEX_SERIES)
    except Exception as e:
        print(f"❌ Failed to fetch {CAPEX_SERIES} from FRED: {e}")
        pd.DataFrame(columns=["Capex_Supply_Macro"]).to_csv(OUT)
        sys.exit(1)

    if ser is None or ser.empty:
        print(f"ℹ️ {CAPEX_SERIES} returned empty from FRED.")
        pd.DataFrame(columns=["Capex_Supply_Macro"]).to_csv(OUT)
        return

    # ser index is quarterly period-end; normalize to datetime index
    ser.index = pd.to_datetime(ser.index)
    ser.name = "capex_raw"

    # Convert to month-end by forward-filling each quarter across its months
    q_df = ser.to_frame()
    start = q_df.index.min().to_period("M").to_timestamp("M")
    end = pd.Timestamp.today().to_period("M").to_timestamp("M")
    idx = pd.period_range(start, end, freq="M").to_timestamp("M")
    m_df = q_df.reindex(idx).ffill()
    m_df.index.name = "date"

    # Percentile transform on level (we can later move to YoY if desired)
    capex_level = m_df["capex_raw"]
    capex_pct = rolling_pct_rank_flexible(capex_level, window=40)
    capex_pct = capex_pct.clip(1, 99)
    capex_pct.index.name = "date"

    out = pd.DataFrame({"Capex_Supply_Macro": capex_pct}).dropna(how="all")
    out.to_csv(OUT)

    print(f"💾 Wrote {OUT} ({len(out)} rows) using {CAPEX_SERIES}")
    print("Tail:")
    print(out.tail(6))
    print(f"⏱ Done in {time.time() - t0:.2f}s")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ fetch_macro_capex.py: {e}")
        sys.exit(1)
