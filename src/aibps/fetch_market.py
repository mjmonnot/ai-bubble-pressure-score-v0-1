# src/aibps/fetch_market.py
from __future__ import annotations

from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
import yfinance as yf

DATA_DIR = Path("data")
RAW_OUT = DATA_DIR / "raw" / "market_prices.csv"
PROC_OUT = DATA_DIR / "processed" / "market_processed.csv"

# Go back to your birth year 🙂
START = "1980-01-01"

# Broad + growth/speculative proxies
# ^GSPC: S&P 500
# ^IXIC: Nasdaq Composite
# ^NDX : Nasdaq 100
# QQQ  : Nasdaq 100 ETF
# ARKK : High-spec innovation ETF
TICKERS: List[str] = ["^GSPC", "^IXIC", "^NDX", "QQQ", "ARKK"]


def _fetch_one(ticker: str, start: str) -> pd.Series | None:
    """Fetch one ticker's adjusted close as a monthly series."""
    try:
        df = yf.download(ticker, start=start, auto_adjust=True, progress=False)
    except Exception as e:
        print(f"⚠️ yfinance exception for {ticker}: {e}")
        return None

    if df is None or df.empty or "Close" not in df.columns:
        print(f"⚠️ Empty/invalid data for {ticker}; skipping.")
        return None

    s = df["Close"].copy()
    s.index = pd.to_datetime(s.index)
    s.index.name = "date"

    # Monthly: last close of each month
    s = s.resample("M").last().dropna()

    if s.empty:
        print(f"⚠️ No monthly data for {ticker} after resample; skipping.")
        return None

    s.name = ticker
    return s


def _rebase_100(s: pd.Series) -> pd.Series:
    s = s.sort_index()
    if not s.notna().any():
        return s * np.nan
    first = s.dropna().iloc[0]
    if not np.isfinite(first) or first == 0:
        return s * np.nan
    return (s / first) * 100.0


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    RAW_OUT.parent.mkdir(parents=True, exist_ok=True)
    PROC_OUT.parent.mkdir(parents=True, exist_ok=True)

    frames: List[pd.Series] = []
    for t in TICKERS:
        s = _fetch_one(t, START)
        if s is not None:
            frames.append(s)

    if not frames:
        print("❌ No market series fetched; aborting.")
        return

    # Wide panel of monthly levels
    wide = pd.concat(frames, axis=1).sort_index()
    wide.index.name = "date"

    # Persist raw multi-ticker panel for reference/debug
    wide.to_csv(RAW_OUT)
    print(f"💾 Wrote {RAW_OUT} with columns: {list(wide.columns)}")
    print(f"   Date span: {wide.index.min().date()} → {wide.index.max().date()}")

    # Rebase each series to 100 at its own first valid point
    rebased = wide.apply(_rebase_100)
    # Give friendly column names for debug
    rename_map = {col: f"Mkt_{col.replace('^', '')}_idx" for col in rebased.columns}
    rebased = rebased.rename(columns=rename_map)

    # Equal-weight composite of all rebased series
    market_eqw = rebased.mean(axis=1, skipna=True).rename("Market")

    # Output: composite + underlying rebased components
    out = pd.concat([market_eqw, rebased], axis=1).dropna(how="all")
    out.index.name = "date"

    print("---- Market composite tail (rebased EW) ----")
    print(out[["Market"]].tail(6))
    print(f"✅ Market composite span: {out.index.min().date()} → {out.index.max().date()}")

    out.to_csv(PROC_OUT)
    print(f"💾 Wrote {PROC_OUT} (rows={len(out)}) with columns: {list(out.columns)}")


if __name__ == "__main__":
    main()
