# src/aibps/fetch_macro_capex.py
# Macro Capex (FRED) -> monthly interpolation -> YoY % change -> rolling percentile (0–100)

import os, sys, time
import pandas as pd
import numpy as np

OUT = os.path.join("data", "processed", "macro_capex_processed.csv")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

def _expanding_pct(series: pd.Series) -> pd.Series:
    out = []
    vals = series.values
    for i in range(len(vals)):
        s = pd.Series(vals[:i+1])
        out.append(float(s.rank(pct=True).iloc[-1] * 100.0))
    return pd.Series(out, index=series.index)

def rolling_pct_rank_flexible(series: pd.Series, window: int = 120) -> pd.Series:
    series = series.dropna()
    n = len(series)
    if n == 0:
        return series
    if n < 36:
        return _expanding_pct(series)
    def _rank_last(x):
        s = pd.Series(x)
        return float(s.rank(pct=True).iloc[-1] * 100.0)
    minp = max(36, window // 3)  # require ~3y before true rolling
    return series.rolling(window, min_periods=minp).apply(_rank_last, raw=False)

def pick_series(fred):
    candidates = [
        ("PNFI",   "Real Private Nonresidential Fixed Investment"),
        ("PNFIC1", "Real PNFI (SAAR, chained $)"),
        ("PNFIC",  "PNFI (current $)"),
    ]
    for sid, why in candidates:
        try:
            s = fred.get_series(sid, observation_start="2010-01-01")
            if s is not None and len(s) > 0:
                print(f"✔ Using FRED series {sid}: {why}")
                return sid, s
        except Exception as e:
            print(f"… {sid} failed: {e}")
    df = fred.search("Private Nonresidential Fixed Investment")
    if df is not None and not df.empty:
        if "frequency_short" in df.columns:
            df = df[df["frequency_short"].str.upper() == "Q"]
        sid = df.iloc[0]["id"]
        s = fred.get_series(sid, observation_start="2010-01-01")
        if s is not None and len(s) > 0:
            print(f"✔ Using FRED series from search: {sid} — {df.iloc[0].get('title','')}")
            return sid, s
    raise RuntimeError("Could not find a valid PNFI series on FRED.")

def main():
    t0 = time.time()
    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        print("❌ FRED_API_KEY missing")
        pd.DataFrame(columns=["Capex_Supply_Macro"]).to_csv(OUT)
        sys.exit(1)

    try:
        from fredapi import Fred
    except Exception as e:
        print(f"❌ fredapi not installed: {e}")
        pd.DataFrame(columns=["Capex_Supply_Macro"]).to_csv(OUT)
        sys.exit(1)

    fred = Fred(api_key=api_key)
    sid, q = pick_series(fred)

    q.index = pd.to_datetime(q.index, errors="coerce")
    q = q[~q.index.isna()].sort_index()

    # Month-end grid & linear interpolation (monthly proxy)
    start = q.index.min().to_period("M").to_timestamp("M")
    end   = pd.Timestamp.today().to_period("M").to_timestamp("M")
    idx_m = pd.period_range(start, end, freq="M").to_timestamp("M")
    m = q.reindex(idx_m).interpolate(method="linear")  # monthly level

    # YoY % change (12m), 3m smoothing for stability
    yoy = (m.pct_change(12) * 100.0).rolling(3, min_periods=1).mean()

    # Percentile of YoY (0–100), flexible rolling
    capex_pct = rolling_pct_rank_flexible(yoy, window=120)
    # Optional: winsorize to avoid hard 0/100
    capex_pct = capex_pct.clip(1, 99)

    out = pd.DataFrame({"Capex_Supply_Macro": capex_pct})
    out.index.name = "date"
    out = out.dropna(how="all")
    out.to_csv(OUT)

    print(f"💾 Wrote {OUT} ({len(out)} rows) • series {sid}")
    print("Tail:"); print(out.tail(6))
    print(f"⏱  Done in {time.time()-t0:.2f}s")

if __name__ == "__main__":
    main()
