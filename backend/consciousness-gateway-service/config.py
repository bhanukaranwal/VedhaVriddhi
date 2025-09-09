from pydantic import BaseSettings
from typing import List

class ConsciousnessSettings(BaseSettings):
    # Service Configuration
    service_name: str = "consciousness-gateway-service"
    service_port: int = 8210
    debug: bool = False
    
    # Consciousness Processing
    global_consciousness_enabled: bool = True
    collective_intelligence_threshold: float = 0.7
    wisdom_synthesis_enabled: bool = True
    mindfulness_monitoring: bool = True
    
    # Consciousness Levels
    consciousness_levels: List[str] = [
        "individual", "collective", "universal", "transcendent"
    ]
    
    # Synthesis Parameters
    min_wisdom_elements_for_synthesis: int = 5
    synthesis_frequency_minutes: int = 30
    consciousness_evolution_monitoring: bool = True
    
    # Database Configuration  
    database_url: str = "postgresql://vedhavriddhi:vedhavriddhi123@localhost:5432/consciousness_db"
    redis_url: str = "redis://localhost:6379/10"
    
    # Integration Settings
    neural_interface_integration: bool = True
    biometric_consciousness_correlation: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False
