from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime
from decimal import Decimal

class ESGScore(BaseModel):
    instrument_id: str = Field(..., description="Instrument identifier")
    esg_rating: float = Field(..., ge=0, le=100, description="Overall ESG rating (0-100)")
    environmental_score: float = Field(..., ge=0, le=100, description="Environmental component score")
    social_score: float = Field(..., ge=0, le=100, description="Social component score")
    governance_score: float = Field(..., ge=0, le=100, description="Governance component score")
    rating_agency: str = Field(..., description="Rating agency (MSCI, Sustainalytics, etc.)")
    last_updated: datetime = Field(..., description="Last updated timestamp")

class PortfolioESGSummary(BaseModel):
    portfolio_id: str = Field(..., description="Portfolio identifier")
    overall_esg_score: float = Field(..., description="Weighted average ESG score")
    environmental_score: float = Field(..., description="Environmental score")
    social_score: float = Field(..., description="Social score")
    governance_score: float = Field(..., description="Governance score")
    coverage_percentage: float = Field(..., description="Percentage of portfolio with ESG data")
    score_details: Dict[str, float] = Field(default_factory=dict, description="Detailed ESG metrics")
    top_esg_holdings: List[Dict] = Field(default_factory=list, description="Top ESG-rated holdings")
    esg_risk_factors: List[str] = Field(default_factory=list, description="Identified ESG risks")
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class GreenBond(BaseModel):
    bond_id: str = Field(..., description="Green bond identifier")
    issuer: str = Field(..., description="Bond issuer")
    green_bond_framework: str = Field(..., description="Green bond framework type")
    use_of_proceeds: List[str] = Field(..., description="Use of proceeds categories")
    environmental_impact: Dict[str, float] = Field(default_factory=dict, description="Environmental impact metrics")
    certification: Optional[str] = Field(None, description="Third-party certification")
    yield_rate: Decimal = Field(..., description="Current yield rate")
    maturity_date: datetime = Field(..., description="Bond maturity date")
    rating: str = Field(..., description="Credit rating")
    currency: str = Field(..., description="Bond currency")
    issue_size: Decimal = Field(..., description="Total issue size")

class ESGRiskAssessment(BaseModel):
    instrument_id: str = Field(..., description="Instrument identifier")
    climate_risk_score: float = Field(..., description="Climate transition risk score")
    physical_risk_score: float = Field(..., description="Physical climate risk score")
    regulatory_risk_score: float = Field(..., description="Regulatory risk score")
    reputational_risk_score: float = Field(..., description="Reputational risk score")
    overall_risk_level: str = Field(..., description="Overall ESG risk level (Low/Medium/High)")
    risk_factors: List[str] = Field(default_factory=list, description="Key risk factors")
    mitigation_strategies: List[str] = Field(default_factory=list, description="Recommended mitigation strategies")
