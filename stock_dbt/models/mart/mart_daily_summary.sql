WITH prices AS (
    SELECT * FROM {{ ref('stg_stock_prices') }}
),

info AS (
    SELECT * FROM {{ ref('stg_stock_info') }}
),

daily AS (
    SELECT
        p.trade_date                                AS summary_date,

        -- Jumlah saham naik dan turun
        COUNT(*) FILTER (
            WHERE p.price_direction = 'up'
            AND i.sector != 'Index'
        )                                           AS advancers,

        COUNT(*) FILTER (
            WHERE p.price_direction = 'down'
            AND i.sector != 'Index'
        )                                           AS decliners,

        COUNT(*) FILTER (
            WHERE p.price_direction = 'flat'
            AND i.sector != 'Index'
        )                                           AS unchanged,

        -- Total volume semua saham
        SUM(p.volume) FILTER (
            WHERE i.sector != 'Index'
        )                                           AS total_volume,

        -- Average return semua saham
        ROUND(AVG(p.daily_return_pct) FILTER (
            WHERE i.sector != 'Index'
            AND p.daily_return_pct IS NOT NULL
        ), 4)                                       AS avg_market_return,

        -- Top gainer
        MAX(p.daily_return_pct) FILTER (
            WHERE i.sector != 'Index'
        )                                           AS best_return,

        -- Top loser
        MIN(p.daily_return_pct) FILTER (
            WHERE i.sector != 'Index'
        )                                           AS worst_return,

        -- Market sentiment
        CASE
            WHEN COUNT(*) FILTER (WHERE p.price_direction = 'up' AND i.sector != 'Index')
                > COUNT(*) FILTER (WHERE p.price_direction = 'down' AND i.sector != 'Index')
                THEN 'Bullish'
            WHEN COUNT(*) FILTER (WHERE p.price_direction = 'down' AND i.sector != 'Index')
                > COUNT(*) FILTER (WHERE p.price_direction = 'up' AND i.sector != 'Index')
                THEN 'Bearish'
            ELSE 'Neutral'
        END                                         AS market_sentiment

    FROM prices p
    LEFT JOIN info i ON p.ticker = i.ticker
    GROUP BY p.trade_date
)

SELECT * FROM daily ORDER BY summary_date DESC