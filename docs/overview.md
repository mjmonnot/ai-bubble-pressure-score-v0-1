# 📘 **AI Bubble Pressure Score (AIBPS)**
### **Overview, Conceptual Framework & Interpretation Guide (v0.2)**  
_Last updated: {{ auto-updated by GitHub Actions }}_

---

<div align="center">

✨ **A composite indicator for detecting structural overheating in the AI-driven economy.**  
Tracks markets, credit, capex, infrastructure, adoption, and sentiment as a unified macro signal.

</div>

---

# 🧠 **1. What Is the AIBPS?**

The **AI Bubble Pressure Score (AIBPS)** is a multi-pillar composite index designed to estimate **bubble-like systemic pressure** in the AI economy.  
Unlike simple valuation metrics, AIBPS synchs together **six structural dimensions**:

- 📈 Market valuations & volatility  
- 💵 Credit risk & financial conditions  
- 🏭 Capex cycles & supply investment  
- ⚡ Infrastructure stress (power, racks, cooling)  
- 🧩 Adoption growth & enterprise absorption  
- 🔥 Sentiment intensity & hype dynamics  

**Goal:** detect overheating *before* system fragility reveals itself.

---

# 🏗️ **2. Pillar Framework**

Each pillar is transformed into a **0–100 pressure score** using a standardized normalization method (rolling Z → sigmoid scaling).  
This enables meaningful combination of otherwise unrelated signals.

| Pillar | Measures | Why It Matters | Signal Type |
|-------|----------|----------------|-------------|
| **Market** | Returns, volatility, semiconductor & AI baskets | Captures speculative excess | Financial |
| **Credit** | HY/IG spreads | Detects risk complacency | Macro-financial |
| **Capex / Supply** | AI-major capex + macro ICT investment | Reveals investment overshoot | Real economy |
| **Infrastructure** | Power, cooling, rackspace strain | Capacity bottlenecks under bubbles | Physical constraint |
| **Adoption** | Enterprise penetration, API usage, spend | Real demand vs. hype | Demand-side |
| **Sentiment** | Google Trends, narrative intensity | Crowd psychology & hype cycles | Behavioral |

All pillars are equally weighted by default (configurable in `config.yaml`).

---

# 🔧 **3. Data Pipeline (High-Level)**

Raw Data → Cleaning + Resampling → Normalization → Composite AIBPS
(Market, FRED, etc.) (fetch_*.py scripts) (normalize.py) (compute.py)


Automated nightly through GitHub Actions.  
Processed outputs live in:  
`data/processed/`

Dashboard visualization lives in Streamlit.

---

# 🧮 **4. Normalization Model (Intuition)**

AIBPS uses a **rolling Z-score → sigmoid transform**, which:

- Adapts to structural drift (e.g., markets trend over decades)  
- Preserves short-term deviations (bubble pressure signals)  
- Generates a unified 0–100 scale across domains  

Conceptually:

Step 1: Compare each value to its rolling mean (short-term deviation)
Step 2: Scale using rolling standard deviation (local extremeness)
Step 3: Smooth extremes with a sigmoid into 0–100 range


This allows credit spreads, capex, Google Trends, and market volatility to live on the same scale.

---

# 📈 **5. Composite Score Construction**

Final score = weighted average of normalized pillars:

AIBPS = Σ ( weight_i × pillar_i_normalized )


Default weights (equal):

Market, Credit, Capex, Infrastructure, Adoption, Sentiment = 1/6 each


Weights are editable in `config.yaml`.

---

# 🔍 **6. How to Interpret AIBPS Levels**

| AIBPS Range | Meaning | Interpretation |
|-------------|----------|----------------|
| **0–30** | Low Pressure | Underbuilding, stable markets, no bubble formation |
| **30–55** | Neutral | Mixed signals, rising investment, stable fundamentals |
| **55–75** | Elevated | Bubble formation zone; sentiment > fundamentals |
| **75–100** | Extreme | High systemic pressure; historically precedes sharp corrections |

This is not a timing tool — it’s a **stress diagnostician**.

---

# 🕰️ **7. Historical Anchors**

To contextualize modern AI dynamics, the dashboard marks:

- 📌 **Dot-Com Peak (Mar 2000)**  
- 📌 **Housing Bubble (2006)**  
- 📌 **Lehman Event (2008)**  
- 📌 **Generative AI Supercycle (2022–2025)**  

These help interpret whether today’s configuration resembles prior overheating regimes.

---

# 🌍 **8. Data Sources (Primary)**

### **Market**
- Yahoo Finance (indices + tickers)
- Semiconductor index (SOXX)
- Weighted AI megacap basket (NVDA, AMD, MSFT, GOOGL, META)

### **Credit**
- FRED High-Yield Option-Adjusted Spread  
- FRED Investment-Grade OAS  

### **Capex / Supply**
- PNFI (Private Nonresidential Fixed Investment)  
- UNXANO (Information Processing Equipment)  
- 10-K / 10-Q reported capex: NVDA, AMD, MSFT, GOOGL  

### **Infrastructure**
- Data center power/cooling (EIA, CBRE, Statista)
- Rackspace inventory trends
- GPU cluster availability (extensions planned)

### **Adoption**
- Enterprise AI penetration (McKinsey, Deloitte)
- Cloud AI spend
- Model API usage rates

### **Sentiment**
- Google Trends  
- Narrative intensity (GDELT – planned)  
- Social signals (future expansion)

---

# 🔮 **9. Planned Enhancements**

- AI Compute Cost Index  
- Token price inflation metrics  
- GPU market scarcity tracker  
- VC funding cycle indicators  
- NLP sentiment scoring (news + social media)  
- Regime-switching time-series overlays  
- Country-level divergence metrics  
- Bubble lifecycle classification  

---

# 📚 **10. Key References (APA)**

McKinsey Global Institute. (2023). *The State of AI in 2023.*  
OpenAI. (2024). *GPT-4 Technical Report.*  
Federal Reserve Bank of St. Louis. (2025). *FRED Economic Series.*  
CBRE Research. (2024). *North America Data Center Trends.*  
GDELT Project. (2024). *Global Narrative Database.*  
Statista. (2024). *AI Market Size and Adoption.*  

---

# 📎 **11. Document Purpose**

This **Overview** is meant to be:

- The *front door* for new readers  
- A conceptual introduction to the project  
- A high-level explanation of pillars, signals, and interpretation  
- A companion to the deeper docs (`methods.md`, `pillars.md`, etc.)

Technical details are in `methods.md`.  
Data definitions are in `pillars.md`.  
System diagrams are in `architecture.md`.

---

