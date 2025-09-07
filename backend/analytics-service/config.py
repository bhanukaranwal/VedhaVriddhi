import os
from typing import Optional
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Service Configuration
    service_name: str = "analytics-service"
    service_version: str = "2.0.0"
    debug: bool = False
    
    # Database Configuration
    timeseries_db_url: str = "influxdb://localhost:8086"
    timeseries_db_name: str = "vedhavriddhi_timeseries"
    timeseries_db_username: str = "vedhavriddhi"
    timeseries_db_password: str = "vedhavriddhi123"
    
    analytics_db_url: str = "postgresql://vedhavriddhi:vedhavriddhi123@localhost:5432/vedhavriddhi_analytics"
    clickhouse_url: str = "http://localhost:8123"
    clickhouse_database: str = "vedhavriddhi_analytics"
    
    redis_url: str = "redis://localhost:6379/2"
    redis_password: Optional[str] = "vedhavriddhi123"
    
    # ML Configuration
    model_storage_path: str = "/app/models"
    training_data_retention_days: int = 365
    model_retrain_interval_hours: int = 24
    
    # Analytics Configuration
    yield_curve_update_interval: int = 300  # 5 minutes
    portfolio_analytics_cache_ttl: int = 300
    max_concurrent_calculations: int = 10
    
    # External Services
    trading_engine_url: str = "http://localhost:8080"
    market_data_url: str = "http://localhost:8001"
    risk_service_url: str = "http://localhost:8004"
    
    # Performance
    max_workers: int = 4
    request_timeout: int = 30
    max_memory_usage_mb: int = 2048
    
    class Config:
        env_file = ".env"
        case_sensitive = False
