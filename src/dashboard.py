import marimo

__generated_with = "0.1.0"
app = marimo.App()

@app.cell
def setup():
    import marimo as mo
    import duckdb
    import pandas as pd
    import plotly.graph_objects as go
    import plotly.express as px
    import sys
    import os
    import asyncio

    # --- TELEPORTER (For GitHub Pages) ---
    async def mount_db():
        if "pyodide" in sys.modules:
            from pyodide.http import pyfetch
            print(" Downloading Database...")
            response = await pyfetch("nyc_ems.db")
            with open("nyc_ems.db", "wb") as f:
                f.write(await response.bytes())
            print(" Database mounted.")
    
    # Run download if in browser
    try:
        loop = asyncio.get_running_loop()
        if loop.is_running():
            loop.create_task(mount_db())
    except RuntimeError:
        pass
        
    return asyncio, duckdb, go, mo, mount_db, os, pd, px, sys

@app.cell
def show_title(mo):
    mo.md("#  NYC Heat-Shield: Command Center")
    return

@app.cell
def connect_db(duckdb, os):
    # Connect to Database
    # We check if file exists to avoid crashing before the download finishes
    if os.path.exists("nyc_ems.db"):
        con = duckdb.connect("nyc_ems.db", read_only=True)
        status_msg = " Online"
    else:
        con = None
        status_msg = " Loading Data... (Refresh if stuck)"
    return con, status_msg

@app.cell
def show_kpis(con, mo, status_msg):
    # --- KPI SECTION ---
    # Using unique names: kpi_total, kpi_load, etc.
    if con is None:
        mo.md(f"**Status:** {status_msg}")
        kpi_total, kpi_latest, kpi_load, kpi_status = None, None, None, None
    else:
        try:
            kpi_total = con.execute("SELECT COUNT(*) FROM raw_ems").fetchone()[0]
            kpi_latest = con.execute("SELECT MAX(incident_datetime) FROM raw_ems").fetchone()[0]
            
            kpi_load = con.execute("SELECT count(*) FROM raw_ems WHERE incident_datetime > (SELECT MAX(incident_datetime) - INTERVAL 6 HOUR FROM raw_ems)").fetchone()[0]
            
            kpi_status = "Normal"
            if kpi_load > 400: kpi_status = "HIGH SURGE"
            elif kpi_load > 200: kpi_status = "Elevated"
            
            mo.hstack([
                mo.stat("Total Incidents", f"{kpi_total:,}"),
                mo.stat("Latest Update", str(kpi_latest)),
                mo.stat("6-Hour Load", f"{kpi_load}", caption=kpi_status)
            ])
        except Exception as e:
            mo.md(f" Data Error: {e}")
            kpi_total, kpi_latest, kpi_load, kpi_status = None, None, None, None
            
    return kpi_latest, kpi_load, kpi_status, kpi_total

@app.cell
def show_forecast(con, go, mo):
    # --- FORECAST CHART SECTION ---
    # Using unique names: forecast_df, history_df, forecast_fig
    if con:
        try:
            forecast_df = con.execute("SELECT * FROM forecast_results").df()
            history_df = con.execute("SELECT date_trunc('hour', incident_datetime) as ds, count(*) as y FROM raw_ems WHERE incident_datetime > (SELECT MAX(incident_datetime) - INTERVAL 3 DAY FROM raw_ems) GROUP BY ds ORDER BY ds").df()
            
            forecast_fig = go.Figure()
            # Plot History
            forecast_fig.add_trace(go.Scatter(x=history_df['ds'], y=history_df['y'], mode='lines', name='History', line=dict(color='gray')))
            # Plot Prediction
            forecast_fig.add_trace(go.Scatter(x=forecast_df['ds'], y=forecast_df['yhat'], mode='lines', name='AI Forecast', line=dict(color='blue')))
            # Plot Confidence
            forecast_fig.add_trace(go.Scatter(x=list(forecast_df['ds'])+list(forecast_df['ds'])[::-1], y=list(forecast_df['yhat_upper'])+list(forecast_df['yhat_lower'])[::-1], fill='toself', fillcolor='rgba(0,0,255,0.1)', line=dict(color='rgba(0,0,0,0)'), name='Confidence'))
            
            forecast_fig.update_layout(title="7-Day Demand Forecast", xaxis_title="Time", yaxis_title="Ambulance Demand")
            mo.ui.plotly(forecast_fig)
        except:
            mo.md(" Forecast not ready yet.")
            forecast_df, history_df, forecast_fig = None, None, None
    else:
        forecast_df, history_df, forecast_fig = None, None, None
        
    return forecast_df, forecast_fig, history_df

@app.cell
def show_map(con, mo, px):
    # --- MAP SECTION ---
    # Using unique names: borough_df, borough_fig
    if con:
        try:
            borough_df = con.execute("SELECT borough, count(*) as calls FROM raw_ems GROUP BY borough ORDER BY calls DESC").df()
            borough_fig = px.bar(borough_df, x="borough", y="calls", color="calls", title="Risk by Borough", color_continuous_scale="Reds")
            mo.ui.plotly(borough_fig)
        except:
            borough_df, borough_fig = None, None
    else:
        borough_df, borough_fig = None, None
        
    return borough_df, borough_fig
