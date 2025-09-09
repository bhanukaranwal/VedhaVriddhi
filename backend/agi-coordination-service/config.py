from pydantic import BaseSettings
from typing import List

class AGICoordinationSettings(BaseSettings):
    # Service Configuration
    service_name: str = "agi-coordination-service"
    service_port: int = 8208
    debug: bool = False
    
    # AGI Coordination Configuration
    max_agents: int = 50
    default_coordination_mode: str = "democratic"
    consensus_threshold: float = 0.7
    max_reasoning_depth: int = 10
    
    # Supported Coordination Modes
    coordination_modes: List[str] = [
        "centralized", "decentralized", "hierarchical", 
        "democratic", "swarm"
    ]
    
    # Multi-Agent Settings
    agent_timeout: int = 60
    max_concurrent_tasks: int = 20
    knowledge_synthesis_enabled: bool = True
    collective_intelligence_threshold: float = 0.8
    
    # Database Configuration
    database_url: str = "postgresql://vedhavriddhi:vedhavriddhi123@localhost:5432/agi_coord_db"
    redis_url: str = "redis://localhost:6379/8"
    
    # Performance Settings
    coordination_cache_size: int = 200
    decision_timeout: int = 120
    
    class Config:
        env_file = ".env"
        case_sensitive = False
