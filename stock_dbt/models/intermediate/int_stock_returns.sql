WITH prices AS (
    SELECT * FROM {{ ref('stg_stock_prices') }}
),

returns AS (
    SELECT
        ticker,
        trade_date,
        close_price,
        daily_return_pct,

        -- Cumulative return dari awal data
        ROUND(
            (close_price / FIRST_VALUE(close_price) OVER (
                PARTITION BY ticker ORDER BY trade_date
            ) - 1) * 100
        , 4) AS cumulative_return_pct,

        -- Weekly return (5 hari)
        ROUND(
            (close_price / NULLIF(
                LAG(close_price, 5) OVER (PARTITION BY ticker ORDER BY trade_date)
            , 0) - 1) * 100
        , 4) AS weekly_return_pct,

        -- Monthly return (21 hari)
        ROUND(
            (close_price / NULLIF(
                LAG(close_price, 21) OVER (PARTITION BY ticker ORDER BY trade_date)
            , 0) - 1) * 100
        , 4) AS monthly_return_pct,

        -- Quarterly return (63 hari)
        ROUND(
            (close_price / NULLIF(
                LAG(close_price, 63) OVER (PARTITION BY ticker ORDER BY trade_date)
            , 0) - 1) * 100
        , 4) AS quarterly_return_pct

    FROM prices
)

SELECT * FROM returns