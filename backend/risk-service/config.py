import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Service Configuration
    service_name: str = "risk-service"
    service_version: str = "2.0.0"
    service_port: int = 8004
    debug: bool = False
    
    # Database Configuration
    risk_db_url: str = "postgresql://vedhavriddhi:vedhavriddhi123@localhost:5432/vedhavriddhi_risk"
    timeseries_db_url: str = "influxdb://localhost:8086"
    timeseries_db_name: str = "vedhavriddhi_timeseries"
    redis_url: str = "redis://localhost:6379/3"
    
    # Risk Limits Configuration
    max_var_95_institutional: float = 10000000.0  # 10M INR
    max_var_95_retail: float = 1000000.0  # 1M INR
    max_var_99_institutional: float = 20000000.0  # 20M INR
    max_var_99_retail: float = 2000000.0  # 2M INR
    
    # Concentration Limits
    max_single_issuer_pct: float = 15.0  # 15%
    max_single_sector_pct: float = 25.0  # 25%
    max_single_rating_pct: float = 40.0  # 40%
    max_single_maturity_bucket_pct: float = 30.0  # 30%
    
    # Exposure Limits
    max_total_exposure: float = 500000000.0  # 500M INR
    max_leverage_ratio: float = 3.0
    max_duration_limit: float = 15.0  # years
    
    # Liquidity Limits
    min_liquidity_ratio: float = 0.20  # 20%
    max_illiquid_exposure_pct: float = 50.0  # 50%
    
    # Risk Calculation Settings
    var_confidence_levels: list = [0.95, 0.99]
    var_lookback_days: int = 252  # 1 year
    stress_test_scenarios: list = [
        "interest_rate_shock",
        "credit_spread_widening", 
        "liquidity_crisis",
        "inflation_shock",
        "default_cluster"
    ]
    
    # Performance Settings
    max_workers: int = 4
    calculation_timeout: int = 30
    cache_ttl: int = 300  # 5 minutes
    
    # External Services
    analytics_service_url: str = "http://localhost:8003"
    trading_engine_url: str = "http://localhost:8080"
    market_data_url: str = "http://localhost:8001"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
