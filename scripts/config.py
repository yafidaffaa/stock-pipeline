"""
config.py
Konfigurasi bersama untuk seluruh script pipeline.
Dipakai oleh fetch_stock_data.py, load_to_supabase.py, dan export_to_sheets.py.
"""

import os
from pathlib import Path

# --- Daftar 20 saham BEI yang ditrack + sektor (sesuai PRD Section 4.1) ---
# Sektor di sini adalah klasifikasi kita sendiri, BUKAN diambil dari Yahoo Finance,
# supaya konsisten dengan skema mart_sector_performance di dbt.
TICKERS = {
    "BBCA.JK": "Perbankan",
    "BBRI.JK": "Perbankan",
    "BMRI.JK": "Perbankan",
    "BBNI.JK": "Perbankan",
    "TLKM.JK": "Telekomunikasi",
    "EXCL.JK": "Telekomunikasi",
    "ISAT.JK": "Telekomunikasi",
    "ADRO.JK": "Energi",
    "PTBA.JK": "Energi",
    "PGAS.JK": "Energi",
    "ICBP.JK": "Consumer",
    "INDF.JK": "Consumer",
    "UNVR.JK": "Consumer",
    "GOTO.JK": "Teknologi",
    "BUKA.JK": "Teknologi",
    "BSDE.JK": "Properti",
    "SMRA.JK": "Properti",
    "JSMR.JK": "Infrastruktur",
    "WIKA.JK": "Infrastruktur",
    "^JKSE": "Index",
}

# --- Folder tempat menyimpan CSV mentah hasil fetch, sebelum di-load ke Supabase ---
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

STOCK_PRICES_CSV = DATA_DIR / "stock_prices.csv"
STOCK_INFO_CSV = DATA_DIR / "stock_info.csv"

# --- Koneksi database (dibaca dari .env / GitHub Actions secret) ---
SUPABASE_DB_URL = os.getenv("postgresql://postgres:StockPipeline2026!@db.fjoizcrivwjyzkjtrreq.supabase.co:5432/postgres")

# --- Delay antar request ke Yahoo Finance, biar tidak kena rate limit ---
REQUEST_DELAY_SECONDS = 1.0