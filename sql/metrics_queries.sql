-- Dashboard metric queries for the Smart Financial Data Intelligence Platform.
-- Each query answers one metric from the project doc's "Dashboard Metrics" list.
-- These are the reference queries; Power BI will run equivalent logic internally.

-- 1. Total transaction count and total transaction value
SELECT
    COUNT(*) AS total_transaction_count,
    SUM(amount) AS total_transaction_value
FROM transactions;

-- 2. Incoming versus outgoing transaction value
SELECT
    direction,
    COUNT(*) AS transaction_count,
    SUM(amount) AS total_value
FROM transactions
GROUP BY direction;

-- 3. Daily transaction trend
SELECT
    transaction_date,
    COUNT(*) AS transaction_count,
    SUM(amount) AS total_value
FROM transactions
GROUP BY transaction_date
ORDER BY transaction_date;

-- 3b. Monthly transaction trend
SELECT
    DATE_TRUNC('month', transaction_date) AS month,
    COUNT(*) AS transaction_count,
    SUM(amount) AS total_value
FROM transactions
GROUP BY DATE_TRUNC('month', transaction_date)
ORDER BY month;

-- 4. Transaction count and value by region
SELECT
    region,
    COUNT(*) AS transaction_count,
    SUM(amount) AS total_value
FROM transactions
GROUP BY region
ORDER BY total_value DESC;

-- 4b. Transaction count and value by transaction type
SELECT
    transaction_type,
    COUNT(*) AS transaction_count,
    SUM(amount) AS total_value
FROM transactions
GROUP BY transaction_type
ORDER BY total_value DESC;

-- 5. Number and percentage of records flagged as anomalous
-- (anomaly_results is populated in Phase 5 - returns 0 rows until then)
SELECT
    COUNT(*) FILTER (WHERE is_anomaly) AS anomalous_count,
    COUNT(*) AS total_scored,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE is_anomaly) / NULLIF(COUNT(*), 0),
        2
    ) AS anomalous_pct
FROM anomaly_results;

-- 6. Data quality counts: accepted vs rejected, by pipeline run
SELECT
    run_id,
    started_at,
    status,
    records_processed,
    records_rejected,
    ROUND(
        100.0 * records_rejected / NULLIF(records_processed + records_rejected, 0),
        2
    ) AS rejected_pct
FROM pipeline_logs
ORDER BY started_at DESC;

-- 6b. Latest overall data quality snapshot
SELECT
    (SELECT COUNT(*) FROM customers) AS accepted_customers,
    (SELECT COUNT(*) FROM transactions) AS accepted_transactions;
