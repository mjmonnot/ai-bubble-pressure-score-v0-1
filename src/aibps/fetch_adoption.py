"""
fetch_adoption.py

Builds an Adoption pillar for AIBPS from FRED series.

Sub-pillars (all turned into 2015≈100 indices):

(1) Adoption_Enterprise_Software
    - Private fixed investment in software / IP products

(2) Adoption_Cloud_Services
    - Output proxies for information and professional/technical services

(3) Adoption_Digital_Labor
    - Employment in information + professional, scientific, and technical services

(4) Adoption_Connectivity  (optional but useful)
    - Telecom / data transmission proxies

Output:
    data/processed/adoption_processed.csv with columns:
      - Adoption_Enterprise_Software
      - Adoption_Cloud_Services
      - Adoption_Digital_Labor
      - Adoption_Connectivity
      - Adoption_Supply  (composite average)
      - Adoption         (alias for Adoption_Supply)
"""

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROC_DIR = Path("data") / "processed"
OUT_PATH = PROC_DIR / "adoption_processed.csv"

BASELINE_DATE = pd.Timestamp("2015-12-31")

# ----------------------------
# FRED series configuration
# ----------------------------

# NOTE: Some of these IDs may not exist in every time span; we log and skip if FRED
# returns nothing for a given series.

# 1) Enterprise software / IP investment
ENTERPRISE_SERIES = {
    # Real private fixed investment: Intellectual property products
    "A652RX1Q020SBEA": "Real_IP_Inv",
    # Real private fixed investment: Software
    "A747RX1Q020SBEA": "Real_Software_Inv",
}

# 2) Cloud & digital services output
CLOUD_SERIES = {
    # Industrial Production: Information
    "IPG51A2N": "IP_Info_Sector",
    # Industrial Production: Data processing, internet publishing, and other information services
    "IPN518": "IP_Data_Processing",
    # Industrial Production: Professional, scientific, and technical services (if available)
    "IPN541": "IP_Prof_Sci_Tech",
}

# 3) Digital labor (employment in info + professional/technical services)
LABOR_SERIES = {
    # All employees: Information
    "CES5000000001": "Emp_Info",
    # All employees: Professional and business services
    "CES6000000001": "Emp_Prof_Bus_Services",
}

# 4) Connectivity (telecom / data transmission)
CONNECT_SERIES = {
    # Industrial Production: Communications equipment
    "IPN3342": "IP_Comm_Equip",
    # Industrial Production: Wired telecommunications carriers (if available)
    "IPN5171": "IP_Wired_Telecom",
}


def get_fred():
    """Instantiate Fred client if API key exists, else return None."""
    key = os.getenv("FRED_API_KEY")
    if not key:
        print("⚠️ No FRED_API_KEY set; cannot fetch Adoption data from FRED.")
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
                print(f"⚠️ FRED returned empty for {sid} ({col_name}) [{label}]; skipping.")
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

    # 1) Enterprise software / IP
    ent_df = fetch_fred_block(fred, ENTERPRISE_SERIES, label="adoption_enterprise")
    if ent_df is None:
        ent_idx = pd.Series(dtype=float, name="Adoption_Enterprise_Software")
    else:
        ent_idx = build_block_index(ent_df, "Adoption_Enterprise_Software")

    # 2) Cloud / digital services
    cloud_df = fetch_fred_block(fred, CLOUD_SERIES, label="adoption_cloud")
    if cloud_df is None:
        cloud_idx = pd.Series(dtype=float, name="Adoption_Cloud_Services")
    else:
        cloud_idx = build_block_index(cloud_df, "Adoption_Cloud_Services")

    # 3) Digital labor
    labor_df = fetch_fred_block(fred, LABOR_SERIES, label="adoption_labor")
    if labor_df is None:
        labor_idx = pd.Series(dtype=float, name="Adoption_Digital_Labor")
    else:
        labor_idx = build_block_index(labor_df, "Adoption_Digital_Labor")

    # 4) Connectivity
    conn_df = fetch_fred_block(fred, CONNECT_SERIES, label="adoption_connect")
    if conn_df is None:
        conn_idx = pd.Series(dtype=float, name="Adoption_Connectivity")
    else:
        conn_idx = build_block_index(conn_df, "Adoption_Connectivity")

    series_list = [ent_idx, cloud_idx, labor_idx, conn_idx]
    non_empty = [s for s in series_list if s is not None and not s.empty]

    if not non_empty:
        print("⚠️ No Adoption sub-pillar series available; writing empty adoption_processed.csv.")
        df = pd.DataFrame(columns=[
            "Adoption_Enterprise_Software",
            "Adoption_Cloud_Services",
            "Adoption_Digital_Labor",
            "Adoption_Connectivity",
            "Adoption_Supply",
            "Adoption",
        ])
        df.to_csv(OUT_PATH, index_label="Date")
        print(f"💾 Wrote empty {OUT_PATH}")
        return 0

    # Common monthly index
    idx_min = min(s.index.min() for s in non_empty)
    idx_max = max(s.index.max() for s in non_empty)
    monthly_idx = pd.date_range(idx_min, idx_max, freq="M")

    df = pd.DataFrame(index=monthly_idx)

    for s in series_list:
        if s is None or s.empty:
            continue
        df = df.join(s, how="left")

    component_cols = [
        col for col in [
            "Adoption_Enterprise_Software",
            "Adoption_Cloud_Services",
            "Adoption_Digital_Labor",
            "Adoption_Connectivity",
        ]
        if col in df.columns
    ]

    if not component_cols:
        df["Adoption_Supply"] = np.nan
        print("⚠️ No Adoption components found; Adoption_Supply is NaN.")
    else:
        df["Adoption_Supply"] = df[component_cols].mean(axis=1)
        print(f"✅ Adoption_Supply built from components: {component_cols}")

    df["Adoption"] = df["Adoption_Supply"]

    df = df.sort_index()
    print("---- Tail of adoption_processed.csv ----")
    print(df.tail(10))

    df.to_csv(OUT_PATH, index_label="Date")
    print(f"💾 Wrote {OUT_PATH} with columns: {list(df.columns)} (rows={len(df)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
