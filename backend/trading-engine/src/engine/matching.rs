use crate::{
    engine::EngineEvent,
    types::*,
    config::Config,
    utils::metrics::Metrics,
};
use anyhow::Result;
use chrono::Utc;
use dashmap::DashMap;
use parking_lot::RwLock;
use rust_decimal::Decimal;
use std::{
    collections::{BTreeMap, VecDeque},
    sync::Arc,
};
use tokio::sync::broadcast;
use tracing::{debug, info};
use uuid::Uuid;

#[derive(Debug, Clone)]
struct OrderBookEntry {
    order: Order,
    priority: u64,
}

impl OrderBookEntry {
    fn new(order: Order, priority: u64) -> Self {
        Self { order, priority }
    }
}

pub struct MatchingEngine {
    config: Arc<Config>,
    buy_orders: Arc<RwLock<BTreeMap<String, BTreeMap<Decimal, VecDeque<OrderBookEntry>>>>>,
    sell_orders: Arc<RwLock<BTreeMap<String, BTreeMap<Decimal, VecDeque<OrderBookEntry>>>>>,
    order_index: Arc<DashMap<Uuid, (String, Decimal, OrderSide)>>,
    event_sender: broadcast::Sender<EngineEvent>,
    metrics: Arc<Metrics>,
    next_priority: Arc<parking_lot::Mutex<u64>>,
}

impl MatchingEngine {
    pub fn new(
        config: Arc<Config>,
        event_sender: broadcast::Sender<EngineEvent>,
        metrics: Arc<Metrics>,
    ) -> Self {
        Self {
            config,
            buy_orders: Arc::new(RwLock::new(BTreeMap::new())),
            sell_orders: Arc::new(RwLock::new(BTreeMap::new())),
            order_index: Arc::new(DashMap::new()),
            event_sender,
            metrics,
            next_priority: Arc::new(parking_lot::Mutex::new(0)),
        }
    }

    pub async fn process_order(&self, order: Order) -> crate::types::Result<Vec<Trade>> {
        let mut trades = Vec::new();
        let mut remaining_order = order.clone();

        // Try to match against existing orders
        let matched_trades = self.match_order(&mut remaining_order).await?;
        trades.extend(matched_trades);

        // If there's remaining quantity, add to order book
        if remaining_order.remaining_quantity > Decimal::ZERO {
            self.add_to_order_book(remaining_order).await?;
        }

        Ok(trades)
    }

    async fn match_order(&self, order: &mut Order) -> crate::types::Result<Vec<Trade>> {
        let mut trades = Vec::new();

        match order.side {
            OrderSide::Buy => {
                trades.extend(self.match_buy_order(order).await?);
            }
            OrderSide::Sell => {
                trades.extend(self.match_sell_order(order).await?);
            }
        }

        Ok(trades)
    }

