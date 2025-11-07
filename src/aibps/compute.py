# src/aibps/compute.py
# Robust compute: monthly alignment, numeric coercion, trims rows with no pillars, ensures Market/Credit propagate
import os, sys, time
import numpy as np
import pandas as pd

PRO = os.path.join("data","processed")
OUT = os.path.join(PRO,"aibps_monthly.csv")
os.makedirs(PRO, exist_ok=True)

def read_proc(filename: str) -> pd.DataFrame | None:
    path = os.path.join(PRO, filename)
    if not os.path.exists(path): return None
    try:
        df = pd.read_csv(path, index_col=0, parse_dates=True)
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index, errors="coerce")
        df = df[~df.index.isna()].sort_index()
        # Coerce all columns numeric to kill stray strings
        for c in df.columns: df[c] = pd.to_numeric(df[c], errors="coerce")
        # snap to month-end grid
        df.index = df.index.to_period("M").to_timestamp("M")
        return df
    except Exception as e:
        print(f"⚠️ read_proc failed for {filename}: {e}")
        return None

def build_market(market: pd.DataFrame | None) -> pd.DataFrame | None:
    if market is None or market.empty: return None
    mcols = [c for c in market.columns if c.startswith("MKT_")]
    if not mcols:
        mcols = [c for c in market.columns if pd.api.types.is_numeric_dtype(market[c])]
    if not mcols: return None
    ser = market[mcols].mean(axis=1, skipna=True)
    return ser.to_frame("Market")

def build_credit(credit: pd.DataFrame | None) -> pd.DataFrame | None:
    if credit is None or credit.empty: return None
    ccols = [c for c in credit.columns if c.endswith("_pct")]
    if not ccols:
        ccols = [c for c in credit.columns if pd.api.types.is_numeric_dtype(credit[c])]
    if not ccols: return None
    ser = credit[ccols].mean(axis=1, skipna=True)
    return ser.to_frame("Credit")

def keep_one(df: pd.DataFrame | None, name: str) -> pd.DataFrame | None:
    if df is None or df.empty or name not in df.columns: return None
    return df[[name]]

def main():
    t0 = time.time()

    mkt = read_proc("market_processed.csv")
    crd = read_proc("credit_fred_processed.csv")
    cap = read_proc("capex_processed.csv")
    inf = read_proc("infra_processed.csv")
    adp = read_proc("adoption_processed.csv")

    parts = []
    mk = build_market(mkt);    cr = build_credit(crd)
    if mk is not None: parts.append(mk)
    if cr is not None: parts.append(cr)
    if (cx:=keep_one(cap,"Capex_Supply")) is not None: parts.append(cx)
    if (ir:=keep_one(inf,"Infra")) is not None: parts.append(ir)
    if (ap:=keep_one(adp,"Adoption")) is not None: parts.append(ap)

    if not parts:
        raise RuntimeError("No pillar inputs found in data/processed/")

    # Outer join across month-end; then drop rows where ALL pillars are NaN
    df = pd.concat(parts, axis=1, join="outer").sort_index()
    df = df[~df.index.duplicated(keep="last")]
    df = df.loc[~df[pd.Index(df.columns)].isna().all(axis=1)]

    # (Optional) also drop rows where BOTH Market and Credit are NaN (keeps rows only if at least one exists)
    core = [c for c in ["Market","Credit"] if c in df.columns]
    if core:
        df = df.loc[~df[core].isna().all(axis=1)]

    # Static reference composite (app recomputes interactively anyway)
    desired  = ["Market","Capex_Supply","Infra","Adoption","Credit"]
    present  = [p for p in desired if p in df.columns]
    defaults = {"Market":0.25,"Capex_Supply":0.25,"Infra":0.20,"Adoption":0.15,"Credit":0.15}
    w = np.array([defaults[p] for p in present], dtype=float)
    w = w / w.sum() if w.sum() else np.ones(len(present))/len(present)
    df["AIBPS"] = (df[present] * w).sum(axis=1, skipna=True)
    df["AIBPS_RA"] = df["AIBPS"].rolling(3, min_periods=1).mean()

    # Sanity print
    print("---- tails (Market/Credit/AIBPS) ----")
    for col in [c for c in ["Market","Credit","AIBPS","AIBPS_RA"] if c in df.columns]:
        print(col); print(df[col].tail(6))

    df.to_csv(OUT)
    print(f"💾 Wrote {OUT} with pillars: {present} (rows={len(df)})")
    print(f"⏱  Done in {time.time()-t0:.2f}s")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ compute.py: {e}")
        sys.exit(1)
