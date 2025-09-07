import os
from typing import Optional
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Database Configuration
    database_url: str = "postgresql://vedhavriddhi:vedhavriddhi123@localhost:5432/vedhavriddhi"
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: Optional[str] = None
    
    # Service URLs
    trading_engine_url: str = "http://localhost:8080"
    market_data_url: str = "http://localhost:8001"
    analytics_url: str = "http://localhost:8003"
    
    # JWT Configuration
    jwt_secret: str = "your-super-secret-jwt-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 480  # 8 hours
    refresh_token_expire_days: int = 7
    
    # CORS Configuration
    cors_origins: list = ["http://localhost:3000", "http://localhost:3001"]
    cors_credentials: bool = True
    cors_methods: list = ["*"]
    cors_headers: list = ["*"]
    
    # Rate Limiting
    rate_limit_per_minute: int = 1000
    rate_limit_per_hour: int = 10000
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # WebSocket Configuration
    websocket_max_connections: int = 1000
    websocket_heartbeat_interval: int = 30
    
    # Security
    bcrypt_rounds: int = 12
    session_timeout_minutes: int = 480
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15
    
    # External APIs
    nse_api_key: Optional[str] = None
    bse_api_key: Optional[str] = None
    bloomberg_api_key: Optional[str] = None
    reuters_api_key: Optional[str] = None
    
    # Performance
    max_order_history_days: int = 90
    max_trade_history_days: int = 30
    cache_ttl_seconds: int = 300
    
    class Config:
        env_file = ".env"
        case_sensitive = False
