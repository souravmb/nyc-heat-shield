import marimo

__generated_with = "0.1.0"
app = marimo.App()

@app.cell
def _():
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
            print("🌐 Downloading Database...")
            response = await pyfetch("nyc_ems.db")
            with open("nyc_ems.db", "wb") as f:
                f.write(await response.bytes())
            print("Database mounted.")
    
    # Run download if in browser
    try:
        loop = asyncio.get_running_loop()
        if loop.is_running():
            loop.create_task(mount_db())
    except RuntimeError:
        pass
        
    return asyncio, duckdb, go, mo, mount_db, os, pd, px, sys

@app.cell
def _(mo):
    mo.md("# NYC Heat-Shield: Command Center")
    return

@app.cell
def _(duckdb, os):
    # Connect to Database
    if os.path.exists("nyc_ems.db"):
        con = duckdb.connect("nyc_ems.db", read_only=True)
        status_msg = " Online"
    else:
        con = None
        status_msg = " Loading Data... (Refresh if stuck)"
    return con, status_msg

@app.cell
def _(con, mo, status_msg):
    # --- KPI SECTION ---
    if con is None:
        mo.md(f"**Status:** {status_msg}")
        latest, load, status, total = None, None, None, None
    else:
        try:
            total = con.execute("SELECT COUNT(*) FROM raw_ems").fetchone()[0]
            latest = con.execute("SELECT MAX(incident_datetime) FROM raw_ems").fetchone()[0]
            
            load = con.execute("SELECT count(*) FROM raw_ems WHERE incident_datetime > (SELECT MAX(incident_datetime) - INTERVAL 6 HOUR FROM raw_ems)").fetchone()[0]
            
            status = "Normal"
            if load > 400: status = "HIGH SURGE"
            elif load > 200: status = "Elevated"
            
            mo.hstack([
                mo.stat("Total Incidents", f"{total:,}"),
                mo.stat("Latest Update", str(latest)),
                mo.stat("6-Hour Load", f"{load}", caption=status)
            ])
        except Exception as e:
            mo.md(f" Data Error: {e}")
            latest, load, status, total = None, None, None, None
            
    return latest, load, status, total

@app.cell
def _(con, go, mo):
    # --- FORECAST CHART SECTION ---
    if con:
        try:
            fc = con.execute("SELECT * FROM forecast_results").df()
            hist = con.execute("SELECT date_trunc('hour', incident_datetime) as ds, count(*) as y FROM raw_ems WHERE incident_datetime > (SELECT MAX(incident_datetime) - INTERVAL 3 DAY FROM raw_ems) GROUP BY ds ORDER BY ds").df()
            
            fig_forecast = go.Figure()
            fig_forecast.add_trace(go.Scatter(x=hist['ds'], y=hist['y'], mode='lines', name='History', line=dict(color='gray')))
            fig_forecast.add_trace(go.Scatter(x=fc['ds'], y=fc['yhat'], mode='lines', name='AI Forecast', line=dict(color='blue')))
            fig_forecast.add_trace(go.Scatter(x=list(fc['ds'])+list(fc['ds'])[::-1], y=list(fc['yhat_upper'])+list(fc['yhat_lower'])[::-1], fill='toself', fillcolor='rgba(0,0,255,0.1)', line=dict(color='rgba(0,0,0,0)'), name='Confidence'))
            
            fig_forecast.update_layout(title="7-Day Demand Forecast", xaxis_title="Time", yaxis_title="Ambulance Demand")
            mo.ui.plotly(fig_forecast)
        except:
            mo.md(" Forecast not ready yet.")
            fig_forecast = None
            fc, hist = None, None
    else:
        fig_forecast, fc, hist = None, None, None
        
    return fc, fig_forecast, hist

@app.cell
def _(con, mo, px):
    # --- MAP SECTION ---
    if con:
        try:
            map_df = con.execute("SELECT borough, count(*) as calls FROM raw_ems GROUP BY borough ORDER BY calls DESC").df()
            fig_map = px.bar(map_df, x="borough", y="calls", color="calls", title="Risk by Borough", color_continuous_scale="Reds")
            mo.ui.plotly(fig_map)
        except:
            map_df, fig_map = None, None
    else:
        map_df, fig_map = None, None
        
    return fig_map, map_df
