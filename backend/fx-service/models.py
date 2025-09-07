from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional, Dict, List
from datetime import datetime
from decimal import Decimal

class FXProvider(str, Enum):
    BLOOMBERG = "bloomberg"
    REFINITIV = "refinitiv"
    REUTERS = "reuters"
    ICE = "ice"
    OANDA = "oanda"

class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    SGD = "SGD"
    HKD = "HKD"
    INR = "INR"
    AUD = "AUD"
    CAD = "CAD"
    CHF = "CHF"
    CNY = "CNY"

class FXQuote(BaseModel):
    currency_pair: str = Field(..., description="Currency pair (e.g., USD/EUR)")
    base_currency: Currency = Field(..., description="Base currency")
    quote_currency: Currency = Field(..., description="Quote currency")
    bid_rate: Decimal = Field(..., description="Bid exchange rate")
    ask_rate: Decimal = Field(..., description="Ask exchange rate") 
    mid_rate: Decimal = Field(..., description="Mid market rate")
    spread_bps: int = Field(..., description="Bid-ask spread in basis points")
    liquidity: Decimal = Field(..., description="Available liquidity")
    provider: FXProvider = Field(..., description="Rate provider")
    timestamp: datetime = Field(..., description="Quote timestamp")
    volatility: Optional[Decimal] = Field(None, description="Implied volatility")

class FXConversionRequest(BaseModel):
    from_currency: Currency = Field(..., description="Source currency")
    to_currency: Currency = Field(..., description="Target currency") 
    amount: Decimal = Field(..., description="Amount to convert")
    execution_type: str = Field(default="mid", description="Execution type: mid, bid, ask")
    settlement_date: Optional[datetime] = Field(None, description="Settlement date")

class FXConversionResponse(BaseModel):
    from_currency: Currency
    to_currency: Currency
    original_amount: Decimal
    converted_amount: Decimal
    exchange_rate: Decimal
    execution_type: str
    spread_bps: int
    conversion_cost: Decimal
    timestamp: datetime
    reference_id: str

class FXHedgeRequest(BaseModel):
    portfolio_id: str = Field(..., description="Portfolio identifier")
    target_currency: Currency = Field(..., description="Target hedge currency")
    hedge_ratio: Decimal = Field(..., ge=0, le=1, description="Hedge ratio (0-1)")
    hedge_horizon_days: int = Field(..., description="Hedge horizon in days")
    instruments: List[str] = Field(default=["spot", "forward"], description="Hedge instruments")

class FXPosition(BaseModel):
    currency: Currency
    position: Decimal  # Positive = long, negative = short
    notional_value_usd: Decimal
    market_value_usd: Decimal
    unrealized_pnl_usd: Decimal
    hedge_ratio: Decimal
    last_updated: datetime

class FXRisk(BaseModel):
    portfolio_id: str
    total_fx_exposure_usd: Decimal
    var_95_1d_usd: Decimal
    expected_shortfall_usd: Decimal
    largest_exposure: FXPosition
    currency_breakdown: List[FXPosition]
    hedge_effectiveness: Decimal
    last_calculated: datetime
