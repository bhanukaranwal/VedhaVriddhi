from pydantic import BaseSettings
from typing import Dict, List, Optional

class Settings(BaseSettings):
    # Service Configuration
    service_name: str = "quantum-service"
    service_version: str = "4.0.0"
    service_port: int = 8200
    debug: bool = False
    
    # Quantum Provider Configuration
    ibm_quantum_enabled: bool = True
    ibm_quantum_token: str = ""
    ibm_quantum_hub: str = "ibm-q"
    ibm_quantum_group: str = "open"
    ibm_quantum_project: str = "main"
    
    google_quantum_enabled: bool = True
    google_quantum_project_id: str = ""
    google_quantum_processor: str = "rainbow"
    google_quantum_credentials_path: str = ""
    
    rigetti_quantum_enabled: bool = False
    rigetti_quantum_endpoint: str = ""
    rigetti_quantum_user_id: str = ""
    
    # Database Configuration
    quantum_db_url: str = "postgresql://vedhavriddhi:vedhavriddhi123@localhost:5432/vedhavriddhi_quantum"
    redis_url: str = "redis://localhost:6379/11"
    
    # Job Scheduler Configuration
    max_concurrent_jobs_per_processor: int = 5
    job_timeout_seconds: int = 300
    max_queue_size: int = 1000
    scheduling_interval_seconds: float = 1.0
    
    # Algorithm Configuration
    default_qaoa_depth: int = 1
    default_vqe_ansatz: str = "hardware_efficient"
    default_shots: int = 1024
    max_shots: int = 8192
    
    # Performance Configuration
    quantum_advantage_threshold: float = 2.0  # Minimum speedup to claim quantum advantage
    error_mitigation_enabled: bool = True
    circuit_optimization_enabled: bool = True
    
    # Resource Management
    qubit_requirement_buffer: float = 0.1  # 10% buffer for qubit requirements
    memory_limit_gb: float = 16.0
    cpu_cores: int = 8
    gpu_enabled: bool = True
    
    # Monitoring Configuration
    metrics_collection_enabled: bool = True
    performance_logging_enabled: bool = True
    quantum_volume_benchmarking_enabled: bool = True
    
    # Security Configuration
    api_key_required: bool = True
    rate_limit_requests_per_minute: int = 100
    max_request_size_mb: int = 10
    
    # External Services
    portfolio_service_url: str = "http://localhost:8002"
    market_data_url: str = "http://localhost:8001"
    risk_service_url: str = "http://localhost:8004"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
