import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import psycopg2
from datetime import datetime
import os
import json
from dotenv import load_dotenv

load_dotenv()

DB_URL         = os.getenv("SUPABASE_DB_URL")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
CREDS_PATH     = os.getenv("GOOGLE_SHEETS_CREDS_PATH", "credentials.json")

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

def get_sheets_client():
    # Kalau ada GOOGLE_SHEETS_CREDS (di GitHub Actions), pakai itu
    if CREDS_JSON:
        creds_dict = json.loads(CREDS_JSON)
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    else:
        # Lokal — pakai file credentials.json
        creds = Credentials.from_service_account_file(CREDS_PATH, scopes=SCOPES)
    return gspread.authorize(creds)

def get_db_connection():
    return psycopg2.connect(DB_URL)

def export_table(client, sheet_name, query):
    print(f"  Exporting {sheet_name}...")
    conn = get_db_connection()
    df = pd.read_sql(query, conn)
    conn.close()

    if df.empty:
        print(f"  ⚠️  {sheet_name}: tidak ada data")
        return

    worksheet = client.open_by_key(SPREADSHEET_ID).worksheet(sheet_name)
    worksheet.clear()

    # Convert datetime columns to string
    for col in df.select_dtypes(include=["datetime64", "object"]).columns:
        df[col] = df[col].astype(str)

    # Upload header + data
    data = [df.columns.tolist()] + df.values.tolist()
    worksheet.update(data)

    print(f"  ✅  {sheet_name}: {len(df)} baris berhasil diexport")

def main():
    print("=" * 50)
    print("EXPORT TO GOOGLE SHEETS")
    print(f"Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    client = get_sheets_client()

    export_table(client, "mart_daily_summary",
        "SELECT * FROM mart.mart_daily_summary ORDER BY summary_date DESC LIMIT 90")

    export_table(client, "mart_sector_performance",
        "SELECT * FROM mart.mart_sector_performance ORDER BY trade_date DESC LIMIT 500")

    export_table(client, "mart_stock_metrics",
        "SELECT * FROM mart.mart_stock_metrics ORDER BY trade_date DESC LIMIT 500")

    export_table(client, "mart_anomaly_signals",
        "SELECT * FROM mart.mart_anomaly_signals ORDER BY detected_at DESC LIMIT 200")

    print("\n✅ Export selesai! Dashboard Looker Studio akan terupdate.")

if __name__ == "__main__":
    main()