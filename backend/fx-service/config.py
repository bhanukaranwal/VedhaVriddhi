from pydantic import BaseSettings
from typing import List, Dict

class Settings(BaseSettings):
    # Service Configuration
    service_name: str = "fx-service"
    service_version: str = "3.0.0"
    service_port: int = 8101
    debug: bool = False
    
    # Database Configuration
    fx_db_url: str = "postgresql://vedhavriddhi:vedhavriddhi123@localhost:5432/vedhavriddhi_fx"
    redis_url: str = "redis://localhost:6379/6"
    
    # FX Provider APIs
    bloomberg_api_url: str = "https://api.bloomberg.com/v1"
    bloomberg_api_key: str = ""
    refinitiv_api_url: str = "https://api.refinitiv.com/v1"
    refinitiv_api_key: str = ""
    oanda_api_url: str = "https://api-fxtrade.oanda.com/v3"
    oanda_api_key: str = ""
    
    # Rate Configuration
    rate_refresh_interval: int = 1  # seconds
    rate_cache_ttl: int = 5  # seconds
    max_rate_age: int = 30  # seconds
    
    # Spread Configuration
    max_spread_bps: int = 50  # 5 basis points
    min_liquidity_threshold: float = 100000.0  # 100K
    
    # Hedging Configuration
    default_hedge_ratio: float = 0.85  # 85%
    max_hedge_horizon_days: int = 365
    min_hedge_amount: float = 10000.0  # 10K
    
    # Risk Configuration
    var_confidence_level: float = 0.95
    fx_risk_limit_usd: float = 5000000.0  # 5M USD
    max_single_currency_exposure: float = 0.25  # 25%
    
    # Supported Currencies
    supported_currencies: List[str] = [
        "USD", "EUR", "GBP", "JPY", "SGD", "HKD", "INR", 
        "AUD", "CAD", "CHF", "CNY"
    ]
    
    # Major Currency Pairs
    major_pairs: List[str] = [
        "USD/EUR", "USD/GBP", "USD/JPY", "USD/SGD", 
        "USD/HKD", "USD/INR", "EUR/GBP", "EUR/JPY", "GBP/JPY"
    ]
    
    # Provider Weights
    provider_weights: Dict[str, float] = {
        "bloomberg": 0.4,
        "refinitiv": 0.3, 
        "ice": 0.2,
        "oanda": 0.1
    }
    
    # External Services
    global_market_service_url: str = "http://localhost:8100"
    risk_service_url: str = "http://localhost:8004"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
