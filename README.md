# 🚑 NYC Heat-Shield: Operational Resilience System
A predictive analytics system for NYC Emergency Services that forecasts ambulance demand surges during heatwaves using Machine Learning.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Framework](https://img.shields.io/badge/Framework-Marimo_Reactive-009688?logo=python&logoColor=white)
![Pipeline](https://img.shields.io/badge/Pipeline-ETL_%26_MLOps-blueviolet)
![Status](https://img.shields.io/badge/Status-Production_Ready-success)
![Accuracy](https://img.shields.io/badge/Model_R²-0.80-2ecc71)

## 📋 Executive Summary
**The Problem:** Extreme heat events create non-linear surges in emergency medical demand in dense urban environments. Traditional "static rostering" for ambulances fails to account for these rapid fluctuations, leading to increased response times and potential system failure.

**The Solution:** This project establishes a **Predictive Early-Warning System**. By harmonizing **NYC Open Data** (Emergency Dispatch Logs) with **ERA5 Historical Weather Reanalysis**, the system uses Machine Learning to forecast ambulance demand 24 hours in advance.

**The Impact:** The final model achieves **80% accuracy ($R^2 = 0.80$)**, providing municipal agencies with a reliable signal to trigger dynamic resource allocation (e.g., "Flex-Unit Activation") *before* a crisis peaks.

---
## 🏗️ Technical Architecture

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
