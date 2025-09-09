from pydantic import BaseSettings
from typing import List, Optional

class QuantumMLSettings(BaseSettings):
    # Service Configuration
    service_name: str = "quantum-ml-service"
    service_port: int = 8206
    debug: bool = False
    
    # Quantum ML Configuration
    default_quantum_device: str = "default.qubit"
    max_qubits: int = 20
    max_layers: int = 10
    max_shots: int = 1000
    
    # Supported Quantum ML Frameworks
    supported_frameworks: List[str] = [
        "pennylane", "qiskit", "cirq", "tensorflow_quantum"
    ]
    
    # Model Training Settings
    max_training_epochs: int = 100
    early_stopping_patience: int = 10
    learning_rate: float = 0.01
    batch_size: int = 32
    
    # Database Configuration
    database_url: str = "postgresql://vedhavriddhi:vedhavriddhi123@localhost:5432/quantum_ml_db"
    redis_url: str = "redis://localhost:6379/6"
    
    # Performance Settings
    model_cache_size: int = 100
    prediction_timeout: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False