    async fn match_buy_order(&self, buy_order: &mut Order) -> crate::types::Result<Vec<Trade>> {
        let mut trades = Vec::new();
        let mut sell_orders = self.sell_orders.write();
        
        if let Some(symbol_orders) = sell_orders.get_mut(&buy_order.symbol) {
            let mut prices_to_remove = Vec::new();
            
            for (&price, price_level) in symbol_orders.iter_mut() {
                // For buy orders, match against sell orders at or below the buy price
                if let Some(buy_price) = buy_order.price {
                    if price > buy_price {
                        break; // Sell price too high
                    }
                } // Market orders match at any price

                while let Some(mut sell_entry) = price_level.pop_front() {
                    if buy_order.remaining_quantity <= Decimal::ZERO {
                        price_level.push_front(sell_entry);
                        break;
                    }

                    let trade_quantity = buy_order.remaining_quantity.min(sell_entry.order.remaining_quantity);
                    let trade_price = price; // Price improvement for buy order

                    // Create trade
                    let trade = Trade {
                        id: Uuid::new_v4(),
                        symbol: buy_order.symbol.clone(),
                        buyer_order_id: buy_order.id,
                        seller_order_id: sell_entry.order.id,
                        quantity: trade_quantity,
                        price: trade_price,
                        timestamp: Utc::now(),
                        trade_type: TradeType::Regular,
                    };

                    // Update order quantities
                    buy_order.remaining_quantity -= trade_quantity;
                    buy_order.filled_quantity += trade_quantity;
                    sell_entry.order.remaining_quantity -= trade_quantity;
                    sell_entry.order.filled_quantity += trade_quantity;

                    // Update order statuses
                    if buy_order.remaining_quantity <= Decimal::ZERO {
                        buy_order.status = OrderStatus::Filled;
                    } else {
                        buy_order.status = OrderStatus::PartiallyFilled;
                    }

                    if sell_entry.order.remaining_quantity <= Decimal::ZERO {
                        sell_entry.order.status = OrderStatus::Filled;
                        // Remove from index
                        self.order_index.remove(&sell_entry.order.id);
                    } else {
                        sell_entry.order.status = OrderStatus::PartiallyFilled;
                        price_level.push_front(sell_entry);
                    }

                    trades.push(trade.clone());
                    
                    // Send events
                    let _ = self.event_sender.send(EngineEvent::TradeExecuted(trade.clone()));
                    let _ = self.event_sender.send(EngineEvent::OrderFilled {
                        order_id: buy_order.id,
                        trade: trade.clone(),
                    });
                    let _ = self.event_sender.send(EngineEvent::OrderFilled {
                        order_id: sell_entry.order.id,
                        trade: trade.clone(),
                    });

                    self.metrics.increment_trades_executed();
                    
                    debug!("Trade executed: {} {} @ {} between orders {} and {}", 
                           trade_quantity, buy_order.symbol, trade_price, 
                           buy_order.id, sell_entry.order.id);
                }

                if price_level.is_empty() {
                    prices_to_remove.push(price);
                }

                if buy_order.remaining_quantity <= Decimal::ZERO {
                    break;
                }
            }

            // Clean up empty price levels
            for price in prices_to_remove {
                symbol_orders.remove(&price);
            }
        }

        Ok(trades)
    }

    async fn match_sell_order(&self, sell_order: &mut Order) -> crate::types::Result<Vec<Trade>> {
        let mut trades = Vec::new();
        let mut buy_orders = self.buy_orders.write();
        
        if let Some(symbol_orders) = buy_orders.get_mut(&sell_order.symbol) {
            let mut prices_to_remove = Vec::new();
            
            // Iterate through buy orders from highest to lowest price
            for (&price, price_level) in symbol_orders.iter_mut().rev() {
                // For sell orders, match against buy orders at or above the sell price
                if let Some(sell_price) = sell_order.price {
                    if price < sell_price {
                        break; // Buy price too low
                    }
                } // Market orders match at any price

                while let Some(mut buy_entry) = price_level.pop_front() {
                    if sell_order.remaining_quantity <= Decimal::ZERO {
                        price_level.push_front(buy_entry);
                        break;
                    }

                    let trade_quantity = sell_order.remaining_quantity.min(buy_entry.order.remaining_quantity);
                    let trade_price = price; // Price improvement for sell order

                    // Create trade
                    let trade = Trade {
                        id: Uuid::new_v4(),
                        symbol: sell_order.symbol.clone(),
                        buyer_order_id: buy_entry.order.id,
                        seller_order_id: sell_order.id,
                        quantity: trade_quantity,
                        price: trade_price,
                        timestamp: Utc::now(),
                        trade_type: TradeType::Regular,
                    };

                    // Update order quantities
                    sell_order.remaining_quantity -= trade_quantity;
                    sell_order.filled_quantity += trade_quantity;
                    buy_entry.order.remaining_quantity -= trade_quantity;
                    buy_entry.order.filled_quantity += trade_quantity;

                    // Update order statuses
                    if sell_order.remaining_quantity <= Decimal::ZERO {
                        sell_order.status = OrderStatus::Filled;
                    } else {
                        sell_order.status = OrderStatus::PartiallyFilled;
                    }

                    if buy_entry.order.remaining_quantity <= Decimal::ZERO {
                        buy_entry.order.status = OrderStatus::Filled;
                        // Remove from index
                        self.order_index.remove(&buy_entry.order.id);
                    } else {
                        buy_entry.order.status = OrderStatus::PartiallyFilled;
                        price_level.push_front(buy_entry);
                    }

                    trades.push(trade.clone());
                    
                    // Send events
                    let _ = self.event_sender.send(EngineEvent::TradeExecuted(trade.clone()));
                    let _ = self.event_sender.send(EngineEvent::OrderFilled {
                        order_id: sell_order.id,
                        trade: trade.clone(),
                    });
                    let _ = self.event_sender.send(EngineEvent::OrderFilled {
                        order_id: buy_entry.order.id,
                        trade: trade.clone(),
                    });

                    self.metrics.increment_trades_executed();
                    
                    debug!("Trade executed: {} {} @ {} between orders {} and {}", 
                           trade_quantity, sell_order.symbol, trade_price, 
                           buy_entry.order.id, sell_order.id);
                }

                if price_level.is_empty() {
                    prices_to_remove.push(price);
                }

                if sell_order.remaining_quantity <= Decimal::ZERO {
                    break;
                }
            }

            // Clean up empty price levels
            for price in prices_to_remove {
                symbol_orders.remove(&price);
            }
        }

        Ok(trades)
    }

