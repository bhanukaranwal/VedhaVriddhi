import asyncio
from typing import Dict, List, Optional
from datetime import datetime
from contextlib import asynccontextmanager

import structlog
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.agi_orchestrator import AGIOrchestrator
from core.financial_agi_agent import FinancialAGIAgent
from core.natural_language_interface import NaturalLanguageInterface
from models import *

logger = structlog.get_logger()

class AGIService:
    def __init__(self):
        self.orchestrator = AGIOrchestrator()
        self.nl_interface = NaturalLanguageInterface()
        self.active_agents = {}
        
    async def initialize(self):
        """Initialize AGI service"""
        logger.info("Initializing AGI Service")
        
        await self.orchestrator.initialize()
        await self.nl_interface.initialize()
        
        # Create specialized AGI agents
        self.active_agents['strategist'] = FinancialAGIAgent('strategist', 'strategy')
        self.active_agents['analyst'] = FinancialAGIAgent('analyst', 'analysis')
        self.active_agents['risk_manager'] = FinancialAGIAgent('risk_manager', 'risk')
        
        for agent in self.active_agents.values():
            await agent.initialize()
        
        logger.info(f"AGI Service initialized with {len(self.active_agents)} agents")

agi_service = AGIService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await agi_service.initialize()
    yield

app = FastAPI(
    title="VedhaVriddhi AGI Service",
    description="Artificial General Intelligence for finance",
    version="4.0.0",
    lifespan=lifespan
)

@app.post("/agi/analyze-market")
async def agi_market_analysis(request: MarketAnalysisRequest):
    """AGI-powered market analysis"""
    try:
        analysis = await agi_service.orchestrator.analyze_market_conditions(
            market_data=request.market_data,
            analysis_type=request.analysis_type,
            time_horizon=request.time_horizon
        )
        
        return {
            "market_outlook": analysis['outlook'],
            "recommended_actions": analysis['recommendations'],
            "confidence_level": analysis['confidence'],
            "reasoning": analysis['reasoning'],
            "risk_assessment": analysis['risk_factors'],
            "agent_consensus": analysis['consensus_level']
        }
        
    except Exception as e:
        logger.error("AGI market analysis failed", error=str(e))
        raise HTTPException(status_code=500, detail="AGI analysis failed")

@app.post("/agi/natural-language-query")
async def natural_language_query(request: NLQueryRequest):
    """Process natural language financial queries"""
    try:
        response = await agi_service.nl_interface.process_query(
            query=request.query,
            context=request.context,
            user_id=request.user_id
        )
        
        return {
            "interpretation": response['understood_intent'],
            "answer": response['response'],
            "confidence": response['confidence'],
            "suggested_actions": response['actions'],
            "follow_up_questions": response['follow_ups']
        }
        
    except Exception as e:
        logger.error("Natural language processing failed", error=str(e))
        raise HTTPException(status_code=500, detail="NL processing failed")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8201, reload=False)
