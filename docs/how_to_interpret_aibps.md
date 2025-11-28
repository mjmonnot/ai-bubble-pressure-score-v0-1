# 📘 1. Introduction
This guide explains how to read, navigate, and interpret the AIBPS dashboard.  
It is written for analysts, policymakers, investors, economists, and researchers interested in real-time indicators of AI-driven market pressure, hype cycles, systemic risk, and physical/economic constraints.

---

# 🖥️ 2. Dashboard Layout Overview

The dashboard is organized into six major sections:

1. **Main AIBPS Time Series (1980 → present)**  
   The core composite that synthesizes all pillars into a single 0–100 index.

2. **Regime Bands (Historical Context)**  
   Shaded ranges representing percentiles or risk zones.

3. **Pillar Trajectories**  
   Long-run 0–100 normalized trends for:
   - Market  
   - Credit  
   - Capex Supply  
   - Infrastructure  
   - Adoption  
   - Sentiment  

4. **Latest Pillar Contributions (Bar Chart)**  
   Shows which pillars are currently driving the composite score.

5. **Sub-Pillar Debug Panels (per pillar)**  
   Detailed raw + composite views for each underlying data source.

6. **Data Freshness & Raw Data Viewer**  
   Verifies whether the automated GitHub Actions update ran recently.

---

# 🎚️ 3. Interpreting the Main AIBPS Line

AIBPS (0–100):
- **0–20** = Historically low market pressure  
- **20–40** = Stable, low-risk conditions  
- **40–60** = Neutral zone  
- **60–80** = Elevated pressure  
- **80–100** = Historically extreme conditions

AIBPS_RA (smoothed):
- Removes short-term noise using a rolling average  
- Better for regime detection and trend following  
- Helps compare across multi-year cycles

---

# 🧭 4. Understanding the Pillars

Each pillar is normalized on a comparable 0–100 scale.

## Market  
Tracks prices & valuations (normalized to rolling z-sigmoid).

## Credit  
Tracks credit spreads and financing conditions (signal of stress or exuberance).

## Capex Supply  
Measures AI-related investment capacity from:
- Semiconductor fabs  
- Hyperscaler capex  
- Data-center construction  
- Equipment orders  

## Infrastructure  
Tracks compute, power, cooling, and network capacity indicators.

## Adoption  
Measures real enterprise and productivity adoption & labor substitution effects.

## Sentiment  
Quantifies hype, narrative pressure, and psychological momentum.

---

# 📉 5. Pillar Trajectory Panels

Each trajectory chart displays:
- Long-run normalized pillar line  
- Sub-pillars driving the composite  
- Periods of rapid acceleration or collapse  
- Alignment with historical events (dot-com, cloud boom, GPU shortage, etc.)

Usage:
- Identify leading vs lagging pillars  
- Assess where pressure is accumulating  
- Diagnose whether pressure is structural or narrative-driven

---

# 🧱 6. Sub-Pillar Debug Panels

Every pillar has a debug expander showing:
- Raw sub-pillar series  
- Monthly aligned versions  
- Composite sub-pillar indicator  
- Notes on missing or unavailable data  
- Value tails for sanity checks  
- Smoothing/normalization method used  

These panels support:
- Research replication  
- Transparency  
- Troubleshooting (e.g., failed FRED series)  
- Extending the dataset  

---

# 🧮 7. Pillar Contribution Bars

This panel answers:

**“What’s pushing the bubble pressure up right now?”**

Interpretation:
- Values > 0 → positive pressure contribution  
- Values < 0 → deflationary pressure  
- Large bars → major drivers of the current composite  
- Pale bars → pillars with insufficient or stale data  

Typical use:
- Diagnosing AI hype cycles  
- Stress-testing “is the bubble narrative justified?”  
- Comparing supply-side vs demand-side pressure  
- Tracking inflection points  

---

# 🚨 8. Regime Interpretation

Regime overlays show historical percentile bands:
- Grey bars = low-pressure  
- Yellow = elevated  
- Orange = stressed  
- Red = extreme bubble territory  

These help interpret *context*, not just raw values.

---

# 🔄 9. Automatic Updating

Data updates automatically via GitHub Actions:
- Runs daily at midnight UTC  
- Pulls FRED, Yahoo, and local/manual datasets  
- Builds processed CSVs  
- Recomputes pillar composites  
- Updates AIBPS/AIBPS_RA  
- Redeploys Streamlit  

You can verify freshness in the dashboard header.

---

# 📂 10. Viewing Raw Data

Use the "Raw Data" expander to inspect:
- aibps_monthly.csv  
- market_processed.csv  
- credit_fred_processed.csv  
- macro_capex_processed.csv  
- infra_processed.csv  
- adoption_processed.csv  
- sentiment_processed.csv  

Each file includes:
- A monthly DatetimeIndex  
- Sub-pillar columns  
- Composite pillar columns  

---

# 🛠️ 11. Customization & Weights

Users can modify:
- Pillar weights  
- Normalization methods  
- Smoothing windows  
- Sub-pillar construction  
- Date ranges  
- Regime percentile boundaries  

Changes apply immediately upon redeploy.

---

# 📈 12. Recommended Workflow for Analysts

1. Check AIBPS & AIBPS_RA for regime location  
2. Review pillar contributions  
3. Inspect sub-pillar debug views  
4. Compare historical context (dot-com, 2008, cloud boom, GPU booms)  
5. Assess which drivers are structural vs speculative  
6. Adjust weights if exploring alternative hypotheses  
7. Look for sudden acceleration in:
   - Market  
   - Capex  
   - Sentiment  

---

# 🔍 13. Interpretation Examples

**“AIBPS is rising while Market is flat.”**  
→ Narrative/sentiment or fundamental adoption is accelerating.

**“Credit spreads tight + capex exploding.”**  
→ High confidence cycle → overheating likely.

**“Sentiment collapsing but supply rising.”**  
→ Early-stage fundamental cycle, not a bubble.

**“AIBPS > 80 and all pillars accelerating.”**  
→ Historically rare → near bubble peak territory.

---

# 🧪 14. Troubleshooting

If values appear flat or NaN:
- Check FRED API key  
- Verify FRED series availability (some go stale)  
- Ensure monthly aligning isn’t dropping data  
- Look for name mismatches in compute.py  
- Inspect processed CSV tails via debug panels  

---
