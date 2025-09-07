from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional, Dict, List, Any
from datetime import datetime
from decimal import Decimal

class MarketSession(str, Enum):
    ASIAN = "asian"
    EUROPEAN = "european"
    AMERICAN = "american"

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

class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"

class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"

class OrderStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

class GlobalOrder(BaseModel):
    order_id: str = Field(..., description="Unique global order identifier")
    client_id: str = Field(..., description="Client identifier")
    portfolio_id: str = Field(..., description="Portfolio identifier")
    symbol: str = Field(..., description="Instrument symbol (ISIN or local identifier)")
    quantity: Decimal = Field(..., description="Order quantity")
    price: Optional[Decimal] = Field(None, description="Order price (None for market orders)")
    currency: Currency = Field(..., description="Order currency")
    side: OrderSide = Field(..., description="Buy or Sell")
    order_type: OrderType = Field(default=OrderType.LIMIT, description="Order type")
    time_in_force: str = Field(default="DAY", description="Time in force (DAY, GTC, IOC, FOK)")
    target_market: str = Field(..., description="Target market/exchange code")
    settlement_date: Optional[datetime] = Field(None, description="Settlement date")
    regulatory_flags: Dict[str, Any] = Field(default_factory=dict, description="Regulatory compliance flags")
    execution_instructions: Dict[str, Any] = Field(default_factory=dict, description="Special execution instructions")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    filled_quantity: Decimal = Field(default=Decimal('0'))
    avg_fill_price: Optional[Decimal] = Field(None)

class MarketData(BaseModel):
    symbol: str
    bid_price: Decimal
    ask_price: Decimal
    last_price: Decimal
    volume: Decimal
    market: str
    currency: Currency
    timestamp: datetime

class CurrencyPair(BaseModel):
    base_currency: Currency
    quote_currency: Currency
    rate: Decimal
    timestamp: datetime

class TradeExecution(BaseModel):
    execution_id: str
    order_id: str
    symbol: str
    quantity: Decimal
    price: Decimal
    currency: Currency
    side: OrderSide
    market: str
    execution_time: datetime
    settlement_date: datetime
    trade_id: str
    counterparty: Optional[str] = None

class GlobalMarketStatus(BaseModel):
    market_code: str
    market_name: str
    country: str
    currency: Currency
    session: MarketSession
    is_open: bool
    open_time: Optional[datetime] = None
    close_time: Optional[datetime] = None
    timezone: str
    last_updated: datetime
