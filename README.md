# 🔥 AI Bubble Pressure Score (AIBPS)
### Quantifying systemic bubble pressure across the AI economy  
**Market • Credit • Capex • Infrastructure • Adoption • Sentiment**

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Interactive%20App-FF4B4B.svg)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
---

## 📦 About AIBPS
The **AI Bubble Pressure Score (AIBPS)** is a quantitative, multi-pillar index designed to measure **systemwide speculative pressure** in the AI ecosystem.  
It integrates **market valuations**, **credit conditions**, **capex cycles**, **infrastructure constraints**, **adoption patterns**, and **sentiment intensity** into a unified 0–100 index.

AIBPS is **not a price predictor**. It is a **diagnostic instrument** for identifying when AI-related conditions resemble prior speculative bubbles such as the Dot-Com bubble, housing/credit bubble, or crypto asset cycles.

---

## 🚀 Live Dashboard
👉 https://aibps-v0-1.streamlit.app

Features:
- Real-time AIBPS score  
- Adjustable pillar weighting  
- Multi-pillar trajectories  
- Historical bubble regime overlays  
- Deep debug panels  
- Fully automated nightly data refresh  

---

## 📊 AIBPS Regimes (0–100 Scale)

| Range | Regime | Interpretation |
|-------|--------|----------------|
| **0–20** | Green | Fundamentals-driven, early cycle |
| **20–40** | Light Green | Normal expansion |
| **40–60** | Yellow | Elevated enthusiasm |
| **60–80** | Orange | Overheating risk |
| **80–100** | Red | Historically extreme bubble pressure |

---

## 🧠 Why AIBPS?
Traditional bubble indicators track only price. AIBPS instead integrates **six independent economic systems**:

1. **Market valuations** — AI-linked equities, sector indices  
2. **Credit & liquidity** — corporate spread pressure  
3. **Capex supply** — semi fab expansions, cloud GPU purchasing  
4. **Infrastructure** — power grid and datacenter limits  
5. **Adoption** — enterprise AI diffusion and demand  
6. **Sentiment** — hype velocity, narrative acceleration  

This creates a more realistic picture of systemic overheating.

---

# 📚 Documentation

### 🔬 Conceptual
- docs/research_background.md  
- docs/how_to_interpret_aibps.md  
- docs/methodology.md  

### 🏗 Technical
- docs/architecture.md  
- docs/pillars.md  
- docs/data_sources.md  
- docs/roadmap.md  

---

# 🏗 System Architecture

Below is a plain-text diagram safe for Markdown blocks:

    GitHub Actions (Nightly)
                │
                ▼
        Fetchers for all pillars
        (Market, Credit, Capex,
         Infra, Adoption, Sentiment)
                │
                ▼
        data/raw/*.csv (raw lake)
                │
                ▼
      Processing & QA pipeline
      clean → resample → align
                │
                ▼
       data/processed/*.csv
                │
                ▼
        Composite Engine (AIBPS)
     normalize → weight → aggregate
                │
                ▼
  data/processed/aibps_monthly.csv
                │
                ▼
       Streamlit Front-End App

---

# 📥 Installation

### 1. Clone the repository (indentation used instead of code fence)
    git clone https://github.com/mjmonnot/aibps-v0-1.git
    cd aibps-v0-1

### 2. Install dependencies
    pip install -r requirements.txt

### 3. Optional: export your FRED API key
    export FRED_API_KEY="your_fred_key"

---

# 🔄 Automated Data Refresh
A nightly GitHub Action fetches, validates, and updates all datasets.  
Badge:

![Data Update](https://github.com/mjmonnot/aibps-v0-1/actions/workflows/update-data.yml/badge.svg)

---

# 📈 Example Output
![AIBPS Example Chart](docs/img/aibps_chart_placeholder.png)

---

# 📂 Repository Structure

    aibps-v0-1/
    ├── app/
    │   └── streamlit_app.py
    ├── src/aibps/
    │   ├── compute.py
    │   ├── normalize.py
    │   ├── config.yaml
    │   ├── fetch_market.py
    │   ├── fetch_credit.py
    │   ├── fetch_capex.py
    │   ├── fetch_macro_capex.py
    │   ├── fetch_infra.py
    │   ├── fetch_adoption.py
    │   ├── fetch_sentiment.py
    │   └── utils/
    ├── data/
    │   ├── raw/
    │   └── processed/
    ├── docs/
    │   ├── methodology.md
    │   ├── research_background.md
    │   ├── how_to_interpret_aibps.md
    │   ├── data_sources.md
    │   ├── architecture.md
    │   ├── pillars.md
    │   └── img/
    ├── .github/workflows/
    │   └── update-data.yml
    ├── requirements.txt
    └── README.md

---

# 🤝 Contributing
We welcome contributions related to:

- Econometrics & forecasting  
- Data engineering  
- Infrastructure analysis  
- Behavioral & sentiment modeling  
- Visualization & dashboard design  

Submit issues or pull requests.

---

# 📜 License
MIT License — open for research, academic, and commercial use.

---

# 🧠 Citation (APA)
Monnot, M. J. (2025). *AI Bubble Pressure Score (AIBPS): A multi-pillar systemic pressure index.* GitHub Repository. https://github.com/mjmonnot/aibps-v0-1

---

# 💬 Contact
Issues: https://github.com/mjmonnot/aibps-v0-1/issues  
Creator: Matthew J. Monnot, PhD
