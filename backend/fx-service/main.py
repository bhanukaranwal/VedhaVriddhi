import asyncio
from contextlib import asynccontextmanager
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal

import structlog
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from core.fx_aggregator import FXRateAggregator
from core.hedging_engine import HedgingEngine
from database.fx_db import FXDB
from models import *

logger = structlog.get_logger()

class FXQuote(BaseModel):
    base_currency: str = Field(..., description="Base currency code")
    quote_currency: str = Field(..., description="Quote currency code")
    bid_rate: Decimal = Field(..., description="Bid exchange rate")
    ask_rate: Decimal = Field(..., description="Ask exchange rate")
    mid_rate: Decimal = Field(..., description="Mid market rate")
    spread_bps: int = Field(..., description="Bid-ask spread in basis points")
    liquidity: Decimal = Field(..., description="Available liquidity")
    provider: str = Field(..., description="Rate provider")
    timestamp: datetime = Field(..., description="Quote timestamp")

class FXConversionRequest(BaseModel):
    from_currency: str = Field(..., description="Source currency")
    to_currency: str = Field(..., description="Target currency")
    amount: Decimal = Field(..., description="Amount to convert")
    execution_type: str = Field(default="mid", description="mid, bid, ask")

class FXService:
    def __init__(self):
        self.fx_aggregator = FXRateAggregator()
        self.hedging_engine = HedgingEngine()
        self.db = FXDB()
        self.current_rates = {}
        
    async def initialize(self):
        """Initialize FX service"""
        logger.info("Initializing FX Service")
        
        try:
            await self.db.initialize()
            await self.fx_aggregator.initialize()
            await self.hedging_engine.initialize()
            
            # Start rate streaming
            asyncio.create_task(self.stream_fx_rates())
            asyncio.create_task(self.monitor_hedging_positions())
            
            logger.info("FX Service initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize FX Service", error=str(e))
            raise
    
    async def stream_fx_rates(self):
        """Stream real-time FX rates from multiple providers"""
        while True:
            try:
                # Get rates from all providers
                new_rates = await self.fx_aggregator.get_all_rates()
                
                # Update current rates
                for currency_pair, quote in new_rates.items():
                    self.current_rates[currency_pair] = quote
                    
                # Store in database
                await self.db.store_rates(new_rates)
                
                await asyncio.sleep(1)  # Update every second
                
            except Exception as e:
                logger.error("Rate streaming error", error=str(e))
                await asyncio.sleep(5)
    
    async def monitor_hedging_positions(self):
        """Monitor and manage FX hedging positions"""
        while True:
            try:
                # Check current exposures
                exposures = await self.db.get_net_exposures()
                
                # Generate hedging recommendations
                hedging_orders = await self.hedging_engine.generate_hedges(exposures)
                
                # Execute hedges if needed
                for hedge_order in hedging_orders:
                    await self.execute_hedge(hedge_order)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error("Hedging monitoring error", error=str(e))
                await asyncio.sleep(30)
    
    async def execute_hedge(self, hedge_order: Dict):
        """Execute FX hedge order"""
        try:
            # Implementation would execute hedge via FX providers
            logger.info(f"Executing hedge: {hedge_order}")
            
        except Exception as e:
            logger.error("Hedge execution failed", error=str(e))

fx_service = FXService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await fx_service.initialize()
    yield

app = FastAPI(
    title="VedhaVriddhi FX Service", 
    description="Professional foreign exchange service",
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
    return {
        "status": "healthy",
        "service": "fx-service",
        "version": "3.0.0",
        "active_pairs": len(fx_service.current_rates),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/rates")
async def get_current_rates(base_currency: str = "USD"):
    """Get current FX rates for base currency"""
    try:
        relevant_rates = {
            pair: quote for pair, quote in fx_service.current_rates.items()
            if pair.startswith(base_currency)
        }
        
        return {
            "base_currency": base_currency,
            "rates": relevant_rates,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get rates for {base_currency}", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve rates")

@app.post("/convert")
async def convert_currency(request: FXConversionRequest):
    """Convert currency amount at current market rates"""
    try:
        currency_pair = f"{request.from_currency}/{request.to_currency}"
        
        if currency_pair not in fx_service.current_rates:
            # Try reverse pair
            reverse_pair = f"{request.to_currency}/{request.from_currency}"
            if reverse_pair in fx_service.current_rates:
                quote = fx_service.current_rates[reverse_pair]
                rate = 1 / quote['mid_rate'] if request.execution_type == 'mid' else 1 / quote['ask_rate']
            else:
                raise HTTPException(status_code=404, detail="Currency pair not available")
        else:
            quote = fx_service.current_rates[currency_pair]
            if request.execution_type == 'mid':
                rate = quote['mid_rate']
            elif request.execution_type == 'bid':
                rate = quote['bid_rate']
            else:  # ask
                rate = quote['ask_rate']
        
        converted_amount = request.amount * rate
        
        return {
            "from_currency": request.from_currency,
            "to_currency": request.to_currency,
            "original_amount": request.amount,
            "converted_amount": converted_amount,
            "exchange_rate": rate,
            "execution_type": request.execution_type,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Currency conversion failed", error=str(e))
        raise HTTPException(status_code=500, detail="Conversion failed")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0", 
        port=8101,
        reload=False
    )
