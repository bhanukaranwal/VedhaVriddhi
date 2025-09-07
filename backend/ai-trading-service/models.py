from pydantic import BaseModel, Field
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
from decimal import Decimal

class TradingSide(str, Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"

class StrategyType(str, Enum):
    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"
    ARBITRAGE = "arbitrage"
    SENTIMENT = "sentiment"
    ML_PREDICTION = "ml_prediction"

class SignalStrength(str, Enum):
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    VERY_STRONG = "very_strong"

class TradeSignal(BaseModel):
    signal_id: str = Field(..., description="Unique signal identifier")
    symbol: str = Field(..., description="Instrument symbol")
    side: TradingSide = Field(..., description="Trade direction")
    confidence: float = Field(..., ge=0, le=1, description="Confidence level (0-1)")
    strength: SignalStrength = Field(..., description="Signal strength")
    price_target: Optional[Decimal] = Field(None, description="Target price")
    stop_loss: Optional[Decimal] = Field(None, description="Stop loss price")
    time_horizon_minutes: int = Field(60, description="Time horizon in minutes")
    strategy_name: str = Field(..., description="Originating strategy")
    strategy_type: StrategyType = Field(..., description="Strategy category")
    market_conditions: Dict[str, Any] = Field(default_factory=dict)
    risk_parameters: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class TradingAgent(BaseModel):
    agent_id: str = Field(..., description="Unique agent identifier")
    agent_type: str = Field(..., description="Agent type/strategy")
    status: str = Field(default="active", description="Agent status")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    performance_metrics: Dict[str, float] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class AgentPerformanceMetrics(BaseModel):
    agent_id: str
    total_signals: int = 0
    successful_signals: int = 0
    win_rate: float = 0.0
    average_return: float = 0.0
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    calmar_ratio: float = 0.0
    information_ratio: float = 0.0
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class MLModelConfig(BaseModel):
    model_id: str
    model_type: str = Field(..., description="Type of ML model")
    input_features: List[str] = Field(..., description="Required input features")
    output_format: str = Field(..., description="Output format")
    confidence_threshold: float = Field(0.7, description="Minimum confidence for signals")
    retrain_frequency_hours: int = Field(24, description="Retraining frequency")
    performance_metrics: Dict[str, float] = Field(default_factory=dict)
    last_trained: Optional[datetime] = None

class MarketRegime(BaseModel):
    regime_id: str
    name: str
    description: str
    indicators: Dict[str, Any]
    active_strategies: List[str]
    risk_adjustments: Dict[str, float]
    detected_at: datetime
    confidence: float
