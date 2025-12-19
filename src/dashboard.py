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
    
    # Connect Read-Only
    con = duckdb.connect("nyc_ems.db", read_only=True)
    return con, mo, pd, go, px

@app.cell
def _(mo):
    mo.md("# NYC Heat-Shield: Command Center")
    return

@app.cell
def _(con, mo):
    # KPI Stats
    try:
        total = con.execute("SELECT COUNT(*) FROM raw_ems").fetchone()[0]
        latest = con.execute("SELECT MAX(incident_datetime) FROM raw_ems").fetchone()[0]
        
        # Load in last 6 hours
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
        mo.md(f"System Offline. Run src/live_engine.py to start. Error: {e}")
    return latest, load, status, total

@app.cell
def _(con, go, mo):
    # Forecast Chart
    try:
        fc = con.execute("SELECT * FROM forecast_results").df()
        
        hist = con.execute("SELECT date_trunc('hour', incident_datetime) as ds, count(*) as y FROM raw_ems WHERE incident_datetime > (SELECT MAX(incident_datetime) - INTERVAL 3 DAY FROM raw_ems) GROUP BY ds ORDER BY ds").df()
        
        fig = go.Figure()
        # History Line
        fig.add_trace(go.Scatter(x=hist['ds'], y=hist['y'], mode='lines', name='History', line=dict(color='gray')))
        # Forecast Line
        fig.add_trace(go.Scatter(x=fc['ds'], y=fc['yhat'], mode='lines', name='AI Forecast', line=dict(color='blue')))
        # Confidence Interval
        fig.add_trace(go.Scatter(
            x=list(fc['ds'])+list(fc['ds'])[::-1], 
            y=list(fc['yhat_upper'])+list(fc['yhat_lower'])[::-1], 
            fill='toself', fillcolor='rgba(0,0,255,0.1)', 
            line=dict(color='rgba(0,0,0,0)'), name='Confidence'
        ))
        
        fig.update_layout(title="7-Day Demand Forecast", xaxis_title="Time", yaxis_title="Ambulance Demand")
        mo.ui.plotly(fig)
    except:
        mo.md("Forecast Missing. Run src/forecaster.py.")
    return fc, fig, hist

@app.cell
def _(con, mo, px):
    # Map
    try:
        df = con.execute("SELECT borough, count(*) as calls FROM raw_ems GROUP BY borough ORDER BY calls DESC").df()
        fig = px.bar(df, x="borough", y="calls", color="calls", title="Risk by Borough", color_continuous_scale="Reds")
        mo.ui.plotly(fig)
    except:
        pass
    return df, fig
