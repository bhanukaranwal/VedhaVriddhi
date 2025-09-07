use anyhow::Result;
use axum::{extract::State, http::Method, routing::get, Router};
use std::{net::SocketAddr, sync::Arc};
use tokio::signal;
use tower_http::{cors::CorsLayer, trace::TraceLayer};
use tracing::{info, warn};

mod config;
mod engine;
mod network;
mod types;
mod utils;

use config::Config;
use engine::TradingEngine;
use network::handlers;

#[derive(Clone)]
pub struct AppState {
    pub engine: Arc<TradingEngine>,
    pub config: Arc<Config>,
}

#[tokio::main]
async fn main() -> Result<()> {
    tracing_subscriber::fmt::init();

    let config = Arc::new(Config::from_env()?);
    let engine = Arc::new(TradingEngine::new(config.clone()).await?);
    
    let state = AppState { engine, config };

    let cors = CorsLayer::new()
        .allow_methods([Method::GET, Method::POST, Method::PUT, Method::DELETE])
        .allow_origin(tower_http::cors::Any)
        .allow_headers(tower_http::cors::Any);

    let app = Router::new()
        .route("/health", get(handlers::health_check))
        .route("/orders", get(handlers::get_orders).post(handlers::submit_order))
        .route("/orders/:id", get(handlers::get_order).delete(handlers::cancel_order))
        .route("/trades", get(handlers::get_trades))
        .route("/orderbook/:symbol", get(handlers::get_orderbook))
        .route("/positions", get(handlers::get_positions))
        .route("/ws", get(handlers::websocket_handler))
        .with_state(state)
        .layer(TraceLayer::new_for_http())
        .layer(cors);

    let addr = SocketAddr::from(([0, 0, 0, 0], 8080));
    info!("VedhaVriddhi Trading Engine starting on {}", addr);

    let listener = tokio::net::TcpListener::bind(addr).await?;
    
    axum::serve(listener, app)
        .with_graceful_shutdown(shutdown_signal())
        .await?;

    Ok(())
}

async fn shutdown_signal() {
    let ctrl_c = async {
        signal::ctrl_c()
            .await
            .expect("Failed to install Ctrl+C handler");
    };

    #[cfg(unix)]
    let terminate = async {
        signal::unix::signal(signal::unix::SignalKind::terminate())
            .expect("Failed to install signal handler")
            .recv()
            .await;
    };

    #[cfg(not(unix))]
    let terminate = std::future::pending::<()>();

    tokio::select! {
        _ = ctrl_c => {
            warn!("Received Ctrl+C, shutting down");
        },
        _ = terminate => {
            warn!("Received terminate signal, shutting down");
        },
    }
}
