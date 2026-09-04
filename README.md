# Indonesia Stock Market Intelligence Pipeline

> ⚠️ **Disclaimer:** Data yang digunakan dalam project ini adalah **synthetic/simulated data** yang dibuat dengan stock market simulator berbasis Geometric Brownian Motion. Data ini **bukan data pasar BEI yang sebenarnya** dan tidak boleh digunakan untuk keputusan investasi. Project ini dibuat murni untuk tujuan portofolio Data Engineering & Data Analytics.

---

## 🎯 Overview

End-to-end automated data pipeline yang mensimulasikan pasar saham Indonesia (BEI) — mulai dari data generation, transformasi, quality testing, hingga dashboard analitik yang dapat diakses secara publik dan terupdate setiap hari kerja secara otomatis.

**Live Dashboard:** [Indonesia Stock Market Intelligence Dashboard] [https://datastudio.google.com/your-dashboard-link](https://datastudio.google.com/reporting/265c4aed-02c9-423d-b171-fa58a5b8b159)

<img width="1535" height="730" alt="dashboard analysis" src="https://github.com/user-attachments/assets/81584642-73fb-4f89-afa4-edb79ceb9d0d" />

## 🏗️ Arsitektur

```
GitHub Actions (Scheduler — setiap hari kerja jam 20:00 WIB)
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│              Stock Market Simulator                      │
│         Python + Geometric Brownian Motion               │
│    Menghasilkan OHLCV untuk 20 saham BEI secara         │
│    realistis berdasarkan harga hari sebelumnya           │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│                Supabase (PostgreSQL)                     │
│                                                         │
│  raw.stock_prices     → Data OHLCV mentah harian        │
│  raw.stock_info       → Metadata 20 perusahaan          │
│  staging.*            → Data bersih + kalkulasi dasar   │
│  intermediate.*       → Indikator teknikal              │
│  mart.*               → Agregasi siap analisis          │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│                    dbt                                   │
│                                                         │
│  8 models → staging, intermediate, mart                 │
│  9+ data quality tests                                  │
│  Kalkulasi: MA, RSI, Beta, Volatilitas, Anomali         │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│              Google Sheets → Looker Studio               │
│                                                         │
│  Dashboard publik dengan 5 halaman analisis             │
│  Terupdate otomatis setiap hari kerja                   │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Fungsi |
|---|---|---|
| **Orchestration** | GitHub Actions | Scheduler otomatis harian |
| **Data Generation** | Python + NumPy | Stock market simulator |
| **Database** | Supabase (PostgreSQL) | Data warehouse |
| **Transformation** | dbt 1.8 + dbt-postgres | Staging → Intermediate → Mart |
| **Export** | Python + gspread | Sync ke Google Sheets |
| **Dashboard** | Looker Studio | Visualisasi publik |
| **Version Control** | GitHub | Source code management |

---

## 📊 Data Coverage

**20 Saham BEI yang Disimulasikan:**

| Sektor | Ticker |
|---|---|
| Perbankan | BBCA.JK, BBRI.JK, BMRI.JK, BBNI.JK |
| Telekomunikasi | TLKM.JK, EXCL.JK, ISAT.JK |
| Energi | ADRO.JK, PTBA.JK, PGAS.JK |
| Consumer | ICBP.JK, INDF.JK, UNVR.JK |
| Teknologi | GOTO.JK, BUKA.JK |
| Properti | BSDE.JK, SMRA.JK |
| Infrastruktur | JSMR.JK, WIKA.JK |
| Index | ^JKSE |

**Periode data:** Januari 2023 — sekarang (terupdate harian)

---

## 🗄️ Database Schema

```
Supabase PostgreSQL
├── raw
│   ├── stock_prices     (OHLCV harian per ticker)
│   └── stock_info       (metadata perusahaan)
├── staging
│   ├── stg_stock_prices (cleaned + daily return + price direction)
│   └── stg_stock_info   (cleaned metadata + market cap category)
├── intermediate
│   ├── int_stock_indicators  (MA 7/20/50, RSI 14, volatilitas, volume ratio)
│   └── int_stock_returns     (weekly, monthly, quarterly, cumulative return)
└── mart
    ├── mart_daily_summary       (ringkasan pasar harian)
    ├── mart_sector_performance  (performa per sektor)
    ├── mart_stock_metrics       (metrik lengkap per saham)
    └── mart_anomaly_signals     (deteksi anomali volume & harga)
```

---

## 🧪 Data Quality Tests

Pipeline dilengkapi **9 data quality tests** yang berjalan setiap hari:

| Test | Kolom | Deskripsi |
|---|---|---|
| `not_null` | ticker | Kode saham tidak boleh kosong |
| `not_null` | trade_date | Tanggal tidak boleh kosong |
| `not_null` | close_price | Harga penutupan tidak boleh kosong |
| `not_null` | volume | Volume tidak boleh kosong |
| `not_null` | sector | Sektor tidak boleh kosong |
| `unique` | ticker (stock_info) | Setiap ticker unik di tabel info |
| `accepted_values` | price_direction | Hanya: up, down, flat |
| `accepted_values` | sector | Hanya 8 sektor yang valid |
| `not_null` | ticker (stock_info) | Ticker info tidak boleh kosong |

---

## 📈 Dashboard

Dashboard Looker Studio terdiri dari **5 halaman analisis:**

**Page 1 — Executive Overview**
- Market sentiment hari ini (Bullish/Bearish/Neutral)
- Advancers vs decliners scorecard
- Advancers vs decliners over time (bar chart)
- Sentiment calendar (heatmap harian)
- Total volume trend
- Best vs worst return harian

**Page 2 — Market Breadth**
- Distribusi return harian semua saham
- Volume analysis per saham
- Tabel ringkasan lengkap semua saham

**Page 3 — Sector Performance**
- Average return per sektor
- Total volume per sektor
- Sector return matrix

**Page 4 — Stock Explorer**
- Filter interaktif per ticker
- Line chart harga + moving average
- RSI dan signal indicator
- Return analysis (weekly, monthly, quarterly)

**Page 5 — Anomaly Radar**
- Alert table sinyal anomali hari ini
- Volume spike detection
- Price breakout signals
- Timeline anomali historis

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.12+
- PostgreSQL (Supabase free tier)
- GitHub account
- Google account (untuk Sheets + Looker Studio)

### Langkah Instalasi

**1. Clone repository**
```bash
git clone https://github.com/yafidaffaa/stock-pipeline.git
cd stock-pipeline
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Setup Supabase**
- Buat project di [supabase.com](https://supabase.com)
- Jalankan SQL berikut di SQL Editor:

```sql
CREATE SCHEMA raw;
CREATE SCHEMA staging;
CREATE SCHEMA intermediate;
CREATE SCHEMA mart;

CREATE TABLE raw.stock_prices (
    id          SERIAL PRIMARY KEY,
    ticker      TEXT NOT NULL,
    trade_date  DATE NOT NULL,
    open        NUMERIC,
    high        NUMERIC,
    low         NUMERIC,
    close       NUMERIC,
    volume      BIGINT,
    ingested_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(ticker, trade_date)
);

CREATE TABLE raw.stock_info (
    id             SERIAL PRIMARY KEY,
    ticker         TEXT NOT NULL UNIQUE,
    company_name   TEXT,
    sector         TEXT,
    market_cap     NUMERIC,
    pe_ratio       NUMERIC,
    dividend_yield NUMERIC,
    week_52_high   NUMERIC,
    week_52_low    NUMERIC,
    updated_at     TIMESTAMP DEFAULT NOW()
);
```

**4. Setup environment variables**
```bash
cp .env.example .env
```
Isi `.env` dengan kredensial kamu.

**5. Generate historical data**
```bash
python scripts/generate_historical.py
```

**6. Setup dbt**
```bash
cd stock_dbt
dbt run
dbt test
```

**7. Setup GitHub Secrets**

Tambahkan secrets berikut di repository Settings → Secrets → Actions:

| Secret | Keterangan |
|---|---|
| `SUPABASE_DB_URL` | Connection string Supabase |
| `DBT_HOST` | Host Supabase pooler |
| `DBT_PORT` | Port Supabase pooler (6543) |
| `DBT_USER` | User Supabase pooler |
| `DBT_PASSWORD` | Password database |
| `DBT_DBNAME` | Nama database |
| `SPREADSHEET_ID` | ID Google Spreadsheet |
| `GOOGLE_SHEETS_CREDS` | Service account JSON (seluruh isi file) |

**8. Pipeline berjalan otomatis**

Setelah semua setup selesai, pipeline akan berjalan otomatis setiap hari kerja jam 20:00 WIB tanpa perlu intervensi manual.

---

## 📁 Struktur Project

```
stock-pipeline/
├── .github/
│   └── workflows/
│       └── daily_pipeline.yml    # GitHub Actions workflow
├── scripts/
│   ├── generate_historical.py    # Generate data historis 2023–sekarang
│   ├── generate_daily.py         # Generate data harian (dijalankan otomatis)
│   └── export_to_sheets.py       # Export mart tables ke Google Sheets
├── stock_dbt/
│   ├── models/
│   │   ├── staging/              # Cleaning + kalkulasi dasar
│   │   ├── intermediate/         # Indikator teknikal (MA, RSI, dll)
│   │   └── mart/                 # Agregasi siap analisis
│   ├── macros/
│   ├── dbt_project.yml
│   └── profiles.yml
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🔄 Pipeline Flow

```
Setiap hari kerja jam 20:00 WIB
          │
          ▼
generate_daily.py
→ Ambil harga close kemarin dari DB
→ Simulasikan pergerakan harga hari ini (GBM)
→ Insert ke raw.stock_prices
          │
          ▼
dbt run
→ staging: cleaning + daily return
→ intermediate: MA, RSI, volatilitas, beta
→ mart: summary, sector, metrics, anomaly
          │
          ▼
dbt test
→ 9 data quality tests harus lulus semua
          │
          ▼
export_to_sheets.py
→ Query 4 mart tables dari Supabase
→ Upload ke Google Sheets
→ Looker Studio dashboard terupdate otomatis
```

---

## 💡 Catatan Arsitektur

Project ini sengaja menggunakan **synthetic data** sebagai solusi untuk menghindari keterbatasan API data saham gratis (rate limit, data tidak lengkap, pemblokiran IP). Pendekatan ini membuktikan kemampuan membangun pipeline yang:

- **Robust** — retry logic, error handling, data quality tests
- **Scalable** — arsitektur raw → staging → intermediate → mart
- **Cost-efficient** — seluruh stack gratis tanpa billing account
- **Production-like** — GitHub Actions sebagai orchestrator, dbt untuk transformasi, Supabase sebagai managed database

Konsep dan arsitektur yang sama berlaku identik untuk data saham real menggunakan Bloomberg API, Refinitiv, atau data provider berbayar lainnya.

---

## 👤 Author

**Yafi Daffa Andriansyah**
Fresh Graduate — Teknologi Informasi
