import os
from pydantic import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Service Configuration
    service_name: str = "compliance-service"
    service_version: str = "2.0.0"
    service_port: int = 8005
    debug: bool = False
    
    # Database Configuration
    compliance_db_url: str = "postgresql://vedhavriddhi:vedhavriddhi123@localhost:5432/vedhavriddhi_compliance"
    redis_url: str = "redis://localhost:6379/4"
    
    # Compliance Configuration
    enable_real_time_monitoring: bool = True
    monitoring_interval_seconds: int = 60
    violation_alert_threshold: str = "warning"  # info, warning, violation, critical
    
    # Regulatory Bodies
    sebi_api_endpoint: str = "https://www.sebi.gov.in/api"
    rbi_api_endpoint: str = "https://www.rbi.org.in/api"
    fema_api_endpoint: str = ""
    
    # Rule Engine Settings
    max_concurrent_evaluations: int = 100
    rule_evaluation_timeout: int = 10  # seconds
    
    # Reporting Configuration
    auto_generate_reports: bool = True
    report_generation_schedule: str = "0 9 * * *"  # Daily at 9 AM
    report_retention_days: int = 2555  # 7 years
    
    # Alert Configuration
    alert_channels: List[str] = ["email", "sms", "webhook"]
    email_smtp_server: str = "smtp.gmail.com"
    email_smtp_port: int = 587
    webhook_url: str = ""
    
    # AML/KYC Configuration
    enable_aml_screening: bool = True
    kyc_verification_required: bool = True
    suspicious_transaction_threshold: float = 1000000.0  # 10L INR
    
    # External Services
    trading_engine_url: str = "http://localhost:8080"
    analytics_service_url: str = "http://localhost:8003"
    risk_service_url: str = "http://localhost:8004"
    
    # Performance Settings
    max_workers: int = 4
    request_timeout: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False
