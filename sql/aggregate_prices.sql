-- High-volume aggregation of PriceCatcher records.
-- Parameters are injected by src/build_panel.py.

WITH selected_items AS (
    SELECT
        item_code,
        item,
        unit,
        item_group,
        item_category
    FROM read_parquet('{item_lookup}')
    WHERE {item_filter}
),
prices AS (
    SELECT
        CAST(p.date AS DATE) AS date,
        date_trunc('month', CAST(p.date AS DATE)) AS month,
        p.premise_code,
        p.item_code,
        p.price,
        i.item,
        i.unit,
        i.item_group,
        i.item_category,
        pr.premise_type,
        pr.state,
        pr.district
    FROM read_parquet('{price_glob}') AS p
    INNER JOIN selected_items AS i USING (item_code)
    LEFT JOIN read_parquet('{premise_lookup}') AS pr USING (premise_code)
    WHERE
        p.price IS NOT NULL
        AND p.price > 0
        AND pr.state IS NOT NULL
),
state_month AS (
    SELECT
        month,
        state,
        item_code,
        item,
        unit,
        COUNT(*) AS n_observations,
        COUNT(DISTINCT premise_code) AS n_premises,
        median(price) AS price_median,
        quantile_cont(price, 0.25) AS price_q25,
        quantile_cont(price, 0.75) AS price_q75,
        min(price) AS price_min,
        max(price) AS price_max
    FROM prices
    GROUP BY ALL
),
national_month AS (
    SELECT
        month,
        item_code,
        median(price) AS national_price_median
    FROM prices
    GROUP BY ALL
)
SELECT
    s.*,
    s.price_q75 - s.price_q25 AS price_iqr,
    CASE
        WHEN s.price_median > 0
        THEN (s.price_q75 - s.price_q25) / s.price_median
        ELSE NULL
    END AS dispersion_iqr_over_median,
    n.national_price_median,
    CASE
        WHEN n.national_price_median > 0
        THEN s.price_median / n.national_price_median - 1
        ELSE NULL
    END AS state_to_national_gap
FROM state_month AS s
LEFT JOIN national_month AS n
    USING (month, item_code)
ORDER BY item_code, state, month;
