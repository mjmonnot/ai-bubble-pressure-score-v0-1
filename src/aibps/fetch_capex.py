# src/aibps/fetch_capex.py
from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd


DATA_DIR = Path("data")
PROC_OUT = DATA_DIR / "processed" / "capex_processed.csv"

START = "1980-01-01"

# FRED series for Capex / Supply pillar
# Macro capex (broad investment)
PNFI = "PNFI"          # Private Nonresidential Fixed Investment
UNXANO = "UNXANO"      # Nonresidential structures

# Digital / IT / software capex proxies
SOFTWARE = "DTCTRC1A027NBEA"   # Real private fixed investment: software
ICT_EQUIP = "TLPCINS"          # Private fixed investment: tech / ICT equipment
COMP_ELEC = "ITNETPC"          # Computer / electronic products

# Semiconductor / fab proxies
SEMICON_IP = "IPB53800"            # Industrial production: semiconductors
SEMICON_CAPUTIL = "CAPUTLB50001SQ" # Capacity utilization: Semiconductor fab


def _to_monthly(s: pd.Series) -> pd.Series:
    """
    Convert a FRED series (annual, quarterly, or monthly) to end-of-month
    monthly frequency via forward fill, starting at START.
    """
    s = pd.Series(s).sort_index()
    s.index = pd.to_datetime(s.index)
    s.index.name = "date"
    s = s.resample("M").ffill()
    s = s[s.index >= pd.to_datetime(START)]
    return s


def _rebase_100(s: pd.Series) -> pd.Series:
    """
    Rebase a series so that its first non-NaN value = 100.
    """
    if not s.notna().any():
        return s * np.nan
    first = s.dropna().iloc[0]
    if not np.isfinite(first) or first == 0:
        return s * np.nan
    return (s / first) * 100.0


def main():
    key = os.getenv("FRED_API_KEY")
    if not key:
        print("⚠️ No FRED_API_KEY — cannot fetch Capex data.")
        return

    from fredapi import Fred
    fred = Fred(api_key=key)

    series_map = {
        "Capex_PNFI": PNFI,
        "Capex_UNXANO": UNXANO,
        "Capex_Software": SOFTWARE,
        "Capex_ICT_Equip": ICT_EQUIP,
        "Capex_CompElec": COMP_ELEC,
        "Capex_Semicon_IP": SEMICON_IP,
        "Capex_Semicon_CapUtil": SEMICON_CAPUTIL,
    }

    frames = {}
    for label, sid in series_map.items():
        try:
            raw = fred.get_series(sid, observation_start=START)
            monthly = _to_monthly(raw)
            frames[label] = monthly
        except Exception as e:
            print(f"⚠️ Failed to fetch {sid} ({label}): {e}")

    if not frames:
        print("❌ No Capex series fetched; not writing file.")
        return

    # Combine to wide DataFrame
    df = pd.concat(frames.values(), axis=1)
    df.columns = list(frames.keys())
    df.index.name = "date"

    # Rebase each component to 100
    rebased = df.apply(_rebase_100)
    rebased_cols = [f"{c}_idx" for c in rebased.columns]
    rebased.columns = rebased_cols

    # Composite: equal-weight of all rebased components
    composite = rebased.mean(axis=1, skipna=True).rename("Capex_Supply")

    # Final output: composite + rebased + raw
    out = pd.concat([composite, rebased, df.add_suffix("_raw")], axis=1)
    out = out.dropna(how="all")

    PROC_OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(PROC_OUT)

    print("---- Capex composite tail ----")
    print(out[["Capex_Supply"]].tail(6))
    print(f"💾 Wrote {PROC_OUT} with columns: {list(out.columns)}")
    print(f"Range: {out.index.min().date()} → {out.index.max().date()}")


if __name__ == "__main__":
    main()
