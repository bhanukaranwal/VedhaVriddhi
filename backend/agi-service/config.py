from pydantic import BaseSettings
from typing import Dict, List, Optional

class Settings(BaseSettings):
    # Service Configuration
    service_name: str = "agi-service"
    service_version: str = "4.0.0"
    service_port: int = 8201
    debug: bool = False
    
    # AGI Model Configuration
    primary_llm_model: str = "gpt-4o"
    secondary_llm_model: str = "claude-3-sonnet"
    embedding_model: str = "text-embedding-3-large"
    
    # OpenAI Configuration
    openai_api_key: str = ""
    openai_organization: str = ""
    openai_max_tokens: int = 4000
    openai_temperature: float = 0.1
    
    # Anthropic Configuration
    anthropic_api_key: str = ""
    anthropic_max_tokens: int = 4000
    
    # Database Configuration
    agi_db_url: str = "postgresql://vedhavriddhi:vedhavriddhi123@localhost:5432/vedhavriddhi_agi"
    redis_url: str = "redis://localhost:6379/12"
    vector_db_url: str = "http://localhost:6333"  # Qdrant vector database
    
    # Agent Configuration
    max_agents_per_network: int = 50
    default_agent_memory_size: int = 1000
    agent_coordination_frequency: float = 1.0  # seconds
    max_reasoning_depth: int = 5
    
    # Natural Language Processing
    nlp_confidence_threshold: float = 0.6
    max_conversation_history: int = 100
    enable_multilingual: bool = True
    supported_languages: List[str] = ["en", "es", "fr", "de", "zh"]
    
    # Knowledge Management
    enable_knowledge_sharing: bool = True
    knowledge_update_frequency: int = 3600  # seconds
    semantic_search_enabled: bool = True
    
    # Learning Configuration
    enable_online_learning: bool = True
    learning_rate: float = 0.001
    experience_replay_buffer_size: int = 10000
    min_experiences_for_learning: int = 100
    
    # Safety and Ethics
    enable_ethical_constraints: bool = True
    safety_check_level: str = "strict"  # strict, moderate, permissive
    max_action_risk_threshold: float = 0.3
    require_human_approval_for_high_risk: bool = True
    
    # Performance Configuration
    max_concurrent_queries: int = 100
    response_timeout_seconds: int = 30
    memory_optimization_enabled: bool = True
    
    # Communication Configuration
    enable_inter_agent_communication: bool = True
    communication_protocol: str = "websocket"  # websocket, http, grpc
    message_queue_size: int = 1000
    
    # Monitoring Configuration
    enable_performance_monitoring: bool = True
    log_agent_decisions: bool = True
    track_learning_progress: bool = True
    
    # Financial Domain Configuration
    financial_data_sources: List[str] = ["bloomberg", "reuters", "yahoo_finance"]
    market_data_refresh_interval: int = 60  # seconds
    enable_real_time_market_data: bool = True
    
    # External Service URLs
    quantum_service_url: str = "http://localhost:8200"
    market_data_url: str = "http://localhost:8001"
    portfolio_service_url: str = "http://localhost:8002"
    risk_service_url: str = "http://localhost:8004"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
