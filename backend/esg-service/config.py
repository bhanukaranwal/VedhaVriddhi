from pydantic import BaseSettings
from typing import List, Dict

class Settings(BaseSettings):
    # Service Configuration
    service_name: str = "esg-service"
    service_version: str = "3.0.0"
    service_port: int = 8106
    debug: bool = False
    
    # Database Configuration
    esg_db_url: str = "postgresql://vedhavriddhi:vedhavriddhi123@localhost:5432/vedhavriddhi_esg"
    redis_url: str = "redis://localhost:6379/9"
    
    # ESG Data Providers
    msci_api_endpoint: str = "https://api.msci.com/v1"
    msci_api_key: str = ""
    sustainalytics_api_endpoint: str = "https://api.sustainalytics.com/v1"
    sustainalytics_api_key: str = ""
    refinitiv_api_endpoint: str = "https://api.refinitiv.com/esg/v1"
    refinitiv_api_key: str = ""
    bloomberg_api_endpoint: str = "https://api.bloomberg.com/esg/v1"
    bloomberg_api_key: str = ""
    
    # Scoring Configuration
    score_update_interval_hours: int = 6
    cache_ttl_seconds: int = 3600  # 1 hour
    min_data_coverage_threshold: float = 0.7  # 70%
    
    # ESG Scoring Weights
    environmental_weight: float = 0.4
    social_weight: float = 0.3
    governance_weight: float = 0.3
    
    # Provider Weights
    provider_weights: Dict[str, float] = {
        "msci": 0.4,
        "sustainalytics": 0.3,
        "refinitiv": 0.2,
        "bloomberg": 0.1
    }
    
    # Green Bond Criteria
    green_bond_frameworks: List[str] = [
        "Climate Bonds Standard",
        "Green Bond Principles",
        "EU Green Bond Standard",
        "ASEAN Green Bond Standards"
    ]
    
    # Risk Assessment Thresholds
    high_risk_threshold: float = 75.0
    medium_risk_threshold: float = 50.0
    
    # ML Model Configuration
    model_retrain_frequency_days: int = 30
    model_confidence_threshold: float = 0.75
    
    # External Services
    portfolio_service_url: str = "http://localhost:8002"
    market_data_url: str = "http://localhost:8001"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
