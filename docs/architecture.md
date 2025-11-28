# 🏗️ Overview
This document describes the full AIBPS system architecture, data pipeline, module responsibilities, and extensibility model.

---

# 🧩 1. Repository Structure
repo/
├── app/
│   └── streamlit_app.py
├── src/aibps/
│   ├── compute.py
│   ├── normalize.py
│   ├── fetch_market.py
│   ├── fetch_credit.py
│   ├── fetch_macro_capex.py
│   ├── fetch_infra.py
│   ├── fetch_adoption.py
│   ├── fetch_sentiment.py
│   └── config.yaml
├── data/
│   ├── raw/
│   └── processed/
└── .github/workflows/update-data.yml

---

# 🛰️ 2. Data Pipeline Overview
GitHub Actions Scheduler  
↓  
fetch_market.py  
fetch_credit.py  
fetch_macro_capex.py  
fetch_infra.py  
fetch_adoption.py  
fetch_sentiment.py  
↓  
data/raw → data/processed  
↓  
compute.py → aibps_monthly.csv  
↓  
Streamlit Dashboard

---

# ⚙️ 3. Module Responsibilities

## normalize.py
Implements:
- percentile scaling  
- z-score  
- sigmoid(z)  
- rolling z-score  
- clipping  

Called via:
normalize_series(series, method="rolling_z_sigmoid", params={…})

## compute.py
- Loads processed pillar files  
- Aligns all data to a monthly DatetimeIndex (1980 → present)  
- Normalizes pillars using config.yaml  
- Produces:
  - AIBPS
  - AIBPS_RA (smoothed)
- Writes final aibps_monthly.csv  

## fetch_* modules  
Each script:
1. Fetches data (FRED, Yahoo Finance, CSV, synthetic fallback)  
2. Cleans & renames columns  
3. Reindexes to monthly  
4. Builds sub-pillar composites  
5. Saves processed CSV  

Modules:
- fetch_market.py  
- fetch_credit.py  
- fetch_macro_capex.py  
- fetch_infra.py  
- fetch_adoption.py  
- fetch_sentiment.py  

---

# 📊 4. Composite Score Construction

All pillars normalized 0–100.

Weighted composite:
AIBPS = Σ(weight[p] × normalized[p])

Default weights (config.yaml):
- Market: 0.1667  
- Credit: 0.1667  
- Capex_Supply: 0.1667  
- Infra: 0.1667  
- Adoption: 0.1667  
- Sentiment: 0.1667  

Dashboard displays:
- AIBPS  
- AIBPS_RA  

---

# 🧮 5. GitHub Actions Automation

.update-data workflow:
1. Setup Python  
2. Run all fetch scripts  
3. Print dataset tails  
4. Run compute.py  
5. Commit & push processed data  
6. Trigger Streamlit redeploy  

Ensures automatic daily updates.

---

# 🖥️ 6. Streamlit Dashboard Architecture

Displays:
- Main long-run AIBPS line (1980→present)  
- Historical regime bands  
- Pillar trajectory panels  
- Sub-pillar debug expanders  
- Contribution bars  
- Weight sliders  
- Freshness badge  
- Raw data viewer  

Automatic detection of new pillars.

---

# 🧱 7. Extensibility

To add a new pillar:
1. Create fetch_newpillar.py  
2. Create raw and processed CSV outputs  
3. Update config.yaml normalization  
4. Add pillar to compute.py load + weighting  
Dashboard will auto-display.

---

# 🔐 8. Security
- Only secret: FRED_API_KEY  
- Stored in GitHub Secrets  
- Never logged, never written to disk  

---

# ⚡ 9. Performance
- Full pipeline executes in ~5 seconds  
- Supports 45+ years of monthly data  
- Streamlit UI loads instantly  

---

# 📉 10. Limitations
- Quarterly FRED → step artifacts  
- Sparse adoption series  
- Hyperscaler capex partly manual for now  
- Sentiment API limits (rate limiting)  
- Smoothing reduces volatility but hides noise  

---

# 🧭 11. Future Enhancements
- Global compute capacity indices  
- FLOPs-per-dollar curves  
- Cloud utilization + backlog  
- Venture funding cycles  
- AI hiring + displacement indices  
- NVIDIA GPU supply chain load metrics  
- Real hyperscaler capex ingestion  
- Optional forecasting module  

