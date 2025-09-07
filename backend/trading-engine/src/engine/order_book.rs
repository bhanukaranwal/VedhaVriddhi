use crate::types::*;
use dashmap::DashMap;
use parking_lot::RwLock;
use rust_decimal::Decimal;
use std::collections::BTreeMap;
use std::sync::Arc;
use uuid::Uuid;

pub struct OrderBookManager {
    order_books: Arc<DashMap<String, Arc<RwLock<OrderBook>>>>,
}

impl OrderBookManager {
    pub fn new(config: Arc<crate::config::Config>) -> Self {
        Self {
            order_books: Arc::new(DashMap::new()),
        }
    }

    pub fn get_orderbook(&self, symbol: &str) -> Option<OrderBook> {
        self.order_books
            .get(symbol)
            .map(|book| book.read().clone())
    }

    pub fn update_orderbook(&self, symbol: String, bids: Vec<PriceLevel>, asks: Vec<PriceLevel>) {
        let order_book = OrderBook {
            symbol: symbol.clone(),
            bids,
            asks,
            last_update: chrono::Utc::now(),
        };

        match self.order_books.get(&symbol) {
            Some(existing) => {
                *existing.write() = order_book;
            }
            None => {
                self.order_books.insert(symbol, Arc::new(RwLock::new(order_book)));
            }
        }
    }

    pub fn get_best_bid(&self, symbol: &str) -> Option<Decimal> {
        self.order_books
            .get(symbol)?
            .read()
            .bids
            .first()
            .map(|level| level.price)
    }

    pub fn get_best_ask(&self, symbol: &str) -> Option<Decimal> {
        self.order_books
            .get(symbol)?
            .read()
            .asks
            .first()
            .map(|level| level.price)
    }

    pub fn get_spread(&self, symbol: &str) -> Option<Decimal> {
        let book = self.order_books.get(symbol)?.read();
        let best_bid = book.bids.first()?.price;
        let best_ask = book.asks.first()?.price;
        Some(best_ask - best_bid)
    }

    pub fn get_market_depth(&self, symbol: &str, levels: usize) -> Option<(Vec<PriceLevel>, Vec<PriceLevel>)> {
        let book = self.order_books.get(symbol)?.read();
        let bids = book.bids.iter().take(levels).cloned().collect();
        let asks = book.asks.iter().take(levels).cloned().collect();
        Some((bids, asks))
    }
}
