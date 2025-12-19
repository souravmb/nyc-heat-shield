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
    return asyncio, duckdb, go, mo, os, pd, px, sys

@app.cell
def title(mo):
    mo.md("#  NYC Heat-Shield: Command Center")
    return

@app.cell
async def load_data(asyncio, duckdb, mo, os, sys):
    # --- THE LOADER ---
    # This cell controls everything. It won't let the rest of the app run
    # until the database is downloaded and ready.
    
    status = mo.md(" **Initializing System...**")
    
    # 1. Check if we are on the web (Pyodide)
    if "pyodide" in sys.modules:
        status = mo.md("🌐 **Downloading Data from Cloud...**")
        from pyodide.http import pyfetch
        
        # Download the file
        response = await pyfetch("nyc_ems.db")
        with open("nyc_ems.db", "wb") as f:
            f.write(await response.bytes())
            
    # 2. Connect to the Database
    if os.path.exists("nyc_ems.db"):
        con = duckdb.connect("nyc_ems.db", read_only=True)
        status = mo.md(" **System Online**")
    else:
        con = None
        status = mo.callout(" Error: Database file not found.", kind="danger")

    return con, status

@app.cell
def show_kpis(con, mo):
    # Stop here if no connection
    if con is None:
        return
        
    # KPI Logic
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
    return kpi_latest, kpi_load, kpi_status, kpi_total

@app.cell
def show_forecast(con, go, mo):
    if con is None:
        return
        
    try:
        # Fetch Data
        fc_df = con.execute("SELECT * FROM forecast_results").df()
        hist_df = con.execute("SELECT date_trunc('hour', incident_datetime) as ds, count(*) as y FROM raw_ems WHERE incident_datetime > (SELECT MAX(incident_datetime) - INTERVAL 3 DAY FROM raw_ems) GROUP BY ds ORDER BY ds").df()
        
        # Build Chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hist_df['ds'], y=hist_df['y'], mode='lines', name='History', line=dict(color='gray')))
        fig.add_trace(go.Scatter(x=fc_df['ds'], y=fc_df['yhat'], mode='lines', name='AI Forecast', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=list(fc_df['ds'])+list(fc_df['ds'])[::-1], y=list(fc_df['yhat_upper'])+list(fc_df['yhat_lower'])[::-1], fill='toself', fillcolor='rgba(0,0,255,0.1)', line=dict(color='rgba(0,0,0,0)'), name='Confidence'))
        
        fig.update_layout(title="7-Day Demand Forecast", xaxis_title="Time", yaxis_title="Ambulance Demand")
        mo.ui.plotly(fig)
    except:
        mo.md(" Forecast not ready yet.")
    return fc_df, fig, hist_df

@app.cell
def show_map(con, mo, px):
    if con is None:
        return

    try:
        map_df = con.execute("SELECT borough, count(*) as calls FROM raw_ems GROUP BY borough ORDER BY calls DESC").df()
        map_fig = px.bar(map_df, x="borough", y="calls", color="calls", title="Risk by Borough", color_continuous_scale="Reds")
        mo.ui.plotly(map_fig)
    except:
        pass
    return map_df, map_fig
