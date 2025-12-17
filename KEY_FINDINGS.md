##  Key Findings & KPIs

| Metric | Result | Operational Analysis |
| :--- | :--- | :--- |
| **Model Accuracy** | **R² = 0.80** | The model captures **80% of demand variance**. This is a top-tier score for human-behavioral data (where 0.50 is typically considered "good"). |
| **Reaction Lag** | **0-4 Hours** | Granger Causality Tests confirm that heat spikes are a **leading indicator**, impacting call volume significantly within 4 hours. |
| **Primary Drivers** | **Routine + Heat** | Feature Importance reveals that `Lag_24` (Daily Cycle) and `Temperature` are the dominant predictors, with `Day_of_Week` providing fine-tuning. |
| **Stress Test** | **+20% Surge** | A simulation of a **40°C (104°F) Saturday** predicts call volumes exceeding baseline capacity by 20%. |
