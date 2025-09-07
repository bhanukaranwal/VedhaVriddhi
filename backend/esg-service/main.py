import asyncio
from contextlib import asynccontextmanager
from typing import Dict, List, Optional
from datetime import datetime

import structlog
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from core.esg_analyzer import ESGAnalyzer
from core.sustainability_tracker import SustainabilityTracker
from core.green_bonds import GreenBondService
from models import *

logger = structlog.get_logger()

class ESGService:
    def __init__(self):
        self.esg_analyzer = ESGAnalyzer()
        self.sustainability_tracker = SustainabilityTracker()
        self.green_bonds = GreenBondService()
        
    async def initialize(self):
        """Initialize ESG service"""
        logger.info("Initializing ESG Service")
        
        await self.esg_analyzer.initialize()
        await self.sustainability_tracker.initialize()
        await self.green_bonds.initialize()
        
        logger.info("ESG Service initialized successfully")

esg_service = ESGService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await esg_service.initialize()
    yield

app = FastAPI(
    title="VedhaVriddhi ESG Service",
    description="Environmental, Social, and Governance analytics",
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
        "service": "esg-service",
        "version": "3.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/instrument/{instrument_id}/esg")
async def get_instrument_esg(instrument_id: str) -> ESGScore:
    """Get ESG score for specific instrument"""
    try:
        esg_score = await esg_service.esg_analyzer.get_esg_score(instrument_id)
        return esg_score
        
    except Exception as e:
        logger.error(f"Failed to get ESG score for {instrument_id}", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve ESG score")

@app.get("/portfolio/{portfolio_id}/esg")
async def get_portfolio_esg(portfolio_id: str) -> PortfolioESGSummary:
    """Get ESG summary for portfolio"""
    try:
        esg_summary = await esg_service.esg_analyzer.analyze_portfolio(portfolio_id)
        return esg_summary
        
    except Exception as e:
        logger.error(f"Failed to get portfolio ESG for {portfolio_id}", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve portfolio ESG")

@app.get("/green-bonds")
async def get_green_bonds(
    min_rating: Optional[str] = None,
    max_maturity_years: Optional[int] = None
) -> List[GreenBond]:
    """Get available green bonds"""
    try:
        green_bonds = await esg_service.green_bonds.get_available_bonds(
            min_rating, max_maturity_years
        )
        return green_bonds
        
    except Exception as e:
        logger.error("Failed to get green bonds", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve green bonds")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8106,
        reload=False
    )
