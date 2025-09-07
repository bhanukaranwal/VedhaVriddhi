import asyncio
from contextlib import asynccontextmanager
from typing import Dict, List, Optional
from datetime import datetime

import structlog
import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from core.mobile_auth import MobileAuthService
from core.portfolio_mobile import MobilePortfolioService
from core.trading_mobile import MobileTradingService
from models import *

logger = structlog.get_logger()

class MobileAPIService:
    def __init__(self):
        self.auth_service = MobileAuthService()
        self.portfolio_service = MobilePortfolioService()
        self.trading_service = MobileTradingService()
        
    async def initialize(self):
        """Initialize mobile API service"""
        logger.info("Initializing Mobile API Service")
        
        await self.auth_service.initialize()
        await self.portfolio_service.initialize()
        await self.trading_service.initialize()
        
        logger.info("Mobile API Service initialized successfully")

mobile_api = MobileAPIService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await mobile_api.initialize()
    yield

app = FastAPI(
    title="VedhaVriddhi Mobile API Service",
    description="Mobile-optimized trading API",
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
        "service": "mobile-api-service",
        "version": "3.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/portfolio/{portfolio_id}/summary")
async def get_portfolio_summary(portfolio_id: str) -> PortfolioSummary:
    """Get mobile-optimized portfolio summary"""
    try:
        summary = await mobile_api.portfolio_service.get_summary(portfolio_id)
        return summary
        
    except Exception as e:
        logger.error(f"Failed to get portfolio summary for {portfolio_id}", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve portfolio summary")

@app.get("/portfolio/{portfolio_id}/positions")
async def get_portfolio_positions(portfolio_id: str, limit: int = 50) -> List[MobilePosition]:
    """Get mobile-optimized position list"""
    try:
        positions = await mobile_api.portfolio_service.get_positions(portfolio_id, limit)
        return positions
        
    except Exception as e:
        logger.error(f"Failed to get positions for {portfolio_id}", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve positions")

@app.get("/watchlist/{user_id}")
async def get_watchlist(user_id: str) -> List[WatchlistItem]:
    """Get user's watchlist"""
    try:
        watchlist = await mobile_api.portfolio_service.get_watchlist(user_id)
        return watchlist
        
    except Exception as e:
        logger.error(f"Failed to get watchlist for {user_id}", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve watchlist")

@app.post("/orders/quick")
async def quick_order(order: QuickOrderRequest) -> OrderResponse:
    """Submit quick trading order"""
    try:
        result = await mobile_api.trading_service.submit_quick_order(order)
        return result
        
    except Exception as e:
        logger.error(f"Quick order failed for {order.symbol}", error=str(e))
        raise HTTPException(status_code=500, detail="Order submission failed")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8105,
        reload=False
    )
