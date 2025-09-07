use crate::types::*;
use anyhow::Result;
use chrono::Utc;
use dashmap::DashMap;
use rust_decimal::Decimal;
use std::sync::Arc;
use uuid::Uuid;

pub struct PositionManager {
    positions: Arc<DashMap<(Uuid, String), Position>>,
    config: Arc<crate::config::Config>,
}

impl PositionManager {
    pub async fn new(config: Arc<crate::config::Config>) -> Result<Self> {
        Ok(Self {
            positions: Arc::new(DashMap::new()),
            config,
        })
    }

    pub async fn update_position(&self, trade: &Trade) -> crate::types::Result<()> {
        let buyer_key = (trade.buyer_order_id, trade.symbol.clone());
        let seller_key = (trade.seller_order_id, trade.symbol.clone());

        // Update buyer position
        self.update_position_for_trade(buyer_key, trade, OrderSide::Buy).await?;
        
        // Update seller position
        self.update_position_for_trade(seller_key, trade, OrderSide::Sell).await?;

        Ok(())
    }

    async fn update_position_for_trade(
        &self,
        key: (Uuid, String),
        trade: &Trade,
        side: OrderSide,
    ) -> crate::types::Result<()> {
        let (account_id, symbol) = key;
        let quantity_change = match side {
            OrderSide::Buy => trade.quantity,
            OrderSide::Sell => -trade.quantity,
        };

        match self.positions.get_mut(&(account_id, symbol.clone())) {
            Some(mut position) => {
                let old_quantity = position.quantity;
                let new_quantity = old_quantity + quantity_change;
                
                // Calculate new average price
                if new_quantity != Decimal::ZERO {
                    let total_cost = (old_quantity * position.average_price) + 
                                   (quantity_change.abs() * trade.price);
                    position.average_price = total_cost / new_quantity.abs();
                }

                position.quantity = new_quantity;
                position.last_updated = Utc::now();
                
                // Update market value and P&L
                let current_price = self.get_current_price(&symbol).await.unwrap_or(trade.price);
                position.market_value = new_quantity * current_price;
                position.unrealized_pnl = (current_price - position.average_price) * new_quantity;
            }
            None => {
                // Create new position
                let position = Position {
                    symbol: symbol.clone(),
                    account_id,
                    quantity: quantity_change,
                    average_price: trade.price,
                    market_value: quantity_change * trade.price,
                    unrealized_pnl: Decimal::ZERO,
                    realized_pnl: Decimal::ZERO,
                    last_updated: Utc::now(),
                };
                self.positions.insert((account_id, symbol), position);
            }
        }

        Ok(())
    }

    pub async fn get_positions(&self, account_id: Option<Uuid>) -> Vec<Position> {
        match account_id {
            Some(id) => {
                self.positions
                    .iter()
                    .filter_map(|entry| {
                        let ((acc_id, _), position) = entry.pair();
                        if *acc_id == id {
                            Some(position.clone())
                        } else {
                            None
                        }
                    })
                    .collect()
            }
            None => self.positions.iter().map(|entry| entry.value().clone()).collect(),
        }
    }

    pub async fn get_position(&self, account_id: Uuid, symbol: &str) -> Option<Position> {
        self.positions
            .get(&(account_id, symbol.to_string()))
            .map(|pos| pos.clone())
    }

    pub async fn calculate_portfolio_value(&self, account_id: Uuid) -> Decimal {
        self.positions
            .iter()
            .filter_map(|entry| {
                let ((acc_id, _), position) = entry.pair();
                if *acc_id == account_id {
                    Some(position.market_value)
                } else {
                    None
                }
            })
            .sum()
    }

    pub async fn calculate_total_pnl(&self, account_id: Uuid) -> (Decimal, Decimal) {
        let mut unrealized = Decimal::ZERO;
        let mut realized = Decimal::ZERO;

        for entry in self.positions.iter() {
            let ((acc_id, _), position) = entry.pair();
            if *acc_id == account_id {
                unrealized += position.unrealized_pnl;
                realized += position.realized_pnl;
            }
        }

        (unrealized, realized)
    }

    async fn get_current_price(&self, _symbol: &str) -> Option<Decimal> {
        // This would typically fetch from market data service
        // For now, returning None to use trade price
        None
    }
}
