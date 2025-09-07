-- VedhaVriddhi ClickHouse Analytics Schema
-- High-performance analytics database for trading data

CREATE DATABASE IF NOT EXISTS vedhavriddhi_analytics;

USE vedhavriddhi_analytics;

-- Market data time series table
CREATE TABLE IF NOT EXISTS market_data_ts
(
    timestamp DateTime64(3, 'Asia/Kolkata'),
    symbol LowCardinality(String),
    bid_price Nullable(Decimal64(4)),
    ask_price Nullable(Decimal64(4)),
    last_price Nullable(Decimal64(4)),
    volume Decimal64(2),
    yield_to_maturity Nullable(Decimal64(4)),
    duration Nullable(Decimal64(4)),
    accrued_interest Nullable(Decimal64(4)),
    source LowCardinality(String),
    exchange LowCardinality(String)
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (symbol, timestamp)
TTL timestamp + INTERVAL 2 YEAR;

-- Trade analytics table
CREATE TABLE IF NOT EXISTS trade_analytics
(
    trade_id UUID,
    timestamp DateTime64(3, 'Asia/Kolkata'),
    symbol LowCardinality(String),
    side Enum('buy' = 1, 'sell' = 2),
    quantity Decimal64(2),
    price Decimal64(4),
    value Decimal64(2),
    buyer_account_id UUID,
    seller_account_id UUID,
    trade_type LowCardinality(String),
    settlement_date Date,
    commission Decimal64(2),
    taxes Decimal64(2)
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (timestamp, symbol)
TTL timestamp + INTERVAL 7 YEAR;

-- Position snapshots for historical analysis
CREATE TABLE IF NOT EXISTS position_snapshots
(
    snapshot_date Date,
    account_id UUID,
    symbol LowCardinality(String),
    quantity Decimal64(2),
    average_price Decimal64(4),
    market_value Decimal64(2),
    unrealized_pnl Decimal64(2),
    realized_pnl Decimal64(2),
    duration Nullable(Decimal64(4)),
    convexity Nullable(Decimal64(4)),
    sector LowCardinality(String),
    rating LowCardinality(String)
)
ENGINE = ReplacingMergeTree()
PARTITION BY toYYYYMM(snapshot_date)
ORDER BY (snapshot_date, account_id, symbol);

-- Risk metrics aggregation table
CREATE TABLE IF NOT EXISTS risk_metrics_daily
(
    date Date,
    account_id UUID,
    portfolio_value Decimal64(2),
    var_1d Decimal64(2),
    var_10d Decimal64(2),
    expected_shortfall Decimal64(2),
    maximum_drawdown Decimal64(4),
    volatility Decimal64(4),
    beta Decimal64(4),
    modified_duration Decimal64(4),
    convexity Decimal64(4),
    credit_spread_risk Decimal64(2)
)
ENGINE = ReplacingMergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (date, account_id);

-- Order flow analytics
CREATE TABLE IF NOT EXISTS order_flow_analytics
(
    timestamp DateTime64(3, 'Asia/Kolkata'),
    symbol LowCardinality(String),
    side Enum('buy' = 1, 'sell' = 2),
    order_type LowCardinality(String),
    quantity Decimal64(2),
    price Nullable(Decimal64(4)),
    time_in_force LowCardinality(String),
    order_status LowCardinality(String),
    fill_time_ms UInt32,
    account_type LowCardinality(String),
    user_type LowCardinality(String)
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (timestamp, symbol);

-- Materialized view for real-time portfolio valuation
CREATE MATERIALIZED VIEW IF NOT EXISTS portfolio_realtime_mv
ENGINE = AggregatingMergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (date, account_id)
AS SELECT
    toDate(timestamp) as date,
    buyer_account_id as account_id,
    sum(value) as total_traded_value,
    count() as trade_count,
    avg(price) as avg_price,
    max(timestamp) as last_trade_time
FROM trade_analytics
GROUP BY date, account_id;

-- Index for faster symbol lookups
CREATE INDEX IF NOT EXISTS idx_symbol_timestamp ON market_data_ts (symbol, timestamp) TYPE minmax GRANULARITY 1;
CREATE INDEX IF NOT EXISTS idx_account_date ON position_snapshots (account_id, snapshot_date) TYPE minmax GRANULARITY 1;

-- Performance optimization settings
ALTER TABLE market_data_ts MODIFY SETTING index_granularity = 8192;
ALTER TABLE trade_analytics MODIFY SETTING index_granularity = 8192;
