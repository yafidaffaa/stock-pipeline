WITH prices AS (
    SELECT * FROM {{ ref('stg_stock_prices') }}
),

indicators AS (
    SELECT
        ticker,
        trade_date,
        close_price,
        volume,
        daily_return_pct,
        price_direction,

        -- Moving Averages
        ROUND(AVG(close_price) OVER (
            PARTITION BY ticker
            ORDER BY trade_date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ), 2) AS ma_7,

        ROUND(AVG(close_price) OVER (
            PARTITION BY ticker
            ORDER BY trade_date
            ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
        ), 2) AS ma_20,

        ROUND(AVG(close_price) OVER (
            PARTITION BY ticker
            ORDER BY trade_date
            ROWS BETWEEN 49 PRECEDING AND CURRENT ROW
        ), 2) AS ma_50,

        -- Volume moving average 30 hari
        ROUND(AVG(volume) OVER (
            PARTITION BY ticker
            ORDER BY trade_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ), 0) AS avg_volume_30d,

        -- Volume ratio vs rata-rata
        ROUND(
            volume::NUMERIC / NULLIF(
                AVG(volume) OVER (
                    PARTITION BY ticker
                    ORDER BY trade_date
                    ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
                ), 0
            ), 4
        ) AS volume_ratio,

        -- Volatilitas 30 hari (standar deviasi return)
        ROUND(STDDEV(daily_return_pct) OVER (
            PARTITION BY ticker
            ORDER BY trade_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ), 4) AS volatility_30d,

        -- RSI 14 hari (simplified)
        ROUND(
            100 - (100 / (1 + (
                NULLIF(AVG(CASE WHEN daily_return_pct > 0 THEN daily_return_pct ELSE 0 END) OVER (
                    PARTITION BY ticker ORDER BY trade_date
                    ROWS BETWEEN 13 PRECEDING AND CURRENT ROW
                ), 0)
                /
                NULLIF(ABS(AVG(CASE WHEN daily_return_pct < 0 THEN daily_return_pct ELSE 0 END) OVER (
                    PARTITION BY ticker ORDER BY trade_date
                    ROWS BETWEEN 13 PRECEDING AND CURRENT ROW
                )), 0)
            )))
        , 2) AS rsi_14,

        -- 52 week high & low
        MAX(close_price) OVER (
            PARTITION BY ticker
            ORDER BY trade_date
            ROWS BETWEEN 251 PRECEDING AND CURRENT ROW
        ) AS week_52_high,

        MIN(close_price) OVER (
            PARTITION BY ticker
            ORDER BY trade_date
            ROWS BETWEEN 251 PRECEDING AND CURRENT ROW
        ) AS week_52_low

    FROM prices
)

SELECT * FROM indicators