-- Smart Financial Data Intelligence Platform - database schema
-- Run against the smart_financial_db database.

CREATE TABLE IF NOT EXISTS customers (
    customer_id   VARCHAR(20) PRIMARY KEY,
    name          VARCHAR(200) NOT NULL,
    region        VARCHAR(50) NOT NULL,
    signup_date   DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id    VARCHAR(20) PRIMARY KEY,
    customer_id        VARCHAR(20) NOT NULL REFERENCES customers(customer_id),
    transaction_date   DATE NOT NULL,
    amount              NUMERIC(14, 2) NOT NULL CHECK (amount >= 0),
    direction            VARCHAR(10) NOT NULL CHECK (direction IN ('incoming', 'outgoing')),
    transaction_type    VARCHAR(30) NOT NULL,
    region               VARCHAR(50) NOT NULL
);

-- Cleaned/transformed copy of transactions, kept separate so raw validated
-- data and ETL-transformed data can evolve independently.
CREATE TABLE IF NOT EXISTS processed_transactions (
    transaction_id    VARCHAR(20) PRIMARY KEY REFERENCES transactions(transaction_id),
    customer_id        VARCHAR(20) NOT NULL REFERENCES customers(customer_id),
    transaction_date   DATE NOT NULL,
    amount              NUMERIC(14, 2) NOT NULL,
    direction            VARCHAR(10) NOT NULL,
    transaction_type    VARCHAR(30) NOT NULL,
    region               VARCHAR(50) NOT NULL,
    processed_at         TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS anomaly_results (
    transaction_id    VARCHAR(20) PRIMARY KEY REFERENCES transactions(transaction_id),
    anomaly_score       NUMERIC(10, 6) NOT NULL,
    is_anomaly           BOOLEAN NOT NULL,
    model_version        VARCHAR(50) NOT NULL,
    scored_at             TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS daily_analytics (
    analytics_date      DATE NOT NULL,
    region                VARCHAR(50) NOT NULL,
    transaction_count     INTEGER NOT NULL,
    total_incoming         NUMERIC(14, 2) NOT NULL,
    total_outgoing          NUMERIC(14, 2) NOT NULL,
    PRIMARY KEY (analytics_date, region)
);

CREATE TABLE IF NOT EXISTS pipeline_logs (
    run_id               SERIAL PRIMARY KEY,
    started_at            TIMESTAMP NOT NULL,
    finished_at            TIMESTAMP,
    status                 VARCHAR(20) NOT NULL,
    records_processed      INTEGER DEFAULT 0,
    records_rejected       INTEGER DEFAULT 0,
    error_details           TEXT
);

CREATE INDEX IF NOT EXISTS idx_transactions_customer ON transactions(customer_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_transactions_region ON transactions(region);
