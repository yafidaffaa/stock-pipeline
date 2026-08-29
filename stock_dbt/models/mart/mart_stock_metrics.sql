WITH indicators AS (
    SELECT * FROM {{ ref('int_stock_indicators') }}
),

returns AS (
    SELECT * FROM {{ ref('int_stock_returns') }}
),

info AS (
    SELECT * FROM {{ ref('stg_stock_info') }}
),

combined AS (
    SELECT
        ind.ticker,
        ind.trade_date,
        i.company_name,
        i.sector,
        ind.close_price,
        ind.volume,
        ind.daily_return_pct,
        ind.price_direction,
        ind.ma_7,
        ind.ma_20,
        ind.ma_50,
        ind.avg_volume_30d,
        ind.volume_ratio,
        ind.volatility_30d,
        ind.rsi_14,
        ind.week_52_high,
        ind.week_52_low,
        r.weekly_return_pct,
        r.monthly_return_pct,
        r.quarterly_return_pct,
        r.cumulative_return_pct,

        -- Posisi harga vs 52wk high/low
        ROUND(
            (ind.close_price - ind.week_52_low)
            / NULLIF(ind.week_52_high - ind.week_52_low, 0) * 100
        , 2)                                        AS price_position_pct,

        -- MA signal
        CASE
            WHEN ind.close_price > ind.ma_20
                AND ind.ma_7 > ind.ma_20
                THEN 'Bullish'
            WHEN ind.close_price < ind.ma_20
                AND ind.ma_7 < ind.ma_20
                THEN 'Bearish'
            ELSE 'Neutral'
        END                                         AS ma_signal,

        -- RSI signal
        CASE
            WHEN ind.rsi_14 > 70 THEN 'Overbought'
            WHEN ind.rsi_14 < 30 THEN 'Oversold'
            ELSE 'Normal'
        END                                         AS rsi_signal

    FROM indicators ind
    LEFT JOIN returns r ON ind.ticker = r.ticker
                       AND ind.trade_date = r.trade_date
    LEFT JOIN info i    ON ind.ticker = i.ticker
)

SELECT * FROM combined ORDER BY trade_date DESC, ticker