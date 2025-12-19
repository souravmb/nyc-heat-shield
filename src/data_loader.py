import pandas as pd
import oracledb
import getpass
import os
import sys

DB_HOST = "172.17.9.63"
DB_PORT = 1521
DB_SERVICE = "ORCL" 
DB_USER = "P2ASD25023"

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
CSV_FILENAME = os.path.join(PROJECT_ROOT, "backup_data.csv")

def get_data(query):
    print(f"Target: {DB_HOST} (User: {DB_USER})")
    
    print("Type your password (asd251095) below. It will be hidden.")
    password = getpass.getpass(f"Enter Password: ")

    if not password:
        print("No password entered. Skipping to offline mode...")
    
    else:
        try:
            print("Connecting to Oracle...")
            
            dsn = oracledb.makedsn(DB_HOST, DB_PORT, service_name=DB_SERVICE)
            
            conn = oracledb.connect(
                user=DB_USER,
                password=password,
                dsn=dsn
            )
            print("Connection Successful!")

            print(f"Executing query: {query[:50]}...")
            df = pd.read_sql(query, conn)
            conn.close()

            df.to_csv(CSV_FILENAME, index=False)
            print(f"Data saved to: {CSV_FILENAME}")
            return df

        except oracledb.Error as e:
            error_obj = e.args[0]
            print(f"\nCONNECTION FAILED: {error_obj.message}")
            if "ORA-12514" in str(error_obj):
                print("TIP: The Service Name 'ORCL' might be wrong. Try changing DB_SERVICE to 'XE'.")
            elif "ORA-12170" in str(error_obj):
                print("TIP: Network Timeout. Are you on the Amrita Wi-Fi?")
            print("Switching to offline mode...")

    if os.path.exists(CSV_FILENAME):
        print(f"Loading data from local backup: {CSV_FILENAME}")
        return pd.read_csv(CSV_FILENAME)
    else:
        print("\nERROR: Database offline and no backup CSV found.")
        print("   You must run this successfully at least once on campus.")
        return pd.DataFrame()

if __name__ == "__main__":
    TEST_QUERY = "SELECT table_name FROM user_tables"
    
    df = get_data(TEST_QUERY)
    
    if not df.empty:
        print("\nSuccess! Tables Found:")
        print(df)
