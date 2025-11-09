# src/aibps/fetch_infra_macro.py
# Macro Infra pillar (real data via FRED)
# - Uses Total Private Construction Spending on Power and Communication.
# - Computes combined level and turns it into 0–100 percentile.
# - Outputs data/processed/infra_macro_processed.csv with column "Infra_Macro".

import os
import sys
import time
import pandas as pd
import numpy as np

from fredapi import Fred

OUT = os.path.join("data", "processed", "infra_macro_processed.csv")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

# FRED series IDs (monthly, SAAR, millions) :
# Power:        PRPWRCONS
# Communication: PRCMUCONS
POWER_SERIES = "PRPWRCONS"
COMM_SERIES = "PRCMUCONS"


def _expanding_pct(series: pd.Series) -> pd.Series:
    out_vals = []
    vals = series.values
    for i in range(len(vals)):
        s = pd.Series(vals[: i + 1])
        out_vals.append(float(s.rank(pct=True).iloc[-1] * 100.0))
    return pd.Series(out_vals, index=series.index)


def rolling_pct_rank_flexible(series: pd.Series, window: int = 120) -> pd.Series:
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
        print("ℹ️ FRED_API_KEY not set; writing empty infra_macro_processed.csv")
        pd.DataFrame(columns=["Infra_Macro"]).to_csv(OUT)
        return

    fred = Fred(api_key=api_key)

    def get_series_safe(series_id: str) -> pd.Series | None:
        try:
            s = fred.get_series(series_id)
            if s is None or s.empty:
                print(f"ℹ️ {series_id} returned empty from FRED.")
                return None
            s.index = pd.to_datetime(s.index)
            s.name = series_id
            return s
        except Exception as e:
            print(f"❌ Failed to fetch {series_id} from FRED: {e}")
            return None

    power = get_series_safe(POWER_SERIES)
    comm = get_series_safe(COMM_SERIES)

    if power is None and comm is None:
        print("ℹ️ No macro infra series available; writing empty file.")
        pd.DataFrame(columns=["Infra_Macro"]).to_csv(OUT)
        return

    df = pd.DataFrame()
    if power is not None:
        df["power"] = power
    if comm is not None:
        df["comm"] = comm

    df.index.name = "date"
    df = df.sort_index()

    # Combine: sum as a rough proxy for total power+comms infra spend
    df["infra_level"] = df[["power", "comm"]].sum(axis=1, skipna=True)

    infra_level = df["infra_level"].dropna()
    if infra_level.empty:
        print("ℹ️ Combined infra_level empty; writing empty file.")
        pd.DataFrame(columns=["Infra_Macro"]).to_csv(OUT)
        return

    # Percentile transform on level
    infra_pct = rolling_pct_rank_flexible(infra_level, window=120)
    infra_pct = infra_pct.clip(1, 99)
    infra_pct.index.name = "date"

    out = pd.DataFrame({"Infra_Macro": infra_pct}).dropna(how="all")
    out.to_csv(OUT)

    print(f"💾 Wrote {OUT} ({len(out)} rows) using {POWER_SERIES} + {COMM_SERIES}")
    print("Tail:")
    print(out.tail(6))
    print(f"⏱ Done in {time.time() - t0:.2f}s")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ fetch_infra_macro.py: {e}")
        sys.exit(1)
