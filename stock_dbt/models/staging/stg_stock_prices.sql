WITH source AS (
    SELECT * FROM {{ source('raw', 'stock_prices') }}
),

cleaned AS (
    SELECT
        ticker,
        trade_date,
        open                                        AS open_price,
        high                                        AS high_price,
        low                                         AS low_price,
        close                                       AS close_price,
        volume,
        ingested_at,

        -- Daily return
        ROUND(
            (close - LAG(close) OVER (PARTITION BY ticker ORDER BY trade_date))
            / NULLIF(LAG(close) OVER (PARTITION BY ticker ORDER BY trade_date), 0) * 100
        , 4)                                        AS daily_return_pct,

        -- Price change nominal
        ROUND(
            close - LAG(close) OVER (PARTITION BY ticker ORDER BY trade_date)
        , 2)                                        AS price_change,

        -- Intraday range
        ROUND(high - low, 2)                        AS intraday_range,

        -- Apakah harga naik atau turun
        CASE
            WHEN close > LAG(close) OVER (PARTITION BY ticker ORDER BY trade_date)
                THEN 'up'
            WHEN close < LAG(close) OVER (PARTITION BY ticker ORDER BY trade_date)
                THEN 'down'
            ELSE 'flat'
        END                                         AS price_direction,

        -- Filter data valid
        CASE
            WHEN close IS NULL THEN FALSE
            WHEN volume IS NULL THEN FALSE
            WHEN high < low THEN FALSE
            WHEN close <= 0 THEN FALSE
            ELSE TRUE
        END                                         AS is_valid

    FROM source
    WHERE close IS NOT NULL
      AND volume IS NOT NULL
)

SELECT * FROM cleaned WHERE is_valid = TRUE