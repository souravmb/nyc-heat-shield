import pandas as pd
import requests
from sodapy import Socrata
import duckdb

# Configuration
NYC_DATA_URL = "data.cityofnewyork.us"
EMS_DATASET_ID = "76xm-jjuj"
DB_NAME = "nyc_ems.db"

def fetch_live_ems_data(limit=50000):
    print(f"Connecting to NYC Open Data (Fetching last {limit} calls)...")
    
    client = Socrata(NYC_DATA_URL, None)
    
    try:
        results = client.get(EMS_DATASET_ID, limit=limit, order="incident_datetime DESC")
    except Exception as e:
        print(f"API Error: {e}")
        return pd.DataFrame()
    
    df = pd.DataFrame.from_records(results)
    if df.empty:
        return df
        
    df['incident_datetime'] = pd.to_datetime(df['incident_datetime'])
    
    # Select specific columns
    cols = ['incident_datetime', 'borough', 'zipcode', 'incident_dispatch_area', 'final_call_type']
    existing_cols = [c for c in cols if c in df.columns]
    df = df[existing_cols]
    
    print(f"Downloaded {len(df)} incidents.")
    if not df.empty:
        print(f"Latest Call: {df['incident_datetime'].max()}")
    return df

def fetch_weather_forecast():
    print("Fetching 7-Day Weather Forecast...")
    
    params = {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "hourly": "temperature_2m,relative_humidity_2m",
        "forecast_days": 7
    }
    
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        resp = requests.get(url, params=params)
        data = resp.json()
        
        df = pd.DataFrame({
            'time': pd.to_datetime(data['hourly']['time']),
            'temp_c': data['hourly']['temperature_2m'],
            'humidity': data['hourly']['relative_humidity_2m']
        })
        print(f"Downloaded Forecast ({len(df)} hours).")
        return df
    except Exception as e:
        print(f"Weather API Error: {e}")
        return pd.DataFrame()

def update_database():
    ems_df = fetch_live_ems_data()
    weather_df = fetch_weather_forecast()
    
    if ems_df.empty:
        print("CRITICAL ERROR: No EMS data fetched. Aborting update.")
        return

    # Save to DuckDB
    con = duckdb.connect(DB_NAME)
    print(f"Saving to {DB_NAME}...")
    
    con.execute("CREATE OR REPLACE TABLE raw_ems AS SELECT * FROM ems_df")
    
    if not weather_df.empty:
        con.execute("CREATE OR REPLACE TABLE forecast AS SELECT * FROM weather_df")
        
    con.close()
    print("ENGINE UPDATE COMPLETE. Database is ready.")

if __name__ == "__main__":
    update_database()
