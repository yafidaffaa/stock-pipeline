import pandas as pd
import numpy as np
from datetime import date, timedelta
import psycopg2
from psycopg2.extras import execute_values
import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("SUPABASE_DB_URL")

STOCKS = {
    "BBCA.JK": {"volatility": 0.015}, "BBRI.JK": {"volatility": 0.018},
    "BMRI.JK": {"volatility": 0.016}, "BBNI.JK": {"volatility": 0.019},
    "TLKM.JK": {"volatility": 0.014}, "EXCL.JK": {"volatility": 0.022},
    "ISAT.JK": {"volatility": 0.020},
    "ADRO.JK": {"volatility": 0.025}, "PTBA.JK": {"volatility": 0.023},
    "PGAS.JK": {"volatility": 0.021},
    "ICBP.JK": {"volatility": 0.013}, "INDF.JK": {"volatility": 0.014},
    "UNVR.JK": {"volatility": 0.012},
    "GOTO.JK": {"volatility": 0.035}, "BUKA.JK": {"volatility": 0.038},
    "BSDE.JK": {"volatility": 0.020}, "SMRA.JK": {"volatility": 0.022},
    "JSMR.JK": {"volatility": 0.016}, "WIKA.JK": {"volatility": 0.028},
    "^JKSE":   {"volatility": 0.010},
}

def get_last_close(cursor, ticker):
    cursor.execute("""
        SELECT close FROM raw.stock_prices
        WHERE ticker = %s
        ORDER BY trade_date DESC
        LIMIT 1
    """, (ticker,))
    result = cursor.fetchone()
    return float(result[0]) if result else None

def get_last_date(cursor):
    """Ambil tanggal terakhir di database"""
    cursor.execute("SELECT MAX(trade_date) FROM raw.stock_prices")
    result = cursor.fetchone()
    return result[0] if result else None

def generate_ohlcv(prev_close, volatility, base_volume=50_000_000):
    daily_return = np.random.normal(0.0003, volatility)
    gap = np.random.normal(0, volatility * 0.3)
    open_price  = round(prev_close * (1 + gap), 0)
    close_price = round(prev_close * (1 + daily_return), 0)
    intraday    = abs(np.random.normal(0, volatility * 0.8))
    high_price  = round(max(open_price, close_price) * (1 + intraday), 0)
    low_price   = round(min(open_price, close_price) * (1 - intraday), 0)
    volume      = int(base_volume * np.random.lognormal(0, 0.5))

    return {
        "open":   max(open_price, 1),
        "high":   max(high_price, open_price, close_price),
        "low":    min(low_price, open_price, close_price),
        "close":  max(close_price, 1),
        "volume": volume,
    }

def main():
    import pytz
    from datetime import datetime
    wib = pytz.timezone('Asia/Jakarta')
    today = datetime.now(wib).date()

    # Skip kalau weekend
    if today.weekday() >= 5:
        print(f"Hari ini {today} adalah weekend — pipeline tidak dijalankan")
        return

    print("=" * 55)
    print("GENERATE DAILY DATA — Indonesia BEI (Synthetic)")
    print(f"Tanggal: {today}")
    print("=" * 55)

    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()

    last_date = get_last_date(cursor)
    print(f"Data terakhir di database: {last_date}")

    if last_date and last_date >= today:
        print(f"✅ Data hari ini ({today}) sudah ada — pipeline selesai")
        cursor.close()
        conn.close()
        return

    # Generate data untuk semua tanggal yang belum ada
    new_records = []
    current_date = (last_date + timedelta(days=1)) if last_date else today

    while current_date <= today:
        if current_date.weekday() < 5:  # Hari kerja saja
            for ticker, config in STOCKS.items():
                prev_close = get_last_close(cursor, ticker)
                if prev_close is None:
                    print(f"  ⚠️  {ticker}: tidak ada data sebelumnya, skip")
                    continue

                ohlcv = generate_ohlcv(prev_close, config["volatility"])
                new_records.append((
                    ticker, current_date,
                    ohlcv["open"], ohlcv["high"], ohlcv["low"],
                    ohlcv["close"], ohlcv["volume"]
                ))

        current_date += timedelta(days=1)

    if not new_records:
        print("Tidak ada data baru untuk digenerate")
        cursor.close()
        conn.close()
        return

    execute_values(cursor, """
        INSERT INTO raw.stock_prices
            (ticker, trade_date, open, high, low, close, volume)
        VALUES %s
        ON CONFLICT (ticker, trade_date) DO NOTHING
    """, new_records)

    conn.commit()
    cursor.close()
    conn.close()

    days = len(new_records) // len(STOCKS)
    print(f"✅ {len(new_records)} records berhasil digenerate ({days} hari trading)")

if __name__ == "__main__":
    main()