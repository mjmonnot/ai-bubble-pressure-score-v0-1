# src/aibps/fetch_credit.py
from __future__ import annotations
import os
from pathlib import Path
import pandas as pd
import numpy as np

DATA_DIR = Path("data")
PROC_OUT = DATA_DIR / "processed" / "credit_fred_processed.csv"

# FRED series (verified)
AAA = "AAA"          # Moody's Seasoned Aaa Corporate Bond Yield (monthly)  [FRED]
BAA = "BAA"          # Moody's Seasoned Baa Corporate Bond Yield (monthly)  [FRED]
HY_OAS = "BAMLH0A0HYM2"  # ICE BofA US High Yield OAS (bp)                  [FRED]
IG_OAS = "BAMLC0A0CM"    # ICE BofA US Corporate Index OAS (bp)             [FRED]

START = "1980-01-01"  # go as deep as you like

def main():
    key = os.getenv("FRED_API_KEY")
    if not key:
        print("⚠️ No FRED_API_KEY — cannot fetch credit series.")
        return

    from fredapi import Fred
    fred = Fred(api_key=key)

    def get(sid):
        s = fred.get_series(sid, observation_start=START)
        s = pd.Series(s, name=sid).sort_index()
        s.index = pd.to_datetime(s.index)
        s.index.name = "date"
        return s

    # Long-history Baa - Aaa spread (in percentage points)
    aaa = get(AAA)
    baa = get(BAA)
    spread = (baa - aaa).rename("CREDIT_SPREAD_BAA_AAA")

    # ICE OAS (basis points)
    hy = get(HY_OAS).rename("HY_OAS")
    ig = get(IG_OAS).rename("IG_OAS")

    # Combine, monthly index, drop all-null rows
    out = pd.concat([spread, hy, ig], axis=1)
    out = out.resample("M").last()
    out = out.dropna(how="all")
    out.index.name = "date"

    PROC_OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(PROC_OUT)
    print("---- credit tail ----")
    print(out.tail(6))
    print(f"💾 Wrote {PROC_OUT} (rows={len(out)})  span: {out.index.min().date()} → {out.index.max().date()}")

if __name__ == "__main__":
    main()
