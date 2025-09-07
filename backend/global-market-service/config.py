from pydantic import BaseSettings
from typing import List, Dict

class Settings(BaseSettings):
    # Service Configuration
    service_name: str = "global-market-service"
    service_version: str = "3.0.0"
    service_port: int = 8100
    debug: bool = False
    
    # Database Configuration
    global_trading_db_url: str = "postgresql://vedhavriddhi:vedhavriddhi123@localhost:5432/vedhavriddhi_global"
    redis_url: str = "redis://localhost:6379/5"
    
    # Market Data Configuration
    bloomberg_api_key: str = ""
    refinitiv_api_key: str = ""
    ice_api_key: str = ""
    tradeweb_api_key: str = ""
    
    # FX Configuration
    fx_rate_refresh_interval: int = 5  # seconds
    fx_rate_tolerance: float = 0.001  # 0.1%
    
    # Order Routing Configuration
    max_order_size_usd: float = 100000000.0  # 100M USD
    min_order_size_usd: float = 1000.0  # 1K USD
    
    # Session Configuration
    session_overlap_minutes: int = 60
    market_open_buffer_minutes: int = 15
    
    # Supported Markets
    supported_markets: List[str] = [
        "NYSE_BONDS",
        "LSE_BONDS", 
        "XETRA_BONDS",
        "TSE_BONDS",
        "SGX_BONDS"
    ]
    
    # Currency Pairs
    major_currency_pairs: List[str] = [
        "USD/EUR",
        "USD/GBP", 
        "USD/JPY",
        "USD/SGD",
        "USD/HKD",
        "USD/INR"
    ]
    
    # Risk Limits
    single_order_limit_usd: float = 10000000.0  # 10M USD
    daily_volume_limit_usd: float = 1000000000.0  # 1B USD
    
    # External Services
    fx_service_url: str = "http://localhost:8101"
    risk_service_url: str = "http://localhost:8004"
    compliance_service_url: str = "http://localhost:8005"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
