from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from decimal import Decimal

class PortfolioSummary(BaseModel):
    portfolio_id: str = Field(..., description="Portfolio identifier")
    total_value: Decimal = Field(..., description="Total portfolio value")
    currency: str = Field(..., description="Portfolio currency")
    day_change: Decimal = Field(..., description="Day change amount")
    day_change_pct: float = Field(..., description="Day change percentage")
    positions_count: int = Field(..., description="Number of positions")
    available_cash: Decimal = Field(..., description="Available cash")
    last_updated: datetime = Field(..., description="Last update timestamp")

class MobilePosition(BaseModel):
    symbol: str = Field(..., description="Instrument symbol")
    name: str = Field(..., description="Instrument name")
    quantity: Decimal = Field(..., description="Position quantity")
    market_value: Decimal = Field(..., description="Current market value")
    cost_basis: Decimal = Field(..., description="Cost basis")
    unrealized_pnl: Decimal = Field(..., description="Unrealized P&L")
    unrealized_pnl_pct: float = Field(..., description="Unrealized P&L percentage")
    last_price: Decimal = Field(..., description="Last traded price")
    price_change: Decimal = Field(..., description="Price change")
    price_change_pct: float = Field(..., description="Price change percentage")

class WatchlistItem(BaseModel):
    symbol: str = Field(..., description="Instrument symbol")
    name: str = Field(..., description="Instrument name")
    last_price: Decimal = Field(..., description="Last price")
    price_change: Decimal = Field(..., description="Price change")
    price_change_pct: float = Field(..., description="Price change percentage")
    volume: int = Field(..., description="Trading volume")
    market_cap: Optional[Decimal] = Field(None, description="Market capitalization")

class QuickOrderRequest(BaseModel):
    symbol: str = Field(..., description="Instrument symbol")
    side: str = Field(..., description="Buy or Sell")
    quantity: Decimal = Field(..., description="Order quantity")
    order_type: str = Field(default="market", description="Order type")
    price: Optional[Decimal] = Field(None, description="Limit price")
    portfolio_id: str = Field(..., description="Portfolio ID")

class OrderResponse(BaseModel):
    order_id: str = Field(..., description="Order identifier")
    status: str = Field(..., description="Order status")
    message: str = Field(..., description="Status message")
    timestamp: datetime = Field(..., description="Response timestamp")
