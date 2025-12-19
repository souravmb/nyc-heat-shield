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
    mo.md("# NYC Heat-Shield: Command Center")
    return

@app.cell
async def load_data(asyncio, duckdb, mo, os, sys):
    status = mo.md("Initializing System...")
    
    if "pyodide" in sys.modules:
        if not os.path.exists("nyc_ems.db"):
            status = mo.md("Downloading Data from Cloud...")
            try:
                from pyodide.http import pyfetch
                response = await pyfetch("nyc_ems.db")
                with open("nyc_ems.db", "wb") as f:
                    f.write(await response.bytes())
            except Exception as e:
                status = mo.md(f"Download Error: {e}")

    con = None
    if os.path.exists("nyc_ems.db"):
        try:
            con = duckdb.connect("nyc_ems.db", read_only=True)
            status = mo.md("System Online")
        except:
            status = mo.md("Database Corrupted")
    else:
        status = mo.md("No Database Found")

    return con, status

@app.cell
def kpi_display(con, mo):
    if con is None:
        return None, None, None, None

    try:
        total = con.execute("SELECT COUNT(*) FROM raw_ems").fetchone()[0]
        latest = con.execute("SELECT MAX(incident_datetime) FROM raw_ems").fetchone()[0]
        load = con.execute("SELECT count(*) FROM raw_ems WHERE incident_datetime > (SELECT MAX(incident_datetime) - INTERVAL 6 HOUR FROM raw_ems)").fetchone()[0]
        
        status_txt = "Normal"
        if load > 400: 
            status_txt = "HIGH SURGE"
        elif load > 200: 
            status_txt = "Elevated"

        mo.hstack([
            mo.stat("Total Incidents", f"{total:,}"),
            mo.stat("Latest Update", str(latest)),
            mo.stat("6-Hour Load", f"{load}", caption=status_txt)
        ])
    except:
        total, latest, load, status_txt = None, None, None, None

    return latest, load, status_txt, total

@app.cell
def chart_display(con, go, mo):
    if con is None:
        return None, None, None

    try:
        fc = con.execute("SELECT * FROM forecast_results").df()
        hist = con.execute("SELECT date_trunc('hour', incident_datetime) as ds, count(*) as y FROM raw_ems WHERE incident_datetime > (SELECT MAX(incident_datetime) - INTERVAL 3 DAY FROM raw_ems) GROUP BY ds ORDER BY ds").df()
        
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
def map_display(con, mo, px):
    if con is None:
        return None, None

    try:
        map_df = con.execute("SELECT borough, count(*) as calls FROM raw_ems GROUP BY borough ORDER BY calls DESC").df()
        map_fig = px.bar(map_df, x="borough", y="calls", color="calls", title="Risk by Borough", color_continuous_scale="Reds")
        mo.ui.plotly(map_fig)
    except:
        map_df, map_fig = None, None

    return map_df, map_fig

if __name__ == "__main__":
    app.run()
