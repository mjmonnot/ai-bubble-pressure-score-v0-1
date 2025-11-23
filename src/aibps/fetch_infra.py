"""
fetch_infra.py

Builds an Infrastructure (Infra) pillar for AIBPS from FRED series:

Sub-pillars:
(1) Infra_Power_Grid
    - proxies for electric power generation / utilities output

(2) Infra_Construction
    - proxies for nonresidential / power-related construction

(3) Infra_Semi_Equip
    - proxies for semiconductor-related equipment / industrial production

(4) Infra_Materials
    - proxies for steel / metals / copper (key infra inputs)

Output:
    data/processed/infra_processed.csv with columns:
      - Infra_Power_Grid
      - Infra_Construction
      - Infra_Semi_Equip
      - Infra_Materials
      - Infra_Supply  (composite average)
      - Infra         (alias for Infra_Supply, for backward compatibility)
"""

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROC_DIR = Path("data") / "processed"
OUT_PATH = PROC_DIR / "infra_processed.csv"

BASELINE_DATE = pd.Timestamp("2015-12-31")

# ----------------------------
# FRED series configuration
# ----------------------------

# These IDs are all public FRED series.
# If any fail, we log and skip; the composite will use what’s available.

POWER_SERIES = {
    # Industrial Production: Electric Power Generation, Transmission and Distribution
    "IPG2211A2N": "IP_Elec_Power",
    # Utilities industrial production (broader)
    "IPUTIL": "IP_Utilities",
}

CONSTR_SERIES = {
    # Private Nonresidential Fixed Investment
    "PNFI": "Priv_Nonres_Inv",
    # Private Residential Fixed Investment (helps capture broader construction pressure)
    "PRFI": "Priv_Res_Inv",
}

SEMI_EQUIP_SERIES = {
    # Semiconductor and related device production
    "IPG336413": "IP_Semi_Devices",
    # Capacity utilization in Semiconductors and related devices
    "IPN336413": "CU_Semi_Devices",
}

MATERIALS_SERIES = {
    # Steel production index
    "IPN331111": "IP_Steel_Prod",
    # Copper price per metric ton in US dollars (global copper proxy)
    "PCOPPUSDM": "Copper_Price_USD",
}


def get_fred():
    """Instantiate Fred client if API key exists, else return None."""
    key = os.getenv("FRED_API_KEY")
    if not key:
        print("⚠️ No FRED_API_KEY set; cannot fetch Infra data from FRED.")
        return None

    try:
        from fredapi import Fred  # type: ignore
    except ImportError:
        print("⚠️ fredapi not installed; cannot fetch from FRED.")
        return None

    try:
        fred = Fred(api_key=key)
        return fred
    except Exception as e:
        print(f"⚠️ Failed to initialize Fred: {e}")
        return None


def fetch_fred_block(fred, series_map, label: str) -> pd.DataFrame | None:
    """
    Fetch a group of FRED series and resample to monthly.

    Returns a DataFrame with monthly index and columns named per series_map.
    """
    if fred is None:
        print(f"ℹ️ No FRED client; skipping {label} block.")
        return None

    frames = []
    for sid, col_name in series_map.items():
        try:
            ser = fred.get_series(sid)
            if ser is None or len(ser) == 0:
                print(f"⚠️ FRED returned empty for {sid} ({col_name}); skipping.")
                continue
            df = ser.to_frame(name=col_name)
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            df_m = df.resample("M").ffill()
            frames.append(df_m)
            print(
                f"✅ FRED {sid} → {col_name} [{label}]: "
                f"{df_m.index.min().date()} to {df_m.index.max().date()}"
            )
        except Exception as e:
            print(f"⚠️ Failed to fetch {sid} ({col_name}) [{label}]: {e}")

    if not frames:
        print(f"⚠️ No series fetched for {label} block.")
        return None

    combined = pd.concat(frames, axis=1).sort_index()
    combined = combined.dropna(how="all")
    return combined


