import marimo

__generated_with = "0.1.0"
app = marimo.App(width="medium")

@app.cell
def __():
    import marimo as mo
    import pandas as pd
    import oracledb
    import os
    return mo, pd, oracledb, os

@app.cell
def __(os):
    DB_HOST = "172.17.9.63"
    DB_PORT = 1521
    DB_SERVICE = "ORCL"      
    DB_USER = "P2ASD25023"   
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    CSV_FILENAME = os.path.join(project_root, "backup_data.csv")
    
    SQL_QUERY = "SELECT * FROM STUDENTS" 
    return CSV_FILENAME, DB_HOST, DB_PORT, DB_SERVICE, DB_USER, SQL_QUERY, current_dir, project_root

@app.cell
def __(CSV_FILENAME, DB_HOST, DB_PORT, DB_SERVICE, DB_USER, oracledb, os, pd):
    def get_data_hybrid(query, password_input):
        
        if password_input:
            try:
                dsn = oracledb.makedsn(DB_HOST, DB_PORT, service_name=DB_SERVICE)
                conn = oracledb.connect(
                    user=DB_USER,
                    password=password_input,
                    dsn=dsn
                )
                
                df = pd.read_sql(query, conn)
                conn.close()
                
                df.to_csv(CSV_FILENAME, index=False)
                return df, f"Connected to Oracle. Backup saved to {CSV_FILENAME}"

            except Exception as e:
                error_msg = str(e)
                if "ORA-12514" in error_msg:
                    return None, "Service Error: Try changing ORCL to XE in the code."
                elif "ORA-12170" in error_msg:
                    return None, "Timeout: Are you connected to Amrita Wi-Fi?"
                else:
                    return None, f"Connection Failed: {error_msg}"

        if os.path.exists(CSV_FILENAME):
            df = pd.read_csv(CSV_FILENAME)
            return df, f"Offline Mode: Loaded data from {CSV_FILENAME}"
        
        return pd.DataFrame(), "Waiting for password... No local backup found"
    return get_data_hybrid,

@app.cell
def __(mo):
    mo.md("# Student Performance Dashboard")
    return

@app.cell
def __(mo):
    password_box = mo.ui.text(kind="password", label="Oracle Password (asd251095)")
    
    mo.vstack([
        mo.md("**Admin Access (Enter to refresh data):**"),
        password_box
    ])
    return password_box,

@app.cell
def __(SQL_QUERY, get_data_hybrid, password_box):
    df, status_message = get_data_hybrid(SQL_QUERY, password_box.value)
    return df, status_message

@app.cell
def __(df, mo, status_message):
    content = [
        mo.md(f"**Status:** {status_message}"),
        mo.ui.table(df, selection=None) if not df.empty else mo.md("_No data to display_")
    ]
    mo.vstack(content)
    return content,

if __name__ == "__main__":
    app.run()
