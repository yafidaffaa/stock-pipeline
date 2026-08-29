WITH indicators AS (
    SELECT * FROM {{ ref('int_stock_indicators') }}
),

prices AS (
    SELECT * FROM {{ ref('stg_stock_prices') }}
),

info AS (
    SELECT * FROM {{ ref('stg_stock_info') }}
),

anomalies AS (
    SELECT
        ind.ticker,
        ind.trade_date                              AS detected_at,
        i.company_name,
        i.sector,
        ind.close_price,
        ind.daily_return_pct,
        ind.volume,
        ind.volume_ratio,
        ind.rsi_14,
        ind.week_52_high,
        ind.week_52_low,

        -- Tipe anomali
        CASE
            WHEN ind.volume_ratio > 2.5
                THEN 'Volume Spike'
            WHEN ind.close_price >= ind.week_52_high
                THEN 'Price Breakout High'
            WHEN ind.close_price <= ind.week_52_low
                THEN 'Price Breakout Low'
            WHEN ABS(ind.daily_return_pct) > 3.0
                THEN 'Unusual Price Movement'
            WHEN ind.rsi_14 > 75
                THEN 'Overbought'
            WHEN ind.rsi_14 < 25
                THEN 'Oversold'
            ELSE NULL
        END                                         AS signal_type,

        -- Kekuatan sinyal
        CASE
            WHEN ind.volume_ratio > 5 OR ABS(ind.daily_return_pct) > 5
                THEN 'Strong'
            WHEN ind.volume_ratio > 2.5 OR ABS(ind.daily_return_pct) > 3
                THEN 'Moderate'
            ELSE 'Weak'
        END                                         AS signal_strength

    FROM indicators ind
    LEFT JOIN info i ON ind.ticker = i.ticker
    WHERE i.sector != 'Index'
),

filtered AS (
    SELECT * FROM anomalies
    WHERE signal_type IS NOT NULL
)

SELECT * FROM filtered ORDER BY detected_at DESC, ticker