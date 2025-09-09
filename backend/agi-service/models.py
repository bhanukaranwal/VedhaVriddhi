from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, Text
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class AGIAgent(Base):
    __tablename__ = 'agi_agents'

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String, unique=True, index=True)
    agent_name = Column(String)
    agent_type = Column(String)  # reasoning, nlp, decision_making, etc.
    capabilities = Column(JSON)
    specializations = Column(JSON)
    current_load = Column(Float, default=0.0)
    performance_score = Column(Float, default=1.0)
    trust_score = Column(Float, default=0.8)
    intelligence_quotient = Column(Float, default=100.0)
    emotional_intelligence = Column(Float, default=0.5)
    creativity_score = Column(Float, default=0.5)
    learning_rate = Column(Float, default=0.1)
    memory_capacity = Column(Integer, default=1000)
    last_active = Column(DateTime, default=datetime.utcnow)
    total_tasks_completed = Column(Integer, default=0)
    average_task_completion_time = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String, default='active')

class ReasoningSession(Base):
    __tablename__ = 'reasoning_sessions'
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    user_id = Column(String, index=True)
    reasoning_type = Column(String)  # deductive, inductive, abductive, causal
    input_premises = Column(JSON)
    reasoning_chain = Column(JSON)
    conclusion = Column(JSON)
    confidence_score = Column(Float)
    logical_validity = Column(Boolean)
    reasoning_time_ms = Column(Float)
    agent_id = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class KnowledgeGraph(Base):
    __tablename__ = 'knowledge_graph'
    
    id = Column(Integer, primary_key=True, index=True)
    entity_id = Column(String, index=True)
    entity_type = Column(String)
    entity_name = Column(String)
    properties = Column(JSON)
    relationships = Column(JSON)
    confidence_score = Column(Float)
    source_agent = Column(String, index=True)
    verification_status = Column(String, default='unverified')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CollectiveDecision(Base):
    __tablename__ = 'collective_decisions'
    
    id = Column(Integer, primary_key=True, index=True)
    decision_id = Column(String, unique=True, index=True)
    decision_context = Column(JSON)
    participating_agents = Column(JSON)
    individual_decisions = Column(JSON)
    aggregation_method = Column(String)
    final_decision = Column(JSON)
    confidence_level = Column(Float)
    consensus_score = Column(Float)
    decision_quality_score = Column(Float)
    implementation_status = Column(String, default='pending')
    outcome_feedback = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    finalized_at = Column(DateTime, nullable=True)
