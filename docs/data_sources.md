# 📊 Data Sources for the AI Bubble Pressure Score (AIBPS)

_Last updated: {{DATE}}_  

This document describes all **data sources** used (or planned) for the AI Bubble Pressure Score, including:

- Implemented pillars and their inputs  
- How those inputs are transformed  
- Planned / future inputs and recommended sources  
- Known limitations and reliability caveats  

It complements `methods.md` (how we compute) and `pillars.md` (what each pillar conceptually represents).

---

## 1. Overview

AIBPS uses a layered data architecture:

- Raw data lake:  
    - `data/raw/`
- Processed pillar series:  
    - `data/processed/*_processed.csv`
- Composite output:  
    - `data/processed/aibps_monthly.csv`
- Compute & normalization:  
    - `src/aibps/normalize.py`  
    - `src/aibps/compute.py`

Core upstream sources:

- Yahoo Finance (market prices)
- FRED (macro & credit spreads)
- Google Trends (public attention / sentiment)
- Manual or semi-automatic CSVs (adoption, infra; currently placeholders)
- Future APIs (GPU supply, VC funding, hyperscaler capex, etc.)

---

## 2. Data Dictionary (High Level)

Columns in `aibps_monthly.csv`:

- `Market`  
  AI-sensitive market valuation pressure (0–100).

- `Credit`  
  Credit conditions / funding stress (0–100).

- `Capex_Supply`  
  Supply-side buildout / investment pressure (0–100).

- `Infra`  
  Infrastructure strain (power / construction proxies) (0–100).

- `Adoption`  
  AI adoption intensity (0–100).

- `Sentiment`  
  Hype / attention intensity (0–100).

- `AIBPS`  
  Raw composite bubble pressure (0–100).

- `AIBPS_RA`  
  Rolling-adjusted / smoothed composite (0–100).

---

## 3. Implemented Pillar Data

### 3.1 Market Pillar

**Purpose:** capture speculative pricing and valuation pressure in AI-linked assets.

**Current sources (via Yahoo Finance / yfinance):**

- NVDA (NVIDIA)
- QQQ (NASDAQ-100 ETF)
- SOXX (semiconductor ETF)

**Transformations:**

- Download daily closes
- Resample to month-end closes
- Construct an equal-weight composite (NVDA, QQQ, SOXX)
- Apply rolling z-score (about 60-month window)
- Apply sigmoid to map into a 0–100 pressure metric

**Coverage:**  
Limited by common overlap of tickers; practically strong after ~2015.

---

### 3.2 Credit Pillar

**Purpose:** capture liquidity regime and credit conditions that fund AI booms.

**Current sources (via FRED API):**

- A high-yield corporate OAS series (HY credit spread)
- An investment-grade OAS or corporate spread series

Exact series names depend on your current `fetch_credit.py` implementation and successful calls under your FRED key.

**Transformations:**

- Monthly data as provided by FRED or resampled to month-end
- Wider spreads interpreted as higher systemic stress
- Rolling z-score (approximately 60-month window)
- Sigmoid mapping to 0–100

**Coverage:**  
Good coverage back to 1980+, enabling deep historical comparison.

---

### 3.3 Capex / Supply Pillar

**Purpose:** track real-economy investment cycles relevant to AI infrastructure.

**Current sources (via FRED API):**

- PNFI – Private Nonresidential Fixed Investment
- UNXANO – Construction spending series (power / manufacturing / communications, depending on configuration)

**Transformations:**

- Resample / align to monthly where necessary
- Compute change metrics (for example, year-over-year or multi-period growth)
- Blend PNFI and UNXANO into a single supply-side index
- Rolling z-score (about 24-month window)
- Sigmoid to 0–100 Capex_Supply pressure

**Coverage:**  
Back to 1980 in most cases, robust for multi-cycle analysis.

---

### 3.4 Infrastructure Pillar

**Purpose:** capture physical constraints and build-out for AI-related infrastructure.

**Current state:**

- Uses proxies and/or placeholder series, with logic in `fetch_infra.py`.

**Typical target series (future / partial):**

- Electric power generation metrics
- Construction spending in data centers, utilities, and industrial infrastructure
- Manufacturing capacity indices related to electrical / cooling equipment

**Transformations:**

- Monthly alignment
- Rolling z-score (around 36-month window)
- Sigmoid to 0–100 Infra pressure

**Note:**  
At present, infra is partly synthetic or proxy-based; this is a priority area for future, more granular data feeds.

---

### 3.5 Adoption Pillar

**Purpose:** estimate real AI adoption by enterprises and consumers.

**Current state:**

- Constructed from a manual or placeholder CSV (for example, annual or quarterly adoption indices then resampled to monthly).
- Values normalized and then transformed into a 0–100 score.

**Intended future sources:**

- Enterprise AI adoption surveys
- AI usage surveys by consulting firms
- AI share of workloads, projects, or IT budgets

**Transformations:**

- Rescale raw adoption index (0–100 or 0–1)
- Rolling z-score (about 24-month window)
- Sigmoid mapping to 0–100 Adoption

**Caveat:**  
Current series may be flat or synthetic; once real data is wired in, this pillar will carry more signal.

---

### 3.6 Sentiment Pillar

**Purpose:** track hype cycles and narrative intensity around AI.

**Current sources (via Google Trends, when not rate-limited):**

