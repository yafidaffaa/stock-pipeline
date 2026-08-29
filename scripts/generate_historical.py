import pandas as pd
import numpy as np
from datetime import date, timedelta
import psycopg2
from psycopg2.extras import execute_values
import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("SUPABASE_DB_URL")

# ================================
# KONFIGURASI SAHAM BEI
# Harga mendekati real Agustus 2026
# ================================
STOCKS = {
    "BBCA.JK": {"name": "Bank Central Asia",        "sector": "Perbankan",       "base_price": 9200,  "volatility": 0.015},
    "BBRI.JK": {"name": "Bank Rakyat Indonesia",    "sector": "Perbankan",       "base_price": 4350,  "volatility": 0.018},
    "BMRI.JK": {"name": "Bank Mandiri",             "sector": "Perbankan",       "base_price": 6100,  "volatility": 0.016},
    "BBNI.JK": {"name": "Bank Negara Indonesia",    "sector": "Perbankan",       "base_price": 4900,  "volatility": 0.019},
    "TLKM.JK": {"name": "Telkom Indonesia",         "sector": "Telekomunikasi",  "base_price": 3200,  "volatility": 0.014},
    "EXCL.JK": {"name": "XL Axiata",               "sector": "Telekomunikasi",  "base_price": 2400,  "volatility": 0.022},
    "ISAT.JK": {"name": "Indosat Ooredoo",          "sector": "Telekomunikasi",  "base_price": 2100,  "volatility": 0.020},
    "ADRO.JK": {"name": "Adaro Energy",             "sector": "Energi",          "base_price": 3800,  "volatility": 0.025},
    "PTBA.JK": {"name": "Bukit Asam",               "sector": "Energi",          "base_price": 2900,  "volatility": 0.023},
    "PGAS.JK": {"name": "Perusahaan Gas Negara",    "sector": "Energi",          "base_price": 1650,  "volatility": 0.021},
    "ICBP.JK": {"name": "Indofood CBP",             "sector": "Consumer",        "base_price": 9800,  "volatility": 0.013},
    "INDF.JK": {"name": "Indofood",                 "sector": "Consumer",        "base_price": 6400,  "volatility": 0.014},
    "UNVR.JK": {"name": "Unilever Indonesia",       "sector": "Consumer",        "base_price": 2200,  "volatility": 0.012},
    "GOTO.JK": {"name": "GoTo Group",               "sector": "Teknologi",       "base_price": 68,    "volatility": 0.035},
    "BUKA.JK": {"name": "Bukalapak",                "sector": "Teknologi",       "base_price": 142,   "volatility": 0.038},
    "BSDE.JK": {"name": "BSD City",                 "sector": "Properti",        "base_price": 1150,  "volatility": 0.020},
    "SMRA.JK": {"name": "Summarecon",               "sector": "Properti",        "base_price": 890,   "volatility": 0.022},
    "JSMR.JK": {"name": "Jasa Marga",               "sector": "Infrastruktur",   "base_price": 4600,  "volatility": 0.016},
    "WIKA.JK": {"name": "Wijaya Karya",             "sector": "Infrastruktur",   "base_price": 820,   "volatility": 0.028},
    "^JKSE":   {"name": "Jakarta Composite Index",  "sector": "Index",           "base_price": 7450,  "volatility": 0.010},
}

# Market cap awal (dalam miliar IDR)
MARKET_CAP = {
    "BBCA.JK": 1140000, "BBRI.JK": 650000, "BMRI.JK": 580000, "BBNI.JK": 460000,
    "TLKM.JK": 320000,  "EXCL.JK": 25000,  "ISAT.JK": 22000,
    "ADRO.JK": 120000,  "PTBA.JK": 33000,  "PGAS.JK": 40000,
    "ICBP.JK": 115000,  "INDF.JK": 56000,  "UNVR.JK": 84000,
    "GOTO.JK": 70000,   "BUKA.JK": 15000,
    "BSDE.JK": 22000,   "SMRA.JK": 13000,
    "JSMR.JK": 68000,   "WIKA.JK": 8000,
    "^JKSE":   None,
}

PE_RATIO = {
    "BBCA.JK": 24.5, "BBRI.JK": 13.2, "BMRI.JK": 12.8, "BBNI.JK": 11.5,
    "TLKM.JK": 18.3, "EXCL.JK": 22.1, "ISAT.JK": 19.8,
    "ADRO.JK": 8.2,  "PTBA.JK": 7.5,  "PGAS.JK": 9.1,
    "ICBP.JK": 28.4, "INDF.JK": 14.2, "UNVR.JK": 35.6,
    "GOTO.JK": None, "BUKA.JK": None,
    "BSDE.JK": 15.3, "SMRA.JK": 12.8,
    "JSMR.JK": 16.7, "WIKA.JK": None,
    "^JKSE":   None,
}

