WITH source AS (
    SELECT * FROM {{ source('raw', 'stock_info') }}
)

SELECT
    ticker,
    company_name,
    sector,
    market_cap,
    pe_ratio,
    dividend_yield,
    week_52_high,
    week_52_low,
    updated_at,

    -- Kategorisasi market cap
    CASE
        WHEN market_cap >= 100000000000000 THEN 'Large Cap'
        WHEN market_cap >= 10000000000000  THEN 'Mid Cap'
        WHEN market_cap IS NOT NULL        THEN 'Small Cap'
        ELSE 'Unknown'
    END AS market_cap_category

FROM source