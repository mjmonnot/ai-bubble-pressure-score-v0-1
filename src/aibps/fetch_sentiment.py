# src/aibps/fetch_sentiment_trends.py
# Sentiment / AI Hype pillar via Google Trends
# - Uses pytrends to fetch search interest for AI-related terms
# - Aggregates monthly and normalizes 0–100
# - Outputs data/processed/sentiment_processed.csv with column "Sentiment"

import os
import sys
import time
import pandas as pd
import numpy as np
from pytrends.request import TrendReq

OUT = os.path.join("data", "processed", "sentiment_processed.csv")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

# Core AI search terms to track
TERMS = ["artificial intelligence", "chatgpt", "openai", "generative ai", "machine learning"]

def main():
    t0 = time.time()
    try:
        pytrends = TrendReq(hl="en-US", tz=360)
    except Exception as e:
        print(f"❌ pytrends init failed: {e}")
        sys.exit(1)

    dfs = []
    for term in TERMS:
        try:
            pytrends.build_payload([term], timeframe="2015-01-01 2025-12-31", geo="")
            df = pytrends.interest_over_time()
            if not df.empty and term in df.columns:
                s = df[term].rename(term)
                dfs.append(s)
                print(f"Fetched {len(s)} monthly points for {term}")
            else:
                print(f"⚠️ No data for {term}")
        except Exception as e:
            print(f"⚠️ pytrends failed for {term}: {e}")

    if not dfs:
        print("⚠️ No trends fetched; writing empty sentiment_processed.csv")
        pd.DataFrame(columns=["Sentiment"]).to_csv(OUT)
        return

    df_all = pd.concat(dfs, axis=1)
    df_all.index = pd.to_datetime(df_all.index)
    df_all = df_all.resample("M").mean()  # monthly mean interest
    df_all.index.name = "date"

    # Aggregate across terms
    df_all["hype_mean"] = df_all.mean(axis=1, skipna=True)

    # Percentile (0–100) relative to full history
    def expanding_pct(series):
        vals = []
        for i in range(len(series)):
            vals.append(series[: i + 1].rank(pct=True).iloc[-1] * 100)
        return pd.Series(vals, index=series.index)

    s = expanding_pct(df_all["hype_mean"]).clip(1, 99)
    s.name = "Sentiment"

    out = pd.DataFrame({"Sentiment": s}).dropna()
    out.to_csv(OUT)

    print(f"💾 Wrote {OUT} ({len(out)} rows) using Google Trends")
    print("Tail:")
    print(out.tail(6))
    print(f"⏱ Done in {time.time() - t0:.2f}s")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ fetch_sentiment_trends.py: {e}")
        sys.exit(1)
