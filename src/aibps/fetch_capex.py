# src/aibps/fetch_capex.py
# Reads data/raw/capex_manual.csv -> writes data/processed/capex_processed.csv with Capex_Supply (0–100)
import os, sys, time
import pandas as pd
import numpy as np

RAW = os.path.join("data","raw","capex_manual.csv")
OUT = os.path.join("data","processed","capex_processed.csv")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

def rolling_pct_rank(series: pd.Series, window: int = 120) -> pd.Series:
    def _rank_last(x):
        s = pd.Series(x)
        return (s.rank(pct=True).iloc[-1] * 100)
    return series.rolling(window, min_periods=max(24, window//4)).apply(_rank_last, raw=False)

def main():
    if not os.path.exists(RAW):
        print(f"ℹ️ {RAW} not found. Skipping Capex_Supply pillar.")
        pd.DataFrame(columns=["Capex_Supply"]).to_csv(OUT)
        return

    df = pd.read_csv(RAW)
    df["date"] = pd.to_datetime(df["date"]).dt.to_period("M").dt.to_timestamp("M")
    df = df[pd.to_numeric(df["value"], errors="coerce").notna()].copy()
    df["value"] = df["value"].astype(float)

    # Sum across companies each month (USD)
    monthly = df.groupby("date")["value"].sum().sort_index()

    # Rolling 10y percentile (monthly)
    capex_pct = rolling_pct_rank(monthly, window=120)

    out = pd.DataFrame({"Capex_Supply": capex_pct}).dropna()
    out.to_csv(OUT)
    print(f"💾 Wrote {OUT} ({len(out)} rows)")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ fetch_capex.py: {e}")
        sys.exit(1)
