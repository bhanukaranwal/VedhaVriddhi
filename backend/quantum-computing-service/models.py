from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.ext.declarative import declared_attr
from datetime import datetime

Base = declarative_base()

class QuantumJobRecord(Base):
    __tablename__ = 'quantum_job_records'

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True)
    user_id = Column(String, index=True)
    algorithm_type = Column(String, index=True)
    input_parameters = Column(JSON)
    circuit_definition = Column(JSON)
    quantum_backend = Column(String)
    shots = Column(Integer)
    optimization_level = Column(Integer)
    status = Column(String, default='pending')
    result_data = Column(JSON)
    error_message = Column(String, nullable=True)
    quantum_advantage = Column(Float, nullable=True)
    execution_time_ms = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

class QuantumDeviceCalibration(Base):
    __tablename__ = 'quantum_device_calibration'
    
    id = Column(Integer, primary_key=True, index=True)
    device_name = Column(String, unique=True, index=True)
    calibration_data = Column(JSON)
    gate_errors = Column(JSON)
    readout_errors = Column(JSON)
    coherence_times = Column(JSON)
    availability = Column(Float)
    last_calibrated = Column(DateTime)
    next_calibration = Column(DateTime)
    status = Column(String, default='active')
    created_at = Column(DateTime, default=datetime.utcnow)

class QuantumOptimizationResult(Base):
    __tablename__ = 'quantum_optimization_results'
    
    id = Column(Integer, primary_key=True, index=True)
    optimization_id = Column(String, unique=True, index=True)
    portfolio_id = Column(String, index=True)
    optimization_type = Column(String)
    input_constraints = Column(JSON)
    optimal_weights = Column(JSON)
    expected_return = Column(Float)
    risk_level = Column(Float)
    sharpe_ratio = Column(Float)
    quantum_advantage_factor = Column(Float)
    classical_benchmark = Column(JSON)
    convergence_iterations = Column(Integer)
    optimization_time_ms = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
