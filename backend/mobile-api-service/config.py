from pydantic import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Service Configuration
    service_name: str = "mobile-api-service"
    service_version: str = "3.0.0"
    service_port: int = 8105
    debug: bool = False
    
    # Database Configuration
    mobile_db_url: str = "postgresql://vedhavriddhi:vedhavriddhi123@localhost:5432/vedhavriddhi_mobile"
    redis_url: str = "redis://localhost:6379/8"
    
    # Authentication Configuration
    jwt_secret_key: str = "your-secret-jwt-key-here"
    jwt_algorithm: str = "HS256"
    jwt_token_expiry_hours: int = 24
    refresh_token_expiry_days: int = 30
    
    # Mobile-specific Configuration
    max_positions_per_request: int = 100
    max_watchlist_items: int = 50
    push_notification_enabled: bool = True
    
    # Rate Limiting
    rate_limit_requests_per_minute: int = 120
    rate_limit_burst_size: int = 200
    
    # Push Notifications
    fcm_server_key: str = ""  # Firebase Cloud Messaging
    apns_certificate_path: str = ""  # Apple Push Notification Service
    
    # Data Refresh Intervals
    portfolio_refresh_seconds: int = 30
    market_data_refresh_seconds: int = 5
    news_refresh_minutes: int = 15
    
    # External Services
    portfolio_service_url: str = "http://localhost:8002"
    market_data_url: str = "http://localhost:8001"
    trading_engine_url: str = "http://localhost:8080"
    news_service_url: str = "http://localhost:8007"
    
    # Supported Mobile Platforms
    supported_platforms: List[str] = ["ios", "android", "flutter"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False
