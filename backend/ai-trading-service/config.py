from pydantic import BaseSettings
from typing import List, Dict

class Settings(BaseSettings):
    # Service Configuration
    service_name: str = "ai-trading-service"
    service_version: str = "3.0.0"
    service_port: int = 8102
    debug: bool = False
    
    # Database Configuration
    ai_trading_db_url: str = "postgresql://vedhavriddhi:vedhavriddhi123@localhost:5432/vedhavriddhi_ai"
    redis_url: str = "redis://localhost:6379/7"
    
    # ML Model Configuration
    model_storage_path: str = "/app/models"
    model_cache_size: int = 100  # MB
    max_prediction_cache_age: int = 60  # seconds
    
    # Agent Configuration
    max_concurrent_agents: int = 10
    agent_performance_window_days: int = 30
    min_agent_confidence_threshold: float = 0.6
    
    # Signal Processing
    signal_queue_size: int = 1000
    signal_processing_timeout: int = 30  # seconds
    max_signal_age_minutes: int = 60
    
    # Risk Management
    max_position_size_multiplier: float = 3.0
    min_position_size_multiplier: float = 0.1
    global_risk_limit_usd: float = 10000000.0  # 10M USD
    
    # Strategy Configuration
    momentum_lookback_period: int = 20
    momentum_threshold: float = 0.02
    arbitrage_min_spread: float = 0.001
    arbitrage_max_execution_time: int = 30
    
    # ML Model Settings
    prediction_confidence_threshold: float = 0.7
    model_retrain_frequency_hours: int = 6
    feature_importance_threshold: float = 0.05
    
    # Performance Monitoring
    performance_calculation_interval: int = 300  # 5 minutes
    performance_history_days: int = 90
    benchmark_symbol: str = "SPY"  # Default benchmark
    
    # External Services
    global_market_service_url: str = "http://localhost:8100"
    fx_service_url: str = "http://localhost:8101"
    risk_service_url: str = "http://localhost:8004"
    market_data_url: str = "http://localhost:8001"
    
    # Data Providers
    news_data_providers: List[str] = ["bloomberg", "reuters", "ft"]
    social_sentiment_providers: List[str] = ["twitter", "reddit", "stocktwits"]
    alternative_data_providers: List[str] = ["satellite", "credit_card", "web_scraping"]
    
    # Strategy Types and Weights
    strategy_weights: Dict[str, float] = {
        "momentum": 0.3,
        "mean_reversion": 0.2,
        "arbitrage": 0.2,
        "sentiment": 0.15,
        "ml_prediction": 0.15
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = False
