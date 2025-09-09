from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, Numeric
from sqlalchemy.orm import declarative_base
from datetime import datetime
from decimal import Decimal

Base = declarative_base()

class DeFiProtocol(Base):
    __tablename__ = 'defi_protocols'

    id = Column(Integer, primary_key=True, index=True)
    protocol_id = Column(String, unique=True, index=True)
    protocol_name = Column(String, index=True)
    protocol_type = Column(String)  # dex, lending, yield_farming, etc.
    blockchain = Column(String, index=True)
    contract_address = Column(String)
    total_value_locked = Column(Numeric(precision=20, scale=8))
    daily_volume = Column(Numeric(precision=20, scale=8))
    user_count = Column(Integer, default=0)
    governance_token = Column(String, nullable=True)
    audit_status = Column(String, default='unaudited')
    risk_score = Column(Float, default=0.5)
    apy_range = Column(JSON)  # {min: float, max: float, current: float}
    supported_assets = Column(JSON)
    fees_structure = Column(JSON)
    integration_status = Column(String, default='active')
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

class YieldStrategy(Base):
    __tablename__ = 'yield_strategies'

    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(String, unique=True, index=True)
    strategy_name = Column(String)
    strategy_type = Column(String)  # single_pool, multi_pool, arbitrage, etc.
    description = Column(String)
    protocols_involved = Column(JSON)
    asset_allocation = Column(JSON)
    expected_apy = Column(Float)
    risk_level = Column(String)  # low, medium, high
    minimum_investment = Column(Numeric(precision=20, scale=8))
    lock_period_days = Column(Integer, default=0)
    auto_compound = Column(Boolean, default=True)
    impermanent_loss_risk = Column(Float, default=0.0)
    gas_cost_estimate = Column(Numeric(precision=20, scale=8))
    historical_performance = Column(JSON)
    backtest_results = Column(JSON)
    active_users = Column(Integer, default=0)
    total_deposited = Column(Numeric(precision=20, scale=8), default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CrossChainBridge(Base):
    __tablename__ = 'cross_chain_bridges'
    
    id = Column(Integer, primary_key=True, index=True)
    bridge_id = Column(String, unique=True, index=True)
    bridge_name = Column(String)
    source_chain = Column(String, index=True)
    destination_chain = Column(String, index=True)
    supported_assets = Column(JSON)
    bridge_fee = Column(Float)
    transfer_time_minutes = Column(Integer)
    security_model = Column(String)
    total_volume_bridged = Column(Numeric(precision=20, scale=8), default=0)
    success_rate = Column(Float, default=1.0)
    status = Column(String, default='active')
    created_at = Column(DateTime, default=datetime.utcnow)

class CBDCIntegration(Base):
    __tablename__ = 'cbdc_integrations'
    
    id = Column(Integer, primary_key=True, index=True)
    cbdc_id = Column(String, unique=True, index=True)
    central_bank = Column(String)
    country = Column(String, index=True)
    currency_code = Column(String)
    blockchain_platform = Column(String)
    pilot_status = Column(String)  # research, pilot, live
    retail_availability = Column(Boolean, default=False)
    wholesale_availability = Column(Boolean, default=False)
    cross_border_enabled = Column(Boolean, default=False)
    privacy_level = Column(String)  # high, medium, low
    programmability = Column(Boolean, default=False)
    offline_capability = Column(Boolean, default=False)
    integration_endpoints = Column(JSON)
    api_documentation = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
