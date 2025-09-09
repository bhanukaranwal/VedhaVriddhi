from pydantic import BaseSettings
from typing import List, Optional

class QuantumSettings(BaseSettings):
    # Service Configuration
    service_name: str = "quantum-computing-service"
    service_port: int = 8200
    debug: bool = False
    
    # Quantum Backend Configuration
    default_quantum_backend: str = "qiskit_aer"
    ibm_quantum_token: Optional[str] = None
    max_qubits: int = 32
    max_shots: int = 8192
    max_job_timeout: int = 300
    
    # Supported Quantum Backends
    supported_backends: List[str] = [
        "qiskit_aer", "ibm_quantum", "rigetti", "ionq", 
        "cirq_simulator", "pennylane"
    ]
    
    # Optimization Settings
    max_optimization_variables: int = 1000
    optimization_timeout: int = 600
    convergence_threshold: float = 1e-6
    
    # Database Configuration
    database_url: str = "postgresql://vedhavriddhi:vedhavriddhi123@localhost:5432/quantum_db"
    redis_url: str = "redis://localhost:6379/0"
    
    # Security Settings
    encryption_key: str = "quantum_encryption_key_2025"
    max_request_size: int = 10485760  # 10MB
    
    class Config:
        env_file = ".env"
        case_sensitive = False
