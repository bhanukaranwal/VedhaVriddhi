from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from decimal import Decimal
from enum import Enum

class YieldCurvePoint(BaseModel):
    tenor: float = Field(..., description="Tenor in years")
    yield_value: float = Field(..., description="Yield in percentage")
    maturity_date: datetime = Field(..., description="Maturity date")
    curve_type: str = Field(..., description="Type of curve (government, corporate, etc.)")
    timestamp: datetime = Field(..., description="Data timestamp")

class YieldCurveModel(BaseModel):
    curve_type: str
    points: List[YieldCurvePoint]
    statistics: Dict[str, float]
    model_parameters: Optional[Dict[str, float]] = None
    last_updated: datetime

class PortfolioAnalytics(BaseModel):
    portfolio_id: str
    total_return: float
    benchmark_return: float
    attribution: Dict[str, float]
    risk_metrics: Dict[str, float]
    allocation_breakdown: Dict[str, Any]
    duration_metrics: Dict[str, float]
    credit_analysis: Dict[str, Any]
    last_updated: datetime

class MLPredictionRequest(BaseModel):
    model_type: str = Field(..., description="Type of ML model to use")
    features: List[float] = Field(..., description="Input features for prediction")
    horizon: int = Field(1, description="Prediction horizon in days")
    confidence_level: float = Field(0.95, description="Confidence level for prediction")

class MLPredictionResponse(BaseModel):
    model_type: str
    prediction: float
    confidence: float
    horizon_days: int
    features_used: int
    timestamp: datetime
    model_version: str

class ScenarioAnalysisRequest(BaseModel):
    portfolio_id: str
    scenarios: List[Dict[str, Any]]
    confidence_level: float = 0.95

class PerformanceAttribution(BaseModel):
    portfolio_id: str
    period_start: datetime
    period_end: datetime
    total_return: float
    benchmark_return: float
    active_return: float
    attribution: Dict[str, float]
    sector_attribution: Dict[str, float]
    security_selection: float
    asset_allocation: float
    interaction_effect: float
