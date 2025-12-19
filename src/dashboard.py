import marimo

__generated_with = "0.1.0"
app = marimo.App(width="medium")

@app.cell
def __():
    import marimo as mo
    import pandas as pd
    import data_loader 
    return data_loader, mo, pd

@app.cell
def __(mo):
    mo.md("# Student Performance Dashboard")
    return

@app.cell
def __(mo):
    # This creates the Password Box in the UI
    password_box = mo.ui.text(kind="password", label="Oracle Password (asd251095)")
    
    # Display the box
    password_box
    return password_box,

@app.cell
def __(data_loader, password_box):
    sql_query = "SELECT * FROM STUDENTS"
    
    # Pass the value from the UI box to the loader
    df = data_loader.get_data(sql_query, manual_password=password_box.value)
    return df, sql_query

@app.cell
def __(df, mo):
    if not df.empty:
        table = mo.ui.table(df, selection=None)
    else:
        table = mo.md("No data loaded. Please enter password or check CSV.")
    
    table
    return table,

if __name__ == "__main__":
    app.run()
