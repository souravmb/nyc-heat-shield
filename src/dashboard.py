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
    # --- CONFIGURATION ---
    DB_HOST = "172.17.9.63"
    DB_PORT = 1521
    DB_SERVICE = "ORCL"      # Change to "XE" if needed
    DB_USER = "P2ASD25023"   # Your username
    CSV_FILENAME = "backup_data.csv"
    
    # Replace 'STUDENTS' with your actual table name if different
    SQL_QUERY = "SELECT * FROM STUDENTS" 
    return DB_HOST, DB_PORT, DB_SERVICE, DB_USER, CSV_FILENAME, SQL_QUERY

@app.cell
def __(DB_HOST, DB_PORT, DB_SERVICE, DB_USER, CSV_FILENAME, oracledb, os, pd):
    def get_data_hybrid(query, password_input):
        """
        Fetches data. 
        1. If password is provided, tries Oracle DB -> Saves to CSV.
        2. If password is empty or DB fails, tries loading CSV.
        """
        
        # 1. Try Oracle Connection (if password exists)
        if password_input:
            try:
                # Setup Connection
                dsn = oracledb.makedsn(DB_HOST, DB_PORT, service_name=DB_SERVICE)
                conn = oracledb.connect(
                    user=DB_USER,
                    password=password_input,
                    dsn=dsn
                )
                
                # Fetch Data
                df = pd.read_sql(query, conn)
                conn.close()
                
                # Save Backup (This ensures future users see data without password)
                df.to_csv(CSV_FILENAME, index=False)
                return df, f"Connected to Oracle. Backup saved to {CSV_FILENAME}"

            except Exception as e:
                error_msg = str(e)
                if "ORA-12514" in error_msg:
                    return None, f"Service Error: Try changing 'ORCL' to 'XE' in the code."
                elif "ORA-12170" in error_msg:
                    return None, f"Timeout: Are you connected to Amrita Wi-Fi?"
                else:
                    return None, f"Connection Failed: {error_msg}"

        # 2. Fallback: Offline Mode (CSV)
        # This runs automatically for users who don't have the password
        if os.path.exists(CSV_FILENAME):
            df = pd.read_csv(CSV_FILENAME)
            return df, f"Offline Mode: Loaded data from {CSV_FILENAME}"
        
        return pd.DataFrame(), "Waiting for password... (No local backup found)"
    return get_data_hybrid,

@app.cell
def __(mo):
    mo.md("# Student Performance Dashboard")
    return

@app.cell
def __(mo):
    # This widget collects the password safely
    password_box = mo.ui.text(kind="password", label="Oracle Password (asd251095)")
    
    # Display the box
    mo.vstack([
        mo.md("**Admin Access (Enter to refresh data):**"),
        password_box
    ])
    return password_box,

@app.cell
def __(SQL_QUERY, get_data_hybrid, password_box):
    # Fetch data reactively when password changes
    df, status_message = get_data_hybrid(SQL_QUERY, password_box.value)
    return df, status_message

@app.cell
def __(df, mo, status_message):
    # Display Status and Table
    content = [
        mo.md(f"**Status:** {status_message}"),
        mo.ui.table(df, selection=None) if not df.empty else mo.md("_No data to display_")
    ]
    mo.vstack(content)
    return content,

if __name__ == "__main__":
    app.run()
