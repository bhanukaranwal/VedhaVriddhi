import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

import structlog
import uvicorn
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.var_engine import VaREngine
from core.stress_testing import StressTestingEngine
from core.limit_monitoring import LimitMonitoringEngine
from core.concentration_risk import ConcentrationRiskEngine
from database.risk_db import RiskDB
from database.timeseries_db import TimeSeriesDB
from config import Settings
from models import *

logger = structlog.get_logger()

class RiskService:
    def __init__(self):
        self.settings = Settings()
        self.var_engine = VaREngine(self.settings)
        self.stress_engine = StressTestingEngine(self.settings)
        self.limit_engine = LimitMonitoringEngine(self.settings)
        self.concentration_engine = ConcentrationRiskEngine(self.settings)
        self.risk_db = RiskDB(self.settings)
        self.timeseries_db = TimeSeriesDB(self.settings)
        self.running = False

    async def start(self):
        """Start risk management service"""
        logger.info("Starting Risk Management Service")
        
        try:
            await self.risk_db.initialize()
            await self.timeseries_db.initialize()
            await self.var_engine.initialize()
            await self.stress_engine.initialize()
            await self.limit_engine.initialize()
            
            # Start background processing
            asyncio.create_task(self.risk_monitoring_loop())
            asyncio.create_task(self.stress_testing_loop())
            asyncio.create_task(self.limit_checking_loop())
            
            self.running = True
            logger.info("Risk Service started successfully")
            
        except Exception as e:
            logger.error("Failed to start Risk Service", error=str(e))
            raise

    async def stop(self):
        """Stop risk service"""
        logger.info("Stopping Risk Service")
        self.running = False
        await self.risk_db.close()
        await self.timeseries_db.close()

    async def risk_monitoring_loop(self):
        """Main risk monitoring loop"""
        while self.running:
            try:
                # Calculate VaR for all portfolios
                await self.calculate_portfolio_vars()
                
                # Update concentration risk metrics
                await self.update_concentration_risks()
                
                # Calculate liquidity risk
                await self.assess_liquidity_risks()
                
                await asyncio.sleep(300)  # Every 5 minutes
                
            except Exception as e:
                logger.error("Risk monitoring error", error=str(e))
                await asyncio.sleep(60)

    async def stress_testing_loop(self):
        """Periodic stress testing"""
        while self.running:
            try:
                await self.run_stress_tests()
                await asyncio.sleep(3600)  # Every hour
                
            except Exception as e:
                logger.error("Stress testing error", error=str(e))
                await asyncio.sleep(600)

    async def limit_checking_loop(self):
        """Continuous limit monitoring"""
        while self.running:
            try:
                await self.check_all_limits()
                await asyncio.sleep(30)  # Every 30 seconds
                
            except Exception as e:
                logger.error("Limit checking error", error=str(e))
                await asyncio.sleep(60)

    async def calculate_portfolio_vars(self):
        """Calculate VaR for all portfolios"""
        try:
            portfolio_ids = await self.risk_db.get_active_portfolios()
            
            for portfolio_id in portfolio_ids:
                var_metrics = await self.var_engine.calculate_portfolio_var(portfolio_id)
                await self.risk_db.store_var_metrics(portfolio_id, var_metrics)
                
                # Check VaR limits
                if var_metrics['var_95'] > await self.get_var_limit(portfolio_id):
                    await self.trigger_risk_alert(portfolio_id, 'var_breach', var_metrics)
                    
        except Exception as e:
            logger.error("VaR calculation failed", error=str(e))

risk_service = RiskService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await risk_service.start()
    yield
    await risk_service.stop()

app = FastAPI(
    title="VedhaVriddhi Risk Management Service",
    description="Advanced risk analytics and monitoring",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Endpoints
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "risk-service",
        "version": "2.0.0",
        "running": risk_service.running
    }

@app.get("/risk/portfolio/{portfolio_id}")
async def get_portfolio_risk(portfolio_id: str):
    """Get comprehensive portfolio risk metrics"""
    try:
        risk_metrics = await risk_service.var_engine.calculate_portfolio_var(portfolio_id)
        concentration_metrics = await risk_service.concentration_engine.analyze_portfolio(portfolio_id)
        
        return {
            "portfolio_id": portfolio_id,
            "var_metrics": risk_metrics,
            "concentration_metrics": concentration_metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting portfolio risk for {portfolio_id}", error=str(e))
        raise HTTPException(status_code=500, detail="Risk calculation failed")

@app.post("/risk/stress-test")
async def run_stress_test(request: StressTestRequest):
    """Run stress test scenarios"""
    try:
        results = await risk_service.stress_engine.run_scenarios(
            request.portfolio_id,
            request.scenarios,
            request.confidence_level
        )
        return {"results": results}
    except Exception as e:
        logger.error("Stress test failed", error=str(e))
        raise HTTPException(status_code=500, detail="Stress test failed")

@app.get("/risk/limits/{portfolio_id}")
async def get_risk_limits(portfolio_id: str):
    """Get current risk limits and utilization"""
    try:
        limits = await risk_service.limit_engine.get_portfolio_limits(portfolio_id)
        return {"limits": limits}
    except Exception as e:
        logger.error(f"Error getting limits for {portfolio_id}", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get risk limits")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8004,
        log_config=None,
        access_log=False,
        reload=False
    )
