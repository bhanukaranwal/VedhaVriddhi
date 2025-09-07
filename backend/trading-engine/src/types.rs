use chrono::{DateTime, Utc};
use rust_decimal::Decimal;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum OrderSide {
    Buy,
    Sell,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum OrderType {
    Market,
    Limit,
    Stop,
    StopLimit,
    IcebergLimit { display_quantity: Decimal },
    FillOrKill,
    ImmediateOrCancel,
    GoodTillDate { expiry: DateTime<Utc> },
    PostOnly,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum OrderStatus {
    Pending,
    PartiallyFilled,
    Filled,
    Cancelled,
    Rejected,
    Expired,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Order {
    pub id: Uuid,
    pub client_order_id: String,
    pub symbol: String,
    pub side: OrderSide,
    pub order_type: OrderType,
    pub quantity: Decimal,
    pub price: Option<Decimal>,
    pub filled_quantity: Decimal,
    pub remaining_quantity: Decimal,
    pub status: OrderStatus,
    pub timestamp: DateTime<Utc>,
    pub user_id: Uuid,
    pub account_id: Uuid,
    pub time_in_force: TimeInForce,
    pub metadata: HashMap<String, String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum TimeInForce {
    GoodTillCancel,
    ImmediateOrCancel,
    FillOrKill,
    GoodTillDate(DateTime<Utc>),
    GoodForDay,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Trade {
    pub id: Uuid,
    pub symbol: String,
    pub buyer_order_id: Uuid,
    pub seller_order_id: Uuid,
    pub quantity: Decimal,
    pub price: Decimal,
    pub timestamp: DateTime<Utc>,
    pub trade_type: TradeType,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum TradeType {
    Regular,
    Block,
    Repo,
    ReverseRepo,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Position {
    pub symbol: String,
    pub account_id: Uuid,
    pub quantity: Decimal,
    pub average_price: Decimal,
    pub market_value: Decimal,
    pub unrealized_pnl: Decimal,
    pub realized_pnl: Decimal,
    pub last_updated: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OrderBook {
    pub symbol: String,
    pub bids: Vec<PriceLevel>,
    pub asks: Vec<PriceLevel>,
    pub last_update: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PriceLevel {
    pub price: Decimal,
    pub quantity: Decimal,
    pub order_count: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Bond {
    pub isin: String,
    pub symbol: String,
    pub issuer: String,
    pub maturity_date: DateTime<Utc>,
    pub coupon_rate: Decimal,
    pub face_value: Decimal,
    pub bond_type: BondType,
    pub rating: Option<String>,
    pub is_active: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum BondType {
    GovernmentSecurity,
    TreasuryBill,
    CorporateBond,
    StateGovernmentBond,
    MunicipalBond,
    CertificateOfDeposit,
    CommercialPaper,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MarketData {
    pub symbol: String,
    pub bid_price: Option<Decimal>,
    pub ask_price: Option<Decimal>,
    pub last_price: Option<Decimal>,
    pub volume: Decimal,
    pub timestamp: DateTime<Utc>,
    pub yield_to_maturity: Option<Decimal>,
    pub duration: Option<Decimal>,
    pub accrued_interest: Option<Decimal>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RiskLimits {
    pub account_id: Uuid,
    pub max_position_size: Decimal,
    pub max_order_value: Decimal,
    pub max_daily_loss: Decimal,
    pub concentration_limit: Decimal,
    pub var_limit: Decimal,
}

#[derive(Debug, thiserror::Error)]
pub enum TradingError {
    #[error("Order not found: {0}")]
    OrderNotFound(String),
    #[error("Insufficient balance: required {required}, available {available}")]
    InsufficientBalance { required: Decimal, available: Decimal },
    #[error("Risk limit exceeded: {0}")]
    RiskLimitExceeded(String),
    #[error("Invalid order: {0}")]
    InvalidOrder(String),
    #[error("Market closed")]
    MarketClosed,
    #[error("Database error: {0}")]
    DatabaseError(#[from] sqlx::Error),
    #[error("Redis error: {0}")]
    RedisError(#[from] redis::RedisError),
    #[error("Internal error: {0}")]
    InternalError(String),
}

pub type Result<T> = std::result::Result<T, TradingError>;
