# src/aibps/fetch_infra_macro.py
from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd


DATA_DIR = Path("data")
PROC_OUT = DATA_DIR / "processed" / "infra_macro_processed.csv"

# FRED series for power-related infrastructure
# - IPG2211S: Industrial Production Index for Electric Power Generation, Transmission, and Distribution
# - CAPUTLG2211S: Capacity Utilization for the same sector
IP_POWER_IP = "IPG2211S"
IP_POWER_CAPU = "CAPUTLG2211S"

# Go as deep as you like; 1980 matches your birth-year cutoff nicely :)
START = "1980-01-01"


def _rebase_100(s: pd.Series) -> pd.Series:
    s = s.sort_index()
    if not s.notna().any():
        return s * np.nan
    first = s.dropna().iloc[0]
    if first == 0 or not np.isfinite(first):
        return s * np.nan
    return (s / first) * 100.0


def main():
    key = os.getenv("FRED_API_KEY")
    if not key:
        print("⚠️ No FRED_API_KEY — cannot fetch infra macro series.")
        return

    from fredapi import Fred
    fred = Fred(api_key=key)

    def get_series(sid: str) -> pd.Series:
        s = fred.get_series(sid, observation_start=START)
        s = pd.Series(s, name=sid).sort_index()
        s.index = pd.to_datetime(s.index)
        s.index.name = "date"
        # Ensure monthly; most G.17 series are already monthly, but be explicit
        s = s.resample("M").last()
        return s

    try:
        ip = get_series(IP_POWER_IP).rename("IP_Power")
        capu = get_series(IP_POWER_CAPU).rename("CapU_Power")
    except Exception as e:
        print(f"⚠️ FRED fetch failed for infra macro: {e}")
        return

    df = pd.concat([ip, capu], axis=1).dropna(how="all")
    if df.empty:
        print("⚠️ No infra macro data after combining; nothing to write.")
        return

    # Rebase each to 100 at its first valid point
    df["IP_Power_idx"] = _rebase_100(df["IP_Power"])
    df["CapU_Power_idx"] = _rebase_100(df["CapU_Power"])

    # Equal-weighted composite of the indexed series
    df["Infra_Macro"] = df[["IP_Power_idx", "CapU_Power_idx"]].mean(axis=1, skipna=True)

    out = df[["Infra_Macro"]].dropna(how="all")
    out.index.name = "date"

    PROC_OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(PROC_OUT)

    print("---- infra_macro tail ----")
    print(out.tail(6))
    print(f"💾 Wrote {PROC_OUT} (rows={len(out)}) span: {out.index.min().date()} → {out.index.max().date()}")


if __name__ == "__main__":
    main()
