import duckdb
import pandas as pd
from prophet import Prophet

# Configuration
DB_NAME = "nyc_ems.db"

def train_and_predict():
    print("Loading Data from Database...")
    con = duckdb.connect(DB_NAME)
    
    try:
        query = "SELECT date_trunc('hour', incident_datetime) as ds, count(*) as y FROM raw_ems GROUP BY ds ORDER BY ds"
        df = con.execute(query).df()
    except Exception as e:
        print(f"Error: Database not ready. Run live_engine.py first. Details: {e}")
        return
    con.close()

    if len(df) < 24:
        print("Error: Not enough data for forecasting (Need > 24 hours).")
        return

    print(f"Training AI on {len(df)} hours of history...")

    # Initialize Prophet Model
    m = Prophet(daily_seasonality=True, weekly_seasonality=True)
    m.fit(df)
    
    # Predict Next 7 Days (168 Hours)
    future = m.make_future_dataframe(periods=168, freq='H')
    forecast = m.predict(future)
    
    # Save Prediction
    future_forecast = forecast.tail(168)
    
    con = duckdb.connect(DB_NAME)
    con.execute("CREATE OR REPLACE TABLE forecast_results AS SELECT ds, yhat, yhat_lower, yhat_upper FROM future_forecast")
    con.close()
    
    print("Forecast generated and saved to DB.")
    print(f"Peak Demand: {future_forecast['yhat'].max():.0f} ambulances/hour")

if __name__ == "__main__":
    train_and_predict()
