# src/aibps/compute.py
"""
Combines processed inputs into pillar scores and the AIBPS composite.
Writes:
  - data/processed/aibps_monthly.csv
Falls back to sample composite if inputs are missing.
"""
import os, sys, time
import pandas as pd
import numpy as np

PRO_DIR = os.path.join("data", "processed")
SAMPLE = os.path.join("data", "sample", "aibps_monthly_sample.csv")
os.makedirs(PRO_DIR, exist_ok=True)

def safe_read(path, **kwargs):
    if os.path.exists(path):
        try:
            return pd.read_csv(path, **kwargs)
        except Exception as e:
            print(f"⚠️ Failed to read {path}: {e}")
    return None

def main():
    start = time.time()
    # Load processed inputs if present
    market = safe_read(os.path.join(PRO_DIR, "market_processed.csv"), index_col=0, parse_dates=True)
    credit = safe_read(os.path.join(PRO_DIR, "credit_fred_processed.csv"), index_col=0, parse_dates=True)

    if market is None and credit is None:
        # fallback to sample composite
        if os.path.exists(SAMPLE):
            print("ℹ️ Inputs missing → using sample composite.")
            df = pd.read_csv(SAMPLE, index_col=0, parse_dates=True)
            out_path = os.path.join(PRO_DIR, "aibps_monthly.csv")
            df.to_csv(out_path)
            print(f"💾 Wrote sample composite → {out_path}")
            return
        else:
            raise RuntimeError("No inputs and no sample composite found.")

    # Build pillar frame monthly
    frames = []
    if market is not None:
        frames.append(market)
    if credit is not None:
        frames.append(credit)

    df = pd.concat(frames, axis=1).sort_index()
    # Map processed columns to pillars (v0.1 proxy)
    # Market pillar from SOXX/QQQ percentiles
    market_cols = [c for c in df.columns if c.startswith("MKT_")]
    credit_cols = ["HY_OAS_pct", "IG_OAS_pct"] if "HY_OAS_pct" in df.columns else [c for c in df.columns if "OAS_pct" in c]

    out = pd.DataFrame(index=df.index)
    if market_cols:
        out["Market"] = df[market_cols].mean(axis=1)
    if credit_cols:
        ok = [c for c in credit_cols if c in df.columns]
        if ok:
            out["Credit"] = df[ok].mean(axis=1)

    # Stub the other pillars to mid values if missing (keeps app working)
    for p in ["Capex_Supply","Infra","Adoption"]:
        if p not in out.columns:
            out[p] = 55.0

    # Ensure column order
    pillars = ["Market","Capex_Supply","Infra","Adoption","Credit"]
    out = out[pillars].dropna(how="all")

    # Default weights (app can override interactively)
    w = np.array([0.25,0.25,0.20,0.15,0.15])
    present = [p for p in pillars if p in out.columns]
    w_adj = w[:len(present)]
    w_adj = w_adj / w_adj.sum()

    out["AIBPS"] = (out[present] * w_adj).sum(axis=1)
    out["AIBPS_RA"] = out["AIBPS"].rolling(3, min_periods=1).mean()

    out_path = os.path.join(PRO_DIR, "aibps_monthly.csv")
    out.to_csv(out_path)
    print(f"💾 Wrote composite → {out_path}")
    print(f"⏱ Done in {time.time()-start:.1f}s")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ compute.py failed: {e}")
        sys.exit(1)
