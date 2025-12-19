import marimo

__generated_with = "0.1.0"
app = marimo.App()

@app.cell
async def _():
    # 1. IMPORTS
    import marimo as mo
    import duckdb
    import pandas as pd
    import plotly.graph_objects as go
    import plotly.express as px
    import sys
    import os
    
    # 2. TITLE
    mo.output.replace(mo.md("# NYC Heat-Shield: Command Center"))
    
    # 3. DOWNLOAD DATA (Cloud Fix)
    status_text = "Initializing..."
    if "pyodide" in sys.modules:
        if not os.path.exists("nyc_ems.db"):
            print("Downloading data...")
            try:
                from pyodide.http import pyfetch
                response = await pyfetch("nyc_ems.db")
                with open("nyc_ems.db", "wb") as f:
                    f.write(await response.bytes())
            except Exception as e:
                print(f"Error: {e}")

    # 4. CONNECT TO DB
    con = None
    if os.path.exists("nyc_ems.db"):
        try:
            con = duckdb.connect("nyc_ems.db", read_only=True)
        except:
            pass

    # 5. PREPARE DASHBOARD CONTENT
    content = []
    
    # Add Title
    content.append(mo.md("# NYC Heat-Shield: Command Center"))

    if con is None:
        content.append(mo.md("###  System Offline: Database not found."))
    else:
        # --- KPI SECTION ---
        try:
            total = con.execute("SELECT COUNT(*) FROM raw_ems").fetchone()[0]
            latest = con.execute("SELECT MAX(incident_datetime) FROM raw_ems").fetchone()[0]
            load = con.execute("SELECT count(*) FROM raw_ems WHERE incident_datetime > (SELECT MAX(incident_datetime) - INTERVAL 6 HOUR FROM raw_ems)").fetchone()[0]
            
            status_label = "Normal"
            if load > 400: status_label = "HIGH SURGE"
            elif load > 200: status_label = "Elevated"
            
            content.append(
                mo.hstack([
                    mo.stat("Total Incidents", f"{total:,}"),
                    mo.stat("Latest Update", str(latest)),
                    mo.stat("6-Hour Load", f"{load}", caption=status_label)
                ])
            )
        except:
            content.append(mo.md("Error loading KPIs"))

        # --- CHART SECTION ---
        try:
            fc = con.execute("SELECT * FROM forecast_results").df()
            hist = con.execute("SELECT date_trunc('hour', incident_datetime) as ds, count(*) as y FROM raw_ems WHERE incident_datetime > (SELECT MAX(incident_datetime) - INTERVAL 3 DAY FROM raw_ems) GROUP BY ds ORDER BY ds").df()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=hist['ds'], y=hist['y'], mode='lines', name='History', line=dict(color='gray')))
            fig.add_trace(go.Scatter(x=fc['ds'], y=fc['yhat'], mode='lines', name='AI Forecast', line=dict(color='blue')))
            fig.add_trace(go.Scatter(x=list(fc['ds'])+list(fc['ds'])[::-1], y=list(fc['yhat_upper'])+list(fc['yhat_lower'])[::-1], fill='toself', fillcolor='rgba(0,0,255,0.1)', line=dict(color='rgba(0,0,0,0)'), name='Confidence'))
            
            fig.update_layout(title="7-Day Demand Forecast", xaxis_title="Time", yaxis_title="Ambulance Demand")
            content.append(mo.ui.plotly(fig))
        except:
            pass

        # --- MAP SECTION ---
        try:
            map_df = con.execute("SELECT borough, count(*) as calls FROM raw_ems GROUP BY borough ORDER BY calls DESC").df()
            map_fig = px.bar(map_df, x="borough", y="calls", color="calls", title="Risk by Borough", color_continuous_scale="Reds")
            content.append(mo.ui.plotly(map_fig))
        except:
            pass

    # 6. DISPLAY EVERYTHING
    mo.vstack(content)
    
    return con, content, duckdb, go, mo, os, pd, px, status_text, sys
