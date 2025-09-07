from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class RiskMetric(BaseModel):
    metric_name: str
    value: float
    threshold: Optional[float] = None
    status: str = Field(..., description="green, yellow, red")
    timestamp: datetime

class VaRMetrics(BaseModel):
    portfolio_id: str
    var_95_1d: float = Field(..., description="1-day VaR at 95% confidence")
    var_99_1d: float = Field(..., description="1-day VaR at 99% confidence")
    var_95_10d: float = Field(..., description="10-day VaR at 95% confidence")
    var_99_10d: float = Field(..., description="10-day VaR at 99% confidence")
    expected_shortfall_95: float
    expected_shortfall_99: float
    calculation_method: str = Field(..., description="historical, parametric, monte_carlo")
    confidence_interval: Dict[str, float]
    timestamp: datetime

class StressTestRequest(BaseModel):
    portfolio_id: str
    scenarios: List[str] = Field(..., description="List of scenario names to run")
    confidence_level: float = Field(0.95, ge=0.5, le=0.99)
    custom_parameters: Optional[Dict[str, Any]] = None

class StressTestResult(BaseModel):
    portfolio_id: str
    scenario_name: str
    baseline_value: float
    stressed_value: float
    impact_absolute: float
    impact_percentage: float
    position_impacts: List[Dict[str, Any]]
    scenario_parameters: Dict[str, Any]
    timestamp: datetime

class RiskLimit(BaseModel):
    limit_id: str
    portfolio_id: str
    limit_type: str = Field(..., description="var, concentration, exposure, etc.")
    limit_value: float
    current_value: float
    utilization_pct: float
    status: str = Field(..., description="green, yellow, red")
    threshold_warning: float
    threshold_breach: float
    last_updated: datetime

class ConcentrationRisk(BaseModel):
    portfolio_id: str
    concentration_type: str = Field(..., description="issuer, sector, rating, maturity")
    concentrations: List[Dict[str, Any]]
    max_concentration_pct: float
    diversification_ratio: float
    herfindahl_index: float
    effective_number_holdings: float
    timestamp: datetime

class LiquidityRisk(BaseModel):
    portfolio_id: str
    liquidity_score: float = Field(..., ge=0, le=1, description="0=illiquid, 1=very liquid")
    liquidity_at_risk: float
    funding_gap: float
    days_to_liquidate: Dict[str, float]  # percentage of portfolio -> days
    liquidity_buffer: float
    timestamp: datetime

class RiskAlert(BaseModel):
    alert_id: str
    portfolio_id: str
    alert_type: str = Field(..., description="limit_breach, concentration, liquidity, etc.")
    severity: str = Field(..., description="low, medium, high, critical")
    message: str
    details: Dict[str, Any]
    triggered_at: datetime
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None

class PortfolioRiskSummary(BaseModel):
    portfolio_id: str
    total_value: float
    var_metrics: VaRMetrics
    concentration_risk: ConcentrationRisk
    liquidity_risk: LiquidityRisk
    active_limits: List[RiskLimit]
    recent_alerts: List[RiskAlert]
    risk_score: float = Field(..., ge=0, le=100, description="Overall risk score")
    last_updated: datetime
