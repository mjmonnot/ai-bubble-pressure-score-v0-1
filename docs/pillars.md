# 🏛 AIBPS Pillars
### Detailed definitions of all six core pillars in the AI Bubble Pressure Score

_Last updated: {{ auto-updated }}_

---

# 📌 Overview

The AIBPS is built from **six independent pillars**, each chosen because it reflects a distinct subsystem of the AI economy:

1. **Market Valuation**
2. **Credit & Funding Conditions**
3. **Capex / Supply Investment**
4. **Infrastructure Stress**
5. **AI Adoption Velocity**
6. **Sentiment / Hype Intensity**

Each pillar is transformed into a **0–100 pressure scale** using the normalization logic described in `methods.md`.

This document explains:

- what each pillar measures  
- why it matters  
- how it is built  
- what “high pressure” means  
- current limitations and future planned improvements  

---

# 1️⃣ Market Pillar  
**What it measures:**  
Systemic pricing pressure in AI-linked assets.

**Data sources**  
- Nasdaq-100 (QQQ)  
- Global Semiconductors ETF (SOXX)  
- NVDA & AMD (optional extension)  
- AI thematic ETFs (ex: BOTZ, ARKQ)  
- Tech momentum regimes  

**Why it matters**  
Market valuations are the fastest-moving signal of speculative pressure.  
AI-linked equities often undergo momentum cascades before downstream fundamentals turn.

**Interpretation**  
- **Low (0–30)** — depressed valuations, low speculative heat  
- **Medium (30–60)** — healthy regime  
- **High (60–80)** — frothy valuations, dislocation from fundamentals  
- **Very High (80–100)** — speculative regime historically aligned with bubble peaks  

**Future enhancements**  
- Options implied volatility skew  
- Equity risk premium decomposition  
- NLP on earnings-call mentions of “AI”  

---

# 2️⃣ Credit Pillar  
**What it measures:**  
The *cost and availability of capital* for AI expansion.

**Data sources**  
- HY OAS (High-Yield Credit Spreads)  
- IG OAS (Investment-Grade Spreads)  
- Venture funding conditions (future)  
- Bank lending standards (future)  

**Why it matters**  
AI expansion relies on massive capital expenditure.  
When credit is **tight**, bubbles tend to burst; when it is **loose**, bubbles inflate.

**Interpretation**  
- **Low pressure** → cheap credit, easy money  
- **Medium** → neutral conditions  
- **High pressure** → credit stress rising  
- **Critical** → funding constraints likely  

**Future enhancements**  
- NVCA venture funding index  
- LQD/HYG ratios  
- Fed Senior Loan Officer Survey integrations  

---

# 3️⃣ Capex / Supply Pillar  
**What it measures:**  
Physical investment cycles tied to AI compute, hardware, and datacenter construction.

**Data sources**  
- FRED PNFI (Private Nonresidential Fixed Investment)  
- FRED UNXANO (Mfg Construction Spending)  
- Cloud hyperscaler capex (manual ingest)  
- Semiconductor fab spending (semi-auto pipeline planned)  

**Why it matters**  
Capex bubbles form when firms over-invest relative to real demand (e.g., fiber boom 1999, shale boom 2012).

This pillar helps identify **supply gluts** forming before price collapses.

**Interpretation**  
- **Low (<30)** → underinvestment relative to demand  
- **Medium (30–60)** → balanced  
- **High (60–80)** → aggressive buildout  
- **Critical (>80)** → historical precursor to correction  

**Future enhancements**  
- TSMC, Samsung, Intel capex ingestion  
- AI robotics + automated warehouse capex  
- GPU supply curve modeling  

---

# 4️⃣ Infrastructure Pillar  
**What it measures:**  
Strain in the physical systems required to deploy AI at scale.

**Data sources**  
- FRED electricity/industrial power metrics  
- Cooling equipment production indices  
- Land & industrial construction data  
- Grid load & data center strain proxies  
- (Future) ISO grid operator real-time load  

**Why it matters**  
Even if demand is high, **physical constraints** (power, cooling, land) can limit AI growth.  
When infrastructure strain rises, speculative expansion outruns real capacity.

**Interpretation**  
- **Low** → ample capacity  
- **Medium** → early bottlenecks  
- **High** → cooling/power shortages  
- **Critical** → unmet demand + capex overshoot  

**Future enhancements**  
- DOE electricity data  
- Data center water/power availability indexes  
- GPU lead-time models  

---

# 5️⃣ Adoption Pillar  
**What it measures:**  
How quickly AI is being integrated into business workflows and consumer behavior.

**Data sources**  
- BLS productivity proxies (future)  
- App usage metrics (manual ingest)  
- Enterprise adoption surveys (semi-auto planned)  
- Hiring patterns in AI-related roles  
- Vector index of AI mentions in job postings  

**Why it matters**  
Bubbles inflate fastest when **adoption lags hype**.  
Real economic absorption matters more than valuation.

**Interpretation**  
- **Low** → weak adoption  
- **Medium** → steady uptake  
- **High** → accelerated incorporation  
- **Critical** → overheating + overinvestment  

**Future enhancements**  
- Indeed / LinkedIn AI hiring index  
- GitHub AI repo velocity  
- Enterprise LLM deployment benchmarks  

---

# 6️⃣ Sentiment Pillar  
**What it measures:**  
Narrative hype and attention intensity around AI.

**Data sources**  
- Google Trends: “AI”, “Artificial Intelligence”, “ChatGPT”, “Generative AI”, “OpenAI”  
- (Future) News-based sentiment  
- (Future) X/Twitter hype metrics  
- (Future) Academic publication explosion  

**Why it matters**  
Sentiment often **peaks before fundamentals** — a classic bubble signature.

**Interpretation**  
- **Low** → narrative uninterested  
- **Medium** → steady interest  
- **High** → public mania phase  
- **Critical** → narrative fever historically seen at bubble tops  

**Future enhancements**  
- NLP tone scoring  
- Venture pitchdeck sentiment  
- Social-media hype acceleration  

---

# 🔗 Cross-Pillar Logic

Each pillar captures a *different form* of systemic heat:

| Pillar | What it captures |
|-------|------------------|
| Market | Valuation pressure |
| Credit | Financial conditions |
| Capex | Investment cycle pressure |
| Infrastructure | Physical constraints |
| Adoption | Real economy absorption |
| Sentiment | Narrative intensity |

The composite is a **mean of normalized pillars**, weighted evenly unless overridden in `config.yaml`.

---

# 🧩 Limitations & Caveats

- Early data stages rely partly on auto-structured FRED or synthetic seeds.  
- Sentiment metrics are limited by Google’s rate limits.  
- Adoption metrics remain partially manual until additional APIs are integrated.  
- Normalization assumes stationarity within each rolling window.  

---

# 📘 See Also

- **overview.md** — high-level intro  
- **methods.md** — full computational math  
- **architecture.md** — data pipeline diagrams  
- **changelog.md** — update history  

---

# 📝 Citation (APA)

Monnot, M. J. (2025). *AI Bubble Pressure Score (AIBPS): A multi-pillar composite index for systemic AI market pressure*.  
https://github.com/mjmonnot/aibps-v0-1

