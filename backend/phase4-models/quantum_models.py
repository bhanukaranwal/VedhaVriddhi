from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from decimal import Decimal

class QuantumPortfolioRequest(BaseModel):
    assets: List[str] = Field(..., description="List of asset identifiers")
    expected_returns: List[float] = Field(..., description="Expected returns for each asset")
    covariance_matrix: List[List[float]] = Field(..., description="Asset covariance matrix")
    risk_tolerance: float = Field(..., description="Risk tolerance parameter")
    quantum_processor: str = Field(default="ibm", description="Preferred quantum processor")

class QuantumOptimizationResult(BaseModel):
    optimized_weights: List[float] = Field(..., description="Optimal portfolio weights")
    expected_return: float = Field(..., description="Expected portfolio return")
    risk_level: float = Field(..., description="Portfolio risk level")
    quantum_advantage: float = Field(..., description="Speedup vs classical computation")
    computation_time: float = Field(..., description="Total computation time in seconds")
    confidence: float = Field(..., description="Result confidence level")

class AGIAnalysisRequest(BaseModel):
    market_data: Dict[str, Any] = Field(..., description="Market data for analysis")
    analysis_type: str = Field(..., description="Type of analysis to perform")
    time_horizon: int = Field(default=30, description="Analysis time horizon in days")
    confidence_threshold: float = Field(default=0.7, description="Minimum confidence threshold")

class NLQueryRequest(BaseModel):
    query: str = Field(..., description="Natural language query")
    context: Dict[str, Any] = Field(default_factory=dict, description="Query context")
    user_id: str = Field(..., description="User identifier")
    language: str = Field(default="en", description="Query language")

class DeFiSwapRequest(BaseModel):
    token_in: str = Field(..., description="Input token address")
    token_out: str = Field(..., description="Output token address") 
    amount_in: Decimal = Field(..., description="Input amount")
    slippage_tolerance: float = Field(default=0.005, description="Maximum slippage tolerance")
    recipient: str = Field(..., description="Recipient address")

class CBDCTransferRequest(BaseModel):
    from_account: str = Field(..., description="Source account")
    to_account: str = Field(..., description="Destination account")
    amount: Decimal = Field(..., description="Transfer amount")
    cbdc_type: str = Field(..., description="CBDC type (USD, EUR, etc.)")
    compliance_data: Dict[str, Any] = Field(default_factory=dict, description="Compliance information")

class MetaverseSessionRequest(BaseModel):
    user_id: str = Field(..., description="User identifier")
    environment_type: str = Field(..., description="Preferred environment type")
    device_capabilities: Dict[str, Any] = Field(..., description="VR/AR device capabilities")
    session_duration: int = Field(default=3600, description="Session duration in seconds")

class BiometricAuthRequest(BaseModel):
    user_id: str = Field(..., description="User identifier")
    biometric_data: Dict[str, Any] = Field(..., description="Biometric data")
    auth_type: str = Field(..., description="Authentication type")

class ClimateRiskRequest(BaseModel):
    asset_id: str = Field(..., description="Asset identifier")
    time_horizon: int = Field(default=365, description="Risk assessment horizon in days")
    scenarios: List[str] = Field(default_factory=list, description="Climate scenarios to analyze")

class QuantumMLTrainingRequest(BaseModel):
    training_data: Dict[str, Any] = Field(..., description="Training dataset")
    architecture: Dict[str, Any] = Field(..., description="Model architecture specification")
    quantum_params: Dict[str, Any] = Field(..., description="Quantum-specific parameters")
