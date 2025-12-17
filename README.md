#  NYC Heat-Shield: Operational Resilience System
A predictive analytics system for NYC Emergency Services that forecasts ambulance demand surges during heatwaves using Machine Learning.
**Data from** https://data.cityofnewyork.us/resource/76xm-jjuj.csv
### Analysis Python file: app.py

### https://souravmb.github.io/nyc-heat-shield/

---

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Framework](https://img.shields.io/badge/Framework-Marimo_Reactive-009688?logo=python&logoColor=white)
![Pipeline](https://img.shields.io/badge/Pipeline-ETL_%26_MLOps-blueviolet)
![Status](https://img.shields.io/badge/Status-Production_Ready-success)
![Accuracy](https://img.shields.io/badge/Model_R²-0.80-2ecc71)

---

##  Executive Summary
**The Problem:** Extreme heat events create non-linear surges in emergency medical demand in dense urban environments. Traditional "static rostering" for ambulances fails to account for these rapid fluctuations, leading to increased response times and potential system failure.

**The Solution:** This project establishes a **Predictive Early-Warning System**. By harmonizing **NYC Open Data** (Emergency Dispatch Logs) with **ERA5 Historical Weather Reanalysis**, the system uses Machine Learning to forecast ambulance demand 24 hours in advance.

**The Impact:** The final model achieves **80% accuracy ($R^2 = 0.80$)**, providing municipal agencies with a reliable signal to trigger dynamic resource allocation (e.g., "Flex-Unit Activation") *before* a crisis peaks.

---

## Key Findings

### 1. Causality Proven 
* **Leading Indicator:** Statistical testing (Granger Causality) confirms that temperature spikes are a significant leading indicator ($p < 0.05$) for EMS demand.
* **Reaction Time:** The system shows a systemic reaction within **0 to 4 hours** of a heat event, validating the need for rapid-response protocols.

### 2. High Predictive Accuracy 
* **Performance:** The Random Forest model achieved an **$R^2$ of 0.80**, capturing 80% of the variance in ambulance demand.
* **Benchmark:** This result significantly outperforms standard operational baselines (typically 0.50–0.60 for complex human behavior), confirming production readiness.

### 3. Primary Drivers of Stress 
Feature importance analysis identified the three critical forces acting on the system:
1.  **System Inertia:** Recent call volume (past 24h) is the strongest predictor of near-future demand.
2.  **Thermal Stress:** Heat is the primary environmental variable pushing the system from "Normal" to "Critical."
3.  **Social Factors:** Weekends (Saturday/Sunday) amplify stress, likely due to increased social activity.

### 4. Vulnerability Assessment 
* **Scenario:** A simulated **40°C (104°F)** heatwave on a Saturday.
* **Impact:** Predicted call volume surges **+20% above seasonal norms**.
* **Conclusion:** Current static rosters would likely be overwhelmed, necessitating dynamic "Flex-Unit" activation.

---

## Technology Stack
### 1. Ingestion:
Requests, SODA API (NYC Open Data), Open-Meteo API
### 2. Processing:
Pandas (Time-series discretization, timezone alignment)
### 3. Statistics:
Statsmodels (Granger Causality Tests)
### 4. Machine Learning:
Scikit-Learn (Random Forest Regressor, Train-Test Split)
### 5. Visualization:
Plotly (Interactive Heatmaps & Line Charts)
### 6. Environment:
Marimo (Reactive Python Notebooks)

---

## How to Run:
This project utilizes Marimo, a next-generation reactive notebook that guarantees reproducibility (no hidden state).

-**Clone the Repository:**  git clone [https://github.com/souravmb/nyc-heat-shield.git](https://github.com/souravmb/nyc-heat-shield.git) 
cd nyc-heat-shield

-**Install Dependencies:** marimo>=0.1.0,
pandas>=2.0.0,
numpy,
requests,
requests-cache,
retry-requests,
openmeteo-requests,
scikit-learn,
statsmodels,
plotly

-**Lauch the Dashboard:** marimo edit app.py

---

##  Technical Architecture

The system follows a strict **ETL (Extract, Transform, Load)** and **MLOps** workflow.

```text
┌─────────────────────────┐       ┌─────────────────────────┐
│  NYC Open Data API      │       │  Open-Meteo Weather API │
│  (EMS Dispatch Logs)    │       │  (ERA5 Historical Data) │
└────────────┬────────────┘       └────────────┬────────────┘
             │                                 │
             ▼                                 ▼
   ┌─────────────────────────────────────────────────────┐
   │          PHASE 1: INGESTION & PROCESSING            │
   │  • SODA API Streaming                               │
   │  • Pandas Time-Series Binning (Hourly)              │
   │  • Inner-Join Harmonization                         │
   └──────────────────────────┬──────────────────────────┘
                              │
                              ▼
   ┌─────────────────────────────────────────────────────┐
   │          PHASE 2 & 3: ANALYTICS CORE                │
   │  • Inference: Granger Causality Tests (p < 0.05)    │
   │  • Modeling: Random Forest Regressor (Scikit-Learn) │
   │  • Optimization: Feature Engineering (Lags/Day)     │
   └──────────────────────────┬──────────────────────────┘
                              │
                              ▼
   ┌─────────────────────────────────────────────────────┐
   │          PHASE 4: DEPLOYMENT & REPORTING            │
   │  • Scenario Simulator (Stress-Testing)              │
   │  • Marimo Interactive Dashboard                     │
   │  • Executive CSV Export                             │
   └─────────────────────────────────────────────────────┘