def generate_ohlcv(prev_close, volatility, base_volume):
    """
    Generate OHLCV satu hari berdasarkan harga penutupan hari sebelumnya
    Menggunakan Geometric Brownian Motion — model standar di financial modeling
    """
    # Daily return mengikuti distribusi normal
    daily_return = np.random.normal(0.0003, volatility)

    # Open sedikit gap dari close kemarin
    gap = np.random.normal(0, volatility * 0.3)
    open_price = round(prev_close * (1 + gap), 0)

    # Close berdasarkan return
    close_price = round(prev_close * (1 + daily_return), 0)

    # High dan Low — range harian
    intraday_range = abs(np.random.normal(0, volatility * 0.8))
    high_price = round(max(open_price, close_price) * (1 + intraday_range), 0)
    low_price  = round(min(open_price, close_price) * (1 - intraday_range), 0)

    # Volume dengan variasi acak
    volume_multiplier = np.random.lognormal(0, 0.5)
    volume = int(base_volume * volume_multiplier)

    return {
        "open":   max(open_price, 1),
        "high":   max(high_price, open_price, close_price),
        "low":    min(low_price, open_price, close_price),
        "close":  max(close_price, 1),
        "volume": volume,
    }

def get_trading_days(start_date, end_date):
    """Ambil semua hari kerja (Senin-Jumat) antara dua tanggal"""
    days = []
    current = start_date
    while current <= end_date:
        if current.weekday() < 5:  # 0=Senin, 4=Jumat
            days.append(current)
        current += timedelta(days=1)
    return days

def generate_historical_data(start_date, end_date):
    """Generate data historis untuk semua saham"""
    trading_days = get_trading_days(start_date, end_date)
    print(f"Generating data untuk {len(trading_days)} hari trading...")
    print(f"Periode: {start_date} sampai {end_date}\n")

    all_records = []

    for ticker, config in STOCKS.items():
        print(f"  Generating {ticker}...")
        current_price = config["base_price"]
        base_volume = 50_000_000 if ticker != "^JKSE" else 0

        # Mundur dari base_price ke awal periode
        # Simulasikan harga awal berdasarkan drift ke belakang
        n_days = len(trading_days)
        start_price = current_price * np.exp(
            -0.0003 * n_days + np.random.normal(0, config["volatility"] * np.sqrt(n_days))
        )
        start_price = max(start_price, 1)

        prev_close = start_price

        for trade_date in trading_days:
            ohlcv = generate_ohlcv(prev_close, config["volatility"], base_volume)
            all_records.append({
                "ticker":     ticker,
                "trade_date": trade_date,
                **ohlcv,
            })
            prev_close = ohlcv["close"]

    return pd.DataFrame(all_records)

def load_to_database(df):
    """Load data ke Supabase"""
    print(f"\nLoading {len(df)} records ke Supabase...")
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()

    records = [
        (row["ticker"], row["trade_date"], row["open"], row["high"],
         row["low"], row["close"], row["volume"])
        for _, row in df.iterrows()
    ]

    execute_values(cursor, """
        INSERT INTO raw.stock_prices
            (ticker, trade_date, open, high, low, close, volume)
        VALUES %s
        ON CONFLICT (ticker, trade_date) DO NOTHING
    """, records, page_size=1000)

    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ {len(df)} records berhasil diload!")

def load_stock_info():
    """Load info perusahaan ke Supabase"""
    print("\nLoading info perusahaan...")
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()

    for ticker, config in STOCKS.items():
        cursor.execute("""
            INSERT INTO raw.stock_info
                (ticker, company_name, sector, market_cap, pe_ratio,
                 dividend_yield, week_52_high, week_52_low)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (ticker) DO UPDATE SET
                company_name = EXCLUDED.company_name,
                sector       = EXCLUDED.sector,
                market_cap   = EXCLUDED.market_cap,
                pe_ratio     = EXCLUDED.pe_ratio,
                updated_at   = NOW()
        """, (
            ticker,
            config["name"],
            config["sector"],
            MARKET_CAP.get(ticker),
            PE_RATIO.get(ticker),
            None,
            config["base_price"] * 1.15,
            config["base_price"] * 0.82,
        ))

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Info perusahaan berhasil diload!")

def main():
    print("=" * 55)
    print("GENERATE HISTORICAL DATA — Indonesia BEI (Synthetic)")
    print("=" * 55)

    # Generate 3 tahun data historis: 2023-01-02 sampai kemarin
    start_date = date(2023, 1, 2)
    end_date   = date(2026, 8, 28)

    df = generate_historical_data(start_date, end_date)
    load_to_database(df)
    load_stock_info()

    print("\n🎉 Historical data generation selesai!")
    print(f"   Total records: {len(df)}")
    print(f"   Periode: {start_date} s/d {end_date}")

if __name__ == "__main__":
    main()