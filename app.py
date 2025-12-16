import marimo

__generated_with = "0.16.5"
app = marimo.App(auto_download=["ipynb"])


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import requests_cache
    import openmeteo_requests
    from retry_requests import retry
    from urllib.parse import quote


    EMS_API_URL = "https://data.cityofnewyork.us/resource/76xm-jjuj.csv"
    LAT, LON = 40.7128, -74.0060
    START, END = "2023-06-01", "2023-08-31"


    q = quote(f"$where=incident_datetime between '{START}T00:00:00' and '{END}T23:59:59'&$select=incident_datetime,initial_call_type&$limit=50000", safe='=&$,')
    ems_df = pd.read_csv(f"{EMS_API_URL}?{q}")
    ems_df['incident_datetime'] = pd.to_datetime(ems_df['incident_datetime'])
    ems_df['incident_hour'] = ems_df['incident_datetime'].dt.floor('h')


    s = retry(requests_cache.CachedSession('.cache', expire_after=3600), retries=5, backoff_factor=0.2)
    c = openmeteo_requests.Client(session=s)
    p = {"latitude": LAT, "longitude": LON, "start_date": START, "end_date": END, "hourly": ["temperature_2m"]}
    r = c.weather_api("https://archive-api.open-meteo.com/v1/archive", params=p)[0].Hourly()

    w_df = pd.DataFrame({
        "date": pd.date_range(start=pd.to_datetime(r.Time(), unit="s", utc=True), end=pd.to_datetime(r.TimeEnd(), unit="s", utc=True), freq=pd.Timedelta(seconds=r.Interval()), inclusive="left"),
        "temperature_2m": r.Variables(0).ValuesAsNumpy()
    })
    w_df['local_time'] = w_df['date'].dt.tz_convert('America/New_York').dt.tz_localize(None)

    merged_df = pd.merge(ems_df.groupby('incident_hour').size().reset_index(name='call_volume'), w_df, left_on='incident_hour', right_on='local_time', how='inner')


    dashboard = mo.vstack([
        mo.md("##**Project: Stress-Testing Urban Resilience**"),
        mo.md(f" **Phase 1 Complete:** {len(merged_df)} hourly records linked."),
        mo.ui.tabs({
            "Master Data": mo.ui.table(merged_df, selection=None),
            "Raw EMS": mo.ui.table(ems_df.head(50), selection=None),
            "Raw Weather": mo.ui.table(w_df.head(50), selection=None)
        })
    ])

    dashboard
    return merged_df, mo, pd


@app.cell
def _(merged_df, mo):
    from statsmodels.tsa.stattools import grangercausalitytests
    import plotly.graph_objects as go
    import contextlib
    import io

    print("Starting Phase 2...")

    P2_LAG_LIMIT = 24
    P2_THRESHOLD = 0.05

    if merged_df is None or len(merged_df) < 50:
         view_p2_clean = mo.md("**Waiting for Phase 1 Data...**")
    else:
        with contextlib.redirect_stdout(io.StringIO()):
            p2_test_output = grangercausalitytests(
                merged_df[['call_volume', 'temperature_2m']], 
                maxlag=P2_LAG_LIMIT
            )

        p2_lags = []
        p2_p_values = []
    
        for i in range(1, P2_LAG_LIMIT + 1):
            val = p2_test_output[i][0]['ssr_chi2test'][1]
            p2_lags.append(i)
            p2_p_values.append(val)

        p2_colors = ['#2ecc71' if p < P2_THRESHOLD else '#95a5a6' for p in p2_p_values]
    
        fig_p2 = go.Figure(data=[go.Bar(
            x=p2_lags,
            y=p2_p_values,
            marker_color=p2_colors,
            text=[f"{p:.4f}" for p in p2_p_values],
            textposition='auto',
            hoverinfo='x+y'
        )])

        fig_p2.add_shape(type="line",
            x0=0, y0=P2_THRESHOLD, x1=P2_LAG_LIMIT+1, y1=P2_THRESHOLD,
            line=dict(color="red", width=2, dash="dash"),
        )

        fig_p2.update_layout(
            title="<b>Granger Causality Test:</b> Does Heat Drive EMS Demand?",
            xaxis_title="Lag (Hours after Heat Spike)",
            yaxis_title="P-Value",
            template="plotly_white",
            annotations=[dict(
                x=P2_LAG_LIMIT/2, y=P2_THRESHOLD,
                xref="x", yref="y",
                text="Significance Threshold",
                showarrow=True, arrowhead=1, ax=0, ay=-40
            )]
        )

        p2_min_p = min(p2_p_values)
        p2_best_lag = p2_lags[p2_p_values.index(p2_min_p)]
    
        view_p2_clean = mo.vstack([
            mo.ui.plotly(fig_p2)
        ])

    view_p2_clean
    return


@app.cell
def _(merged_df, mo, pd):
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import mean_absolute_error, r2_score
    import plotly.graph_objects as go_ml

    print("Running Advanced AI Analysis...")

    if merged_df is None or len(merged_df) < 50:
        view_final = mo.md("**Data Error:** Please run Phase 1 again.")
    else:
        df_ml = merged_df.copy().sort_values('incident_hour')
    
        df_ml['hour'] = df_ml['incident_hour'].dt.hour
        df_ml['lag_1'] = df_ml['call_volume'].shift(1)
        df_ml['lag_24'] = df_ml['call_volume'].shift(24)
        df_ml['day_of_week'] = df_ml['incident_hour'].dt.dayofweek # 0=Mon, 6=Sun
    
        df_ml = df_ml.dropna()
    
        split = int(len(df_ml) * 0.8)
        train, test = df_ml.iloc[:split], df_ml.iloc[split:]
    
        features = ['temperature_2m', 'hour', 'lag_1', 'lag_24', 'day_of_week']
        X_train, y_train = train[features], train['call_volume']
        X_test, y_test = test[features], test['call_volume']

        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
    
        preds = model.predict(X_test)
        r2 = r2_score(y_test, preds)

        fig_acc = go_ml.Figure()
        fig_acc.add_trace(go_ml.Scatter(x=test['incident_hour'], y=y_test, mode='lines', name='Actual', line=dict(color='rgba(0,0,0,0.3)')))
        fig_acc.add_trace(go_ml.Scatter(x=test['incident_hour'], y=preds, mode='lines', name='AI Forecast', line=dict(color='#3498db', width=2)))
        fig_acc.update_layout(title=f"<b>Model Accuracy (R²: {r2:.2f})</b>", template="plotly_white", height=400)

        df_imp = pd.DataFrame({
            'Feature': features, 
            'Importance': model.feature_importances_
        }).sort_values('Importance', ascending=True)

        fig_imp = go_ml.Figure(go_ml.Bar(
            x=df_imp['Importance'], y=df_imp['Feature'], orientation='h', marker_color='#e74c3c'
        ))
        fig_imp.update_layout(title="<b>What drives the prediction?</b> (Feature Importance)", template="plotly_white", height=300)

        view_final = mo.vstack([
            mo.md("###**Advanced AI Results**"),
            mo.md(f"The model has learned from **{len(train)} hours** of city data."),
            mo.ui.plotly(fig_acc),
            mo.md("---"),
            mo.ui.plotly(fig_imp),
        ])

    view_final
    return


@app.cell
def _(merged_df, mo):
    total_calls = merged_df['call_volume'].sum()
    peak_temp = merged_df['temperature_2m'].max()

    stress_threshold = merged_df['call_volume'].quantile(0.90)
    stress_hours = len(merged_df[merged_df['call_volume'] > stress_threshold])

    csv_buffer = merged_df.to_csv(index=False)
    download_btn = mo.download(
        data=csv_buffer,
        filename="NYC_EMS_Heat_Analysis.csv",
        label="Download Processed Data (CSV)"
    )

    final_output = mo.vstack([
        mo.md("###Execution Complete"),
        mo.stat(
            label="Total Analyzed Hours",
            value=f"{len(merged_df)}",
            caption=f"Covering {total_calls:,} emergency calls"
        ),
        mo.stat(
            label="Peak Temperature",
            value=f"{peak_temp:.1f}°C",
            caption=f"{stress_hours} High-Stress Hours Detected"
        ),
        download_btn
    ])

    final_output
    return


if __name__ == "__main__":
    app.run()
