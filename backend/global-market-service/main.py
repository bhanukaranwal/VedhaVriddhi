import asyncio
import logging
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum

import structlog
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from core.order_router import GlobalOrderRouter
from core.market_data import GlobalMarketDataService
from core.currency_converter import CurrencyConverter
from core.settlement_engine import SettlementEngine
from database.global_db import GlobalTradingDB
from models import *
from config import Settings

logger = structlog.get_logger()

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

class GlobalOrder(BaseModel):
    order_id: str = Field(..., description="Unique global order identifier")
    client_id: str = Field(..., description="Client identifier")
    symbol: str = Field(..., description="Instrument symbol")
    quantity: Decimal = Field(..., description="Order quantity")
    price: Optional[Decimal] = Field(None, description="Order price (None for market orders)")
    currency: Currency = Field(..., description="Order currency")
    target_market: str = Field(..., description="Target market/exchange")
    side: str = Field(..., description="Buy or Sell")
    order_type: str = Field(default="limit", description="Order type")
    time_in_force: str = Field(default="DAY", description="Time in force")
    settlement_date: Optional[datetime] = None
    regulatory_flags: Dict[str, Any] = Field(default_factory=dict)

class GlobalMarketService:
    def __init__(self):
        self.settings = Settings()
        self.order_router = GlobalOrderRouter(self.settings)
        self.market_data = GlobalMarketDataService(self.settings)
        self.currency_converter = CurrencyConverter(self.settings)
        self.settlement_engine = SettlementEngine(self.settings)
        self.db = GlobalTradingDB(self.settings)
        self.active_sessions = set()
        
    async def initialize(self):
        """Initialize global market service"""
        logger.info("Initializing Global Market Service")
        
        try:
            await self.db.initialize()
            await self.order_router.initialize()
            await self.market_data.initialize()
            await self.currency_converter.initialize()
            await self.settlement_engine.initialize()
            
            # Start market session monitoring
            asyncio.create_task(self.monitor_global_sessions())
            asyncio.create_task(self.process_cross_currency_orders())
            
            logger.info("Global Market Service initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize Global Market Service", error=str(e))
            raise
    
    async def monitor_global_sessions(self):
        """Monitor global trading sessions"""
        while True:
            try:
                current_time = datetime.now(timezone.utc)
                active_sessions = self.determine_active_sessions(current_time)
                
                if active_sessions != self.active_sessions:
                    self.active_sessions = active_sessions
                    logger.info(f"Active trading sessions: {active_sessions}")
                    await self.adjust_routing_for_sessions(active_sessions)
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error("Session monitoring error", error=str(e))
                await asyncio.sleep(60)
    
    def determine_active_sessions(self, current_time: datetime) -> set:
        """Determine which trading sessions are currently active"""
        hour = current_time.hour
        active = set()
        
        # Asian session (00:00-09:00 UTC)
        if 0 <= hour < 9:
            active.add(MarketSession.ASIAN)
            
        # European session (07:00-17:00 UTC)  
        if 7 <= hour < 17:
            active.add(MarketSession.EUROPEAN)
            
        # American session (13:00-22:00 UTC)
        if 13 <= hour < 22:
            active.add(MarketSession.AMERICAN)
            
        return active
    
    async def adjust_routing_for_sessions(self, active_sessions: set):
        """Adjust order routing based on active sessions"""
        await self.order_router.update_session_routing(active_sessions)
    
    async def process_cross_currency_orders(self):
        """Process orders requiring currency conversion"""
        while True:
            try:
                pending_orders = await self.db.get_pending_cross_currency_orders()
                
                for order in pending_orders:
                    await self.handle_cross_currency_order(order)
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error("Cross-currency processing error", error=str(e))
                await asyncio.sleep(30)
    
    async def handle_cross_currency_order(self, order: Dict[str, Any]):
        """Handle order requiring currency conversion"""
        try:
            # Get current FX rate
            fx_rate = await self.currency_converter.get_rate(
                order['base_currency'], 
                order['target_currency']
            )
            
            # Convert order amount
            converted_amount = order['amount'] * fx_rate
            
            # Update order with conversion details
            order['converted_amount'] = converted_amount
            order['fx_rate'] = fx_rate
            order['conversion_timestamp'] = datetime.utcnow()
            
            # Route to appropriate market
            await self.order_router.route_order(order)
            
            logger.info(f"Processed cross-currency order {order['order_id']}")
            
        except Exception as e:
            logger.error(f"Failed to process cross-currency order {order['order_id']}", error=str(e))

global_service = GlobalMarketService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await global_service.initialize()
    yield
    # Cleanup code here

app = FastAPI(
    title="VedhaVriddhi Global Market Service",
    description="Multi-currency, multi-market trading service",
    version="3.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "global-market-service",
        "version": "3.0.0",
        "active_sessions": list(global_service.active_sessions),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/orders/global")
async def place_global_order(order: GlobalOrder, background_tasks: BackgroundTasks):
    """Place a global cross-market order"""
    try:
        # Validate order
        validation_result = await global_service.order_router.validate_order(order)
        if not validation_result['valid']:
            raise HTTPException(status_code=400, detail=validation_result['errors'])
        
        # Check if currency conversion needed
        if await global_service.currency_converter.requires_conversion(order):
            background_tasks.add_task(global_service.handle_cross_currency_order, order.dict())
        else:
            background_tasks.add_task(global_service.order_router.route_order, order.dict())
        
        # Store order
        await global_service.db.store_order(order.dict())
        
        return {
            "order_id": order.order_id,
            "status": "accepted",
            "target_market": order.target_market,
            "currency": order.currency,
            "estimated_settlement": global_service.settlement_engine.estimate_settlement_time(order.target_market),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Order placement failed for {order.order_id}", error=str(e))
        raise HTTPException(status_code=500, detail="Order placement failed")

@app.get("/markets/active")
async def get_active_markets():
    """Get currently active global markets"""
    try:
        active_markets = await global_service.market_data.get_active_markets()
        return {
            "active_markets": active_markets,
            "active_sessions": list(global_service.active_sessions),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to get active markets", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve market data")

@app.get("/currency/rates")
async def get_currency_rates(base: Currency = Currency.USD):
    """Get current currency exchange rates"""
    try:
        rates = await global_service.currency_converter.get_all_rates(base)
        return {
            "base_currency": base,
            "rates": rates,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get currency rates for {base}", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve currency rates")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8100,
        reload=False,
        log_config=None
    )