Search terms such as:
- "artificial intelligence"
- "generative ai"
- "machine learning"
- "chatgpt"
- "openai"

**Transformations:**

- Fetch weekly normalized interest
- Aggregate across multiple terms (e.g., average or weighted blend)
- Resample to monthly
- Apply rolling z-score (circa 24-month window)
- Sigmoid mapping to 0–100 Sentiment

**Coverage:**

- Google Trends data begins around 2004
- Prior history (1980–2003) may be blank or seeded with synthetic placeholders

**Limitations:**

- Google Trends is a relative index (0–100) per query over its own selected range
- Subject to rate limits (e.g., HTTP 429 errors)
- Cannot be interpreted as an absolute global volume of mentions

---

## 4. Normalization Notes (Shared Across Data)

All implemented pillars undergo a **common normalization approach** defined in `normalize.py` and configured via `config.yaml`.

**General pattern:**

1. Align each raw series to a monthly date index.
2. Apply a rolling window to compute mean and standard deviation.
3. Compute rolling z-scores and clip to a finite range (for example, from -4 to +4).
4. Pass the clipped z-score through a sigmoid function.
5. Multiply by 100 to obtain a 0–100 pressure score.

Typical configuration for a pillar:

- Method: rolling_z_sigmoid
- Params:
    - window: 24 to 60 months (pillar-specific)
    - z_clip: 4.0

This ensures:

- Pillars are on a comparable 0–100 scale
- Outliers do not dominate
- Each pillar is sensitive to relative changes within its own historical context

---

## 5. Planned / Future Pillars and Sub-Inputs

The pipeline is designed to accept additional, more granular inputs as they become available. Some planned or conceptual data sources:

### 5.1 GPU / Compute Supply (Future)

**Goal:** quantify tightness or glut in AI compute supply.

Potential sources:

- NVIDIA data center unit shipments (from 10-Q and 10-K filings)
- Mercury Research GPU unit and ASP reports
- TSMC revenue by high-performance computing segments
- Trade or export datasets for GPU-related HS codes

---

### 5.2 Cloud / Hyperscaler Capex (Future)

**Goal:** track hyperscaler-level AI investment capacity and cycles.

Potential sources:

- AWS, Azure, Google Cloud capex from public filings
- Synergy Research or Canalys cloud capex index
- IDC or Gartner reports on cloud infrastructure spending

---

### 5.3 VC / Startup Funding (Future)

**Goal:** capture private-market bubble dynamics.

Potential sources:

- PitchBook (AI-related VC deals)
- Crunchbase (AI-tagged startups)
- CB Insights emerging tech indices
- NVCA Yearbook

---

### 5.4 AI Labor Market / Talent (Future)

**Goal:** track hiring cycles, skills demand, and talent overheating.

Potential sources:

- Lightcast / Burning Glass job posting analytics
- Indeed or LinkedIn job postings for AI roles
- BLS occupational data for AI/ML-related occupations

---

### 5.5 AI Regulation / Policy Heat (Future)

**Goal:** measure the regulatory and political pressure around AI.

Potential sources:

- GDELT topic/tone indices for AI-related news
- Legislative / regulatory tracking (EU AI Act, NIST, etc.)
- Congressional or parliamentary hearings metadata

---

## 6. Recommended Upgrades for Each Pillar

When expanding beyond current proxies, recommended best-in-class data:

- Market: CRSP / Compustat, Bloomberg sector indices, AI thematic indices
- Credit: ICE BofA OAS indices for HY and IG
- Capex: BEA detailed fixed-investment tables and sector-level FRED series
- Infra: FERC, EIA, and utility-level power capacity filings
- Adoption: Stanford AI Index, McKinsey AI adoption data, vendor usage metrics
- Sentiment: GDELT, news sentiment models, social-media text embeddings

---

## 7. Reliability, Bias, and Limitations

- **Revision risk**: FRED series can be revised retrospectively.
- **Coverage gaps**: Some pillars start later (e.g., Google Trends in 2004), limiting early history.
- **Synthetic placeholders**: Until fully replaced, certain series are partly synthetic and should not be interpreted as real historical facts.
- **Nonlinearity**: Upstream sources (like Google Trends) are not linear counts, but normalized scales.
- **Sampling bias**: Survey-based adoption data tends to overrepresent larger firms or tech-forward respondents.

These limitations are mitigated by:

- Using relative, rolling-window normalization
- Treating some pillars as directional rather than absolute
- Documenting synthetic vs real series clearly

---

## 8. Appendix: Raw → Processed File Map

Current (or planned) mapping:

- `data/raw/market_prices.csv`  
  → `data/processed/market_processed.csv`  

- `data/raw/credit_fred.csv`  
  → `data/processed/credit_fred_processed.csv`  

- `data/raw/macro_capex.csv`  
  → `data/processed/macro_capex_processed.csv`  

- `data/raw/infra.csv`  
  → `data/processed/infra_processed.csv`  

- `data/raw/adoption.csv`  
  → `data/processed/adoption_processed.csv`  

- `data/raw/sentiment.csv`  
  → `data/processed/sentiment_processed.csv`  

Composite output:

- `data/processed/aibps_monthly.csv`  
  (includes Market, Credit, Capex_Supply, Infra, Adoption, Sentiment, AIBPS, AIBPS_RA)

---

_End of data_sources.md_
``
::contentReference[oaicite:0]{index=0}
