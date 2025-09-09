from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, LargeBinary
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class BiometricTemplate(Base):
    __tablename__ = 'biometric_templates'

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(String, unique=True, index=True)
    user_id = Column(String, index=True)
    biometric_type = Column(String, index=True)  # fingerprint, facial, iris, voice, etc.
    template_data = Column(LargeBinary)  # Encrypted biometric template
    quality_score = Column(Float)
    confidence_threshold = Column(Float, default=0.8)
    enrollment_device = Column(String)
    encryption_method = Column(String, default='AES-256')
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, nullable=True)
    usage_count = Column(Integer, default=0)
    active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)

class BiometricAuthentication(Base):
    __tablename__ = 'biometric_authentications'
    
    id = Column(Integer, primary_key=True, index=True)
    authentication_id = Column(String, unique=True, index=True)
    user_id = Column(String, index=True)
    template_id = Column(String, index=True)
    biometric_type = Column(String, index=True)
    authentication_result = Column(Boolean)
    confidence_score = Column(Float)
    match_quality = Column(String)  # high, medium, low
    processing_time_ms = Column(Float)
    device_info = Column(JSON)
    location_info = Column(JSON, nullable=True)
    risk_assessment = Column(JSON)
    emotional_state = Column(JSON, nullable=True)
    stress_indicators = Column(JSON, nullable=True)
    liveness_verified = Column(Boolean, default=True)
    anti_spoofing_passed = Column(Boolean, default=True)
    authentication_timestamp = Column(DateTime, default=datetime.utcnow)
    session_id = Column(String, nullable=True)

class ConsciousnessState(Base):
    __tablename__ = 'consciousness_states'
    
    id = Column(Integer, primary_key=True, index=True)
    state_id = Column(String, unique=True, index=True)
    user_id = Column(String, index=True)
    consciousness_level = Column(String)  # individual, collective, universal, transcendent
    awareness_score = Column(Float)
    coherence_level = Column(Float)
    integration_depth = Column(Float)
    emotional_resonance = Column(Float)
    wisdom_quotient = Column(Float)
    measurement_method = Column(String)
    measurement_data = Column(JSON)
    contributing_factors = Column(JSON)
    measurement_timestamp = Column(DateTime, default=datetime.utcnow)
    session_duration_minutes = Column(Float, nullable=True)
    meditation_state = Column(Boolean, default=False)
    stress_level = Column(Float, nullable=True)
    focus_level = Column(Float, nullable=True)

class NeuralFeedback(Base):
    __tablename__ = 'neural_feedback'
    
    id = Column(Integer, primary_key=True, index=True)
    feedback_id = Column(String, unique=True, index=True)
    user_id = Column(String, index=True)
    feedback_type = Column(String)  # eeg, heart_rate_variability, breathing, etc.
    feedback_data = Column(JSON)
    target_state = Column(String)
    achieved_state = Column(String)
    improvement_score = Column(Float)
    session_effectiveness = Column(Float)
    recommendations = Column(JSON)
    next_session_suggested = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    session_duration_minutes = Column(Float)
    device_used = Column(String)
    calibration_data = Column(JSON, nullable=True)