    async fn add_to_order_book(&self, order: Order) -> crate::types::Result<()> {
        let priority = {
            let mut next_priority = self.next_priority.lock();
            *next_priority += 1;
            *next_priority
        };

        let entry = OrderBookEntry::new(order.clone(), priority);
        
        let price = order.price.ok_or_else(|| {
            TradingError::InvalidOrder("Cannot add market order to book".to_string())
        })?;

        match order.side {
            OrderSide::Buy => {
                let mut buy_orders = self.buy_orders.write();
                buy_orders
                    .entry(order.symbol.clone())
                    .or_insert_with(BTreeMap::new)
                    .entry(price)
                    .or_insert_with(VecDeque::new)
                    .push_back(entry);
            }
            OrderSide::Sell => {
                let mut sell_orders = self.sell_orders.write();
                sell_orders
                    .entry(order.symbol.clone())
                    .or_insert_with(BTreeMap::new)
                    .entry(price)
                    .or_insert_with(VecDeque::new)
                    .push_back(entry);
            }
        }

        // Update index
        self.order_index.insert(order.id, (order.symbol.clone(), price, order.side));
        
        info!("Order {} added to book: {} {} @ {}", 
              order.id, order.remaining_quantity, order.symbol, price);

        Ok(())
    }

    pub async fn cancel_order(&self, order_id: Uuid) -> crate::types::Result<bool> {
        if let Some((_, (symbol, price, side))) = self.order_index.remove(&order_id) {
            match side {
                OrderSide::Buy => {
                    let mut buy_orders = self.buy_orders.write();
                    if let Some(symbol_orders) = buy_orders.get_mut(&symbol) {
                        if let Some(price_level) = symbol_orders.get_mut(&price) {
                            price_level.retain(|entry| entry.order.id != order_id);
                            if price_level.is_empty() {
                                symbol_orders.remove(&price);
                            }
                        }
                    }
                }
                OrderSide::Sell => {
                    let mut sell_orders = self.sell_orders.write();
                    if let Some(symbol_orders) = sell_orders.get_mut(&symbol) {
                        if let Some(price_level) = symbol_orders.get_mut(&price) {
                            price_level.retain(|entry| entry.order.id != order_id);
                            if price_level.is_empty() {
                                symbol_orders.remove(&price);
                            }
                        }
                    }
                }
            }
            Ok(true)
        } else {
            Ok(false)
        }
    }

    pub fn get_best_bid(&self, symbol: &str) -> Option<Decimal> {
        let buy_orders = self.buy_orders.read();
        buy_orders
            .get(symbol)?
            .keys()
            .next_back()
            .copied()
    }

    pub fn get_best_ask(&self, symbol: &str) -> Option<Decimal> {
        let sell_orders = self.sell_orders.read();
        sell_orders
            .get(symbol)?
            .keys()
            .next()
            .copied()
    }
}
