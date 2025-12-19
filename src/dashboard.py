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
def title_section(mo):
    mo.md("# 🚑 NYC Heat-Shield: Command Center")
    return

@app.cell
async def data_loader(asyncio, duckdb, mo, os, sys):
    # --- THE ENGINE ROOM ---
    # This function handles the download and connection safely.
    
    status_widget = mo.md(" **Initializing System...**")
    
    # 1. Detect if we are running on the Website (Pyodide)
    if "pyodide" in sys.modules:
        if not os.path.exists("nyc_ems.db"):
            status_widget = mo.md(" **Downloading Data from Cloud... (Please Wait)**")
            try:
                from pyodide.http import pyfetch
                response = await pyfetch("nyc_ems.db")
                with open("nyc_ems.db", "wb") as f:
                    f.write(await response.bytes())
            except Exception as e:
                status_widget = mo.md(f" **Download Failed:** {e}")

    # 2. Connect to Database
    con = None
    if os.path.exists("nyc_ems.db"):
        try:
            con = duckdb.connect("nyc_ems.db", read_only=True)
            status_widget = mo.md(" **System Online**")
        except Exception as e:
            status_widget = mo.md(f" **Database Error:** {e}")
    else:
        status_widget = mo.md(" **No Database Found.** (Run live_engine.py locally first)")
        
    return con, status_widget

@app.cell
def kpi_section(con, mo):
    # If database isn't ready, stop here
    if con is None:
        return None, None, None, None
        
    try:
        # Calculate Stats
        total = con.execute("SELECT COUNT(*) FROM raw_ems").fetchone()[0]
        latest = con.execute("SELECT MAX(incident_datetime) FROM raw_ems").fetchone()[0]
        load = con.execute("SELECT count(*) FROM raw_ems WHERE incident_datetime > (SELECT MAX(incident_datetime) - INTERVAL 6 HOUR FROM raw_ems)").fetchone()[0]
        
        # Determine Status
        status_text = "Normal"
        if load > 400: status_text = "HIGH SURGE"
        elif load > 200: status_text = "Elevated"
        
        # Display Widgets
        mo.hstack([
            mo.stat("Total Incidents", f"{total:,}"),
            mo.stat("Latest Update", str(latest)),
            mo.stat("6-Hour Load", f"{load}", caption=status_text)
        ])
    except:
        total, latest, load, status_text = None, None, None, None
        
    return latest, load, status_text, total

@app.cell
def chart_section(con, go, mo):
    # If database isn't ready, stop here
    if con is None:
        return None, None, None
        
    try:
        # Fetch Data
        fc = con.execute("SELECT * FROM forecast_results").df()
        hist = con.execute("SELECT date_trunc('hour', incident_datetime) as ds, count(*) as y FROM raw_ems WHERE incident_datetime > (SELECT MAX(incident_datetime) - INTERVAL 3 DAY FROM raw_ems) GROUP BY ds ORDER BY ds").df()
        
        # Build Chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hist['ds'], y=hist['y'], mode='lines', name='History', line=dict(color='gray')))
        fig.add_trace(go.Scatter(x=fc['ds'], y=fc['yhat'], mode='lines', name='AI Forecast', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=list(fc['ds'])+list(fc['ds'])[::-1], y=list(fc['yhat_upper'])+list(fc['yhat_lower'])[::-1], fill='toself', fillcolor='rgba(0,0,255,0.1)', line=dict(color='rgba(0,0,0,0)'), name='Confidence'))
        
        fig.update_layout(title="7-Day Demand Forecast", xaxis_title="Time", yaxis_title="Ambulance Demand")
        mo.ui.plotly(fig)
    except:
        fc, hist, fig = None, None, None
        
    return fc, fig, hist

@app.cell
def map_section(con, mo, px):
    # If database isn't ready, stop here
    if con is None:
        return None, None
        
    try:
        # Build Map
        map_df = con.execute("SELECT borough, count(*) as calls FROM raw_ems GROUP BY borough ORDER BY calls DESC").df()
        map_fig = px.bar(map_df, x="borough", y="calls", color="calls", title="Risk by Borough", color_continuous_scale="Reds")
        mo.ui.plotly(map_fig)
    except:
        map_df, map_fig = None, None
        
    return map_df, map_fig

if __name__ == "__main__":
    app.run()