def scale_to_index(series: pd.Series, baseline_date: pd.Timestamp, name: str) -> pd.Series:
    """Scale a series so that baseline_date (or first valid) ≈ 100."""
    s = series.copy()

    baseline_val = np.nan
    if baseline_date in s.index and not pd.isna(s.loc[baseline_date]):
        baseline_val = s.loc[baseline_date]
        print(f"🔧 {name}: baseline {baseline_date.date()} value={baseline_val:.3f}")
    else:
        first_idx = s.first_valid_index()
        if first_idx is not None:
            baseline_val = s.loc[first_idx]
            print(f"🔧 {name}: using first valid {first_idx.date()} value={baseline_val:.3f} as baseline")
        else:
            print(f"⚠️ {name}: no valid values; returning unscaled.")
            return s

    if baseline_val == 0 or np.isnan(baseline_val):
        print(f"⚠️ {name}: invalid baseline; returning unscaled.")
        return s

    out = (s / baseline_val) * 100.0
    out.name = name
    return out


def build_block_index(df: pd.DataFrame, name: str) -> pd.Series:
    """Scale each column to an index and average into a composite."""
    if df is None or df.empty:
        return pd.Series(dtype=float, name=name)

    tmp = df.copy()
    for col in tmp.columns:
        tmp[col] = scale_to_index(tmp[col], BASELINE_DATE, col)

    idx = tmp.mean(axis=1)
    idx.name = name
    print(f"✅ Built composite index {name} from columns: {list(tmp.columns)}")
    return idx


def main():
    PROC_DIR.mkdir(parents=True, exist_ok=True)

    fred = get_fred()

    # 1) Power grid sub-pillar
    power_df = fetch_fred_block(fred, POWER_SERIES, label="infra_power")
    if power_df is None:
        power_idx = pd.Series(dtype=float, name="Infra_Power_Grid")
    else:
        power_idx = build_block_index(power_df, "Infra_Power_Grid")

    # 2) Construction sub-pillar
    constr_df = fetch_fred_block(fred, CONSTR_SERIES, label="infra_construction")
    if constr_df is None:
        constr_idx = pd.Series(dtype=float, name="Infra_Construction")
    else:
        constr_idx = build_block_index(constr_df, "Infra_Construction")

    # 3) Semiconductor equipment / capacity sub-pillar
    semi_df = fetch_fred_block(fred, SEMI_EQUIP_SERIES, label="infra_semi_equip")
    if semi_df is None:
        semi_idx = pd.Series(dtype=float, name="Infra_Semi_Equip")
    else:
        semi_idx = build_block_index(semi_df, "Infra_Semi_Equip")

    # 4) Materials sub-pillar
    mat_df = fetch_fred_block(fred, MATERIALS_SERIES, label="infra_materials")
    if mat_df is None:
        mat_idx = pd.Series(dtype=float, name="Infra_Materials")
    else:
        mat_idx = build_block_index(mat_df, "Infra_Materials")

    # Merge onto a common monthly index
    series_list = [power_idx, constr_idx, semi_idx, mat_idx]
    non_empty = [s for s in series_list if s is not None and not s.empty]

    if not non_empty:
        print("⚠️ No Infra sub-pillar series available; writing empty infra_processed.csv.")
        df = pd.DataFrame(columns=[
            "Infra_Power_Grid", "Infra_Construction", "Infra_Semi_Equip",
            "Infra_Materials", "Infra_Supply", "Infra"
        ])
        df.to_csv(OUT_PATH, index_label="Date")
        print(f"💾 Wrote empty {OUT_PATH}")
        return 0

    # Build a unified index from the earliest to latest of all series
    idx_min = min(s.index.min() for s in non_empty)
    idx_max = max(s.index.max() for s in non_empty)
    monthly_idx = pd.date_range(idx_min, idx_max, freq="M")

    df = pd.DataFrame(index=monthly_idx)

    for s in series_list:
        if s is None or s.empty:
            continue
        df = df.join(s, how="left")

    # Composite Infra_Supply from available sub-pillars
    component_cols = [
        col for col in [
            "Infra_Power_Grid",
            "Infra_Construction",
            "Infra_Semi_Equip",
            "Infra_Materials",
        ]
        if col in df.columns
    ]

    if not component_cols:
        df["Infra_Supply"] = np.nan
        print("⚠️ No Infra components found; Infra_Supply is NaN.")
    else:
        df["Infra_Supply"] = df[component_cols].mean(axis=1)
        print(f"✅ Infra_Supply built from components: {component_cols}")

    # Backward-compatible alias
    df["Infra"] = df["Infra_Supply"]

    df = df.sort_index()

    print("---- Tail of infra_processed.csv ----")
    print(df.tail(10))

    df.to_csv(OUT_PATH, index_label="Date")
    print(f"💾 Wrote {OUT_PATH} with columns: {list(df.columns)} (rows={len(df)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
