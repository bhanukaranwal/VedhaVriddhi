from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from enum import Enum

# Enums
class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"

class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    ICEBERG = "iceberg"
    FOK = "fill_or_kill"
    IOC = "immediate_or_cancel"

class TimeInForce(str, Enum):
    GTC = "good_till_cancel"
    IOC = "immediate_or_cancel"
    FOK = "fill_or_kill"
    GTD = "good_till_date"
    GFD = "good_for_day"

class OrderStatus(str, Enum):
    PENDING = "pending"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"

# Request Models
class OrderRequest(BaseModel):
    client_order_id: str = Field(..., description="Client order identifier")
    symbol: str = Field(..., description="Instrument symbol")
    side: OrderSide = Field(..., description="Order side (buy/sell)")
    order_type: OrderType = Field(..., description="Order type")
    quantity: Decimal = Field(..., gt=0, description="Order quantity")
    price: Optional[Decimal] = Field(None, gt=0, description="Order price (for limit orders)")
    time_in_force: TimeInForce = Field(TimeInForce.GTC, description="Time in force")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)

# Response Models
class OrderResponse(BaseModel):
    id: str
    client_order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: Decimal
    price: Optional[Decimal]
    filled_quantity: Decimal
    remaining_quantity: Decimal
    status: OrderStatus
    timestamp: datetime
    user_id: str
    account_id: str
    time_in_force: TimeInForce
    metadata: Dict[str, Any]

class TradeResponse(BaseModel):
    id: str
    symbol: str
    buyer_order_id: str
    seller_order_id: str
    quantity: Decimal
    price: Decimal
    timestamp: datetime
    trade_type: str

class PositionResponse(BaseModel):
    symbol: str
    account_id: str
    quantity: Decimal
    average_price: Decimal
    market_value: Decimal
    unrealized_pnl: Decimal
    realized_pnl: Decimal
    last_updated: datetime

class MarketDataResponse(BaseModel):
    symbol: str
    bid_price: Optional[Decimal]
    ask_price: Optional[Decimal]
    last_price: Optional[Decimal]
    volume: Decimal
    timestamp: datetime
    yield_to_maturity: Optional[Decimal]
    duration: Optional[Decimal]
    accrued_interest: Optional[Decimal]

class InstrumentResponse(BaseModel):
    isin: str
    symbol: str
    instrument_name: str
    issuer: str
    bond_type: str
    face_value: Decimal
    coupon_rate: Optional[Decimal]
    maturity_date: datetime
    currency: str
    exchange: str

# GraphQL Input Types (for Strawberry)
import strawberry
from typing import Optional as TypingOptional

@strawberry.enum
class OrderSideInput(Enum):
    BUY = "buy"
    SELL = "sell"

@strawberry.enum
class OrderTypeInput(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"

@strawberry.enum
class TimeInForceInput(Enum):
    GTC = "good_till_cancel"
    IOC = "immediate_or_cancel"
    FOK = "fill_or_kill"
    GTD = "good_till_date"

@strawberry.input
class OrderInput:
    client_order_id: str
    symbol: str
    side: OrderSideInput
    order_type: OrderTypeInput
    quantity: float
    price: TypingOptional[float] = None
    time_in_force: TypingOptional[TimeInForceInput] = TimeInForceInput.GTC
