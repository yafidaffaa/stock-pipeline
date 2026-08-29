WITH prices AS (
    SELECT * FROM {{ ref('stg_stock_prices') }}
),

info AS (
    SELECT * FROM {{ ref('stg_stock_info') }}
),

indicators AS (
    SELECT * FROM {{ ref('int_stock_indicators') }}
),

sector_daily AS (
    SELECT
        p.trade_date,
        i.sector,
        COUNT(DISTINCT p.ticker)                    AS stock_count,
        ROUND(AVG(p.daily_return_pct), 4)           AS avg_return,
        SUM(p.volume)                               AS total_volume,
        ROUND(AVG(ind.volatility_30d), 4)           AS avg_volatility,
        ROUND(AVG(i.pe_ratio), 2)                   AS avg_pe_ratio,
        COUNT(*) FILTER (
            WHERE p.price_direction = 'up'
        )                                           AS advancers,
        COUNT(*) FILTER (
            WHERE p.price_direction = 'down'
        )                                           AS decliners,
        MAX(p.daily_return_pct)                     AS best_stock_return,
        MIN(p.daily_return_pct)                     AS worst_stock_return

    FROM prices p
    LEFT JOIN info i      ON p.ticker = i.ticker
    LEFT JOIN indicators ind ON p.ticker = ind.ticker
                           AND p.trade_date = ind.trade_date
    WHERE i.sector != 'Index'
    GROUP BY p.trade_date, i.sector
)

SELECT * FROM sector_daily ORDER BY trade_date DESC, sector