# src/aibps/fetch_credit.py
"""
Retrieves HY/IG credit spreads from FRED with fallback.
Writes:
  - data/raw/credit_fred.csv
  - data/processed/credit_fred_processed.csv
"""
import os, sys, time
import pandas as pd
import numpy as np
from datetime import datetime

RAW_DIR = os.path.join("data", "raw")
PRO_DIR = os.path.join("data", "processed")
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PRO_DIR, exist_ok=True)

def fetch_fred_or_fallback():
    key = os.getenv("FRED_API_KEY")
    if key:
        try:
            from fredapi import Fred
            fred = Fred(api_key=key)
            print("🔑 Using FRED API key found in environment.")
            hy = fred.get_series("BAMLH0A0HYM2")  # Series
            ig = fred.get_series("BAMLCC0A0CM")  # Series
            hy = pd.DataFrame({"HY_OAS": hy})
            ig = pd.DataFrame({"IG_OAS": ig})
            df = hy.join(ig, how="outer").sort_index()
            df.index.name = "Date"
            return df
        except Exception as e:
            print(f"⚠️ FRED fetch failed ({e}). Falling back to synthetic/sample.")
    else:
        print("⚠️ No FRED_API_KEY found. Falling back to synthetic/sample.")

    # Try sample first
    sample_path = os.path.join("data", "sample", "credit_fred_sample.csv")
    if os.path.exists(sample_path):
        return pd.read_csv(sample_path, index_col=0, parse_dates=True)

    # Generate synthetic fallback
    idx = pd.date_range("2015-01-31", "2025-12-31", freq="M")
    hy = np.linspace(6.5, 4.5, len(idx)) + np.random.normal(0, 0.2, len(idx))
    ig = np.linspace(2.2, 1.6, len(idx)) + np.random.normal(0, 0.1, len(idx))
    df = pd.DataFrame({"HY_OAS": hy, "IG_OAS": ig}, index=idx)
    df.index.name = "Date"
    return df

def pct_rank(s, invert=False):
    r = s.rank(pct=True) * 100
    return 100 - r if invert else r

def main():
    print(f"pandas version: {pd.__version__}")
    start = time.time()

    df = fetch_fred_or_fallback()

    raw_path = os.path.join(RAW_DIR, "credit_fred.csv")
    df.to_csv(raw_path)
    print(f"💾 Saved raw credit data → {raw_path}")

    # Percentiles (invert spreads: higher spread = lower percentile)
    out = df.copy()
    out["HY_OAS_pct"] = pct_rank(out["HY_OAS"], invert=True)
    out["IG_OAS_pct"] = pct_rank(out["IG_OAS"], invert=True)

    pro_path = os.path.join(PRO_DIR, "credit_fred_processed.csv")
    out.to_csv(pro_path)
    print(f"💾 Saved processed credit data → {pro_path}")
    print(f"⏱ Done in {time.time()-start:.1f}s")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ fetch_credit.py failed: {e}")
        sys.exit(1)
