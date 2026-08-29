"""
config.py
Konfigurasi bersama untuk seluruh script pipeline.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

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

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

STOCK_PRICES_CSV = DATA_DIR / "stock_prices.csv"
STOCK_INFO_CSV   = DATA_DIR / "stock_info.csv"

# Dibaca dari .env — tidak pernah hardcode di sini
SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")

REQUEST_DELAY_SECONDS = 1.0