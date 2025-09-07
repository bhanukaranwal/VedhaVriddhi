use crate::{
    config::Config,
    types::*,
    utils::{metrics::Metrics, time::TimeProvider},
};
use anyhow::Result;
use chrono::Utc;
use dashmap::DashMap;
use parking_lot::RwLock;
use rust_decimal::Decimal;
use std::{collections::VecDeque, sync::Arc};
use tokio::sync::{broadcast, mpsc};
use tracing::{error, info, warn};
use uuid::Uuid;

pub mod matching;
pub mod order_book;
pub mod position_manager;
pub mod risk_manager;

use matching::MatchingEngine;
use order_book::OrderBookManager;
use position_manager::PositionManager;
use risk_manager::RiskManager;

#[derive(Debug, Clone)]
pub enum EngineEvent {
    OrderSubmitted(Order),
    OrderCancelled(Uuid),
    OrderFilled { order_id: Uuid, trade: Trade },
    TradeExecuted(Trade),
    PositionUpdated(Position),
    RiskViolation { account_id: Uuid, violation: String },
}

pub struct TradingEngine {
    config: Arc<Config>,
    matching_engine: Arc<MatchingEngine>,
    order_book_manager: Arc<OrderBookManager>,
    position_manager: Arc<PositionManager>,
    risk_manager: Arc<RiskManager>,
    orders: Arc<DashMap<Uuid, Order>>,
    trades: Arc<RwLock<VecDeque<Trade>>>,
    event_sender: broadcast::Sender<EngineEvent>,
    metrics: Arc<Metrics>,
    time_provider: Arc<TimeProvider>,
}

impl TradingEngine {
    pub async fn new(config: Arc<Config>) -> Result<Self> {
        let metrics = Arc::new(Metrics::new());
        let time_provider = Arc::new(TimeProvider::new());
        let (event_sender, _) = broadcast::channel(10000);

        let matching_engine = Arc::new(MatchingEngine::new(
            config.clone(),
            event_sender.clone(),
            metrics.clone(),
        ));

        let order_book_manager = Arc::new(OrderBookManager::new(config.clone()));
        let position_manager = Arc::new(PositionManager::new(config.clone()).await?);
        let risk_manager = Arc::new(RiskManager::new(config.clone()).await?);

        let orders = Arc::new(DashMap::new());
        let trades = Arc::new(RwLock::new(VecDeque::with_capacity(100000)));

        Ok(Self {
            config,
            matching_engine,
            order_book_manager,
            position_manager,
            risk_manager,
            orders,
            trades,
            event_sender,
            metrics,
            time_provider,
        })
    }

    pub async fn submit_order(&self, mut order: Order) -> crate::types::Result<Uuid> {
        info!("Submitting order: {}", order.id);
        
        // Validate order
        self.validate_order(&order).await?;
        
        // Risk checks
        self.risk_manager.check_order(&order).await?;
        
        // Set timestamp
        order.timestamp = self.time_provider.now();
        order.remaining_quantity = order.quantity;
        
        // Store order
        self.orders.insert(order.id, order.clone());
        
        // Send to matching engine
        let trades = self.matching_engine.process_order(order.clone()).await?;
        
        // Update positions
        for trade in &trades {
            self.position_manager.update_position(trade).await?;
        }
        
        // Store trades
        {
            let mut trades_lock = self.trades.write();
            for trade in trades {
                trades_lock.push_back(trade.clone());
                if trades_lock.len() > 100000 {
                    trades_lock.pop_front();
                }
            }
        }
        
        // Send event
        let _ = self.event_sender.send(EngineEvent::OrderSubmitted(order.clone()));
        
        self.metrics.increment_orders_submitted();
        
        Ok(order.id)
    }

    pub async fn cancel_order(&self, order_id: Uuid) -> crate::types::Result<bool> {
        info!("Cancelling order: {}", order_id);
        
        if let Some((_, mut order)) = self.orders.remove(&order_id) {
            order.status = OrderStatus::Cancelled;
            self.orders.insert(order_id, order.clone());
            
            self.matching_engine.cancel_order(order_id).await?;
            
            let _ = self.event_sender.send(EngineEvent::OrderCancelled(order_id));
            
            self.metrics.increment_orders_cancelled();
            
            Ok(true)
        } else {
            Err(TradingError::OrderNotFound(order_id.to_string()))
        }
    }

    pub fn get_order(&self, order_id: &Uuid) -> Option<Order> {
        self.orders.get(order_id).map(|o| o.clone())
    }

    pub fn get_orders(&self) -> Vec<Order> {
        self.orders.iter().map(|entry| entry.value().clone()).collect()
    }

    pub fn get_trades(&self) -> Vec<Trade> {
        self.trades.read().iter().cloned().collect()
    }

    pub fn get_orderbook(&self, symbol: &str) -> Option<OrderBook> {
        self.order_book_manager.get_orderbook(symbol)
    }

    pub async fn get_positions(&self, account_id: Option<Uuid>) -> Vec<Position> {
        self.position_manager.get_positions(account_id).await
    }

    pub fn subscribe_events(&self) -> broadcast::Receiver<EngineEvent> {
        self.event_sender.subscribe()
    }

    async fn validate_order(&self, order: &Order) -> crate::types::Result<()> {
        if order.quantity <= Decimal::ZERO {
            return Err(TradingError::InvalidOrder("Quantity must be positive".to_string()));
        }

        if let Some(price) = order.price {
            if price <= Decimal::ZERO {
                return Err(TradingError::InvalidOrder("Price must be positive".to_string()));
            }
        }

        if order.symbol.is_empty() {
            return Err(TradingError::InvalidOrder("Symbol cannot be empty".to_string()));
        }

        // Additional validation logic
        match &order.order_type {
            OrderType::Limit => {
                if order.price.is_none() {
                    return Err(TradingError::InvalidOrder("Limit orders must have a price".to_string()));
                }
            }
            OrderType::Market => {
                if order.price.is_some() {
                    return Err(TradingError::InvalidOrder("Market orders cannot have a price".to_string()));
                }
            }
            _ => {}
        }

        Ok(())
    }

    pub fn get_metrics(&self) -> &Metrics {
        &self.metrics
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::config::Config;
    use rust_decimal_macros::dec;

    #[tokio::test]
    async fn test_submit_order() {
        let config = Arc::new(Config::default());
        let engine = TradingEngine::new(config).await.unwrap();

        let order = Order {
            id: Uuid::new_v4(),
            client_order_id: "TEST001".to_string(),
            symbol: "GSEC10Y".to_string(),
            side: OrderSide::Buy,
            order_type: OrderType::Limit,
            quantity: dec!(1000000),
            price: Some(dec!(98.50)),
            filled_quantity: Decimal::ZERO,
            remaining_quantity: Decimal::ZERO,
            status: OrderStatus::Pending,
            timestamp: Utc::now(),
            user_id: Uuid::new_v4(),
            account_id: Uuid::new_v4(),
            time_in_force: TimeInForce::GoodTillCancel,
            metadata: HashMap::new(),
        };

        let result = engine.submit_order(order.clone()).await;
        assert!(result.is_ok());
        assert_eq!(result.unwrap(), order.id);
    }
}
