import asyncio
import logging
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

import structlog
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.analytics_engine import AnalyticsEngine
from core.ml_engine import MLEngine  
from core.yield_curve_engine import YieldCurveEngine
from core.risk_analytics import RiskAnalytics
from core.credit_analytics import CreditAnalytics
from core.performance_analytics import PerformanceAnalytics
from database.timeseries_db import TimeSeriesDB
from database.analytics_db import AnalyticsDB
from config import Settings
from models import *

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

class AnalyticsService:
    def __init__(self):
        self.settings = Settings()
        self.analytics_engine = AnalyticsEngine(self.settings)
        self.ml_engine = MLEngine(self.settings)
        self.yield_curve_engine = YieldCurveEngine(self.settings)
        self.risk_analytics = RiskAnalytics(self.settings)
        self.credit_analytics = CreditAnalytics(self.settings)
        self.performance_analytics = PerformanceAnalytics(self.settings)
        self.timeseries_db = TimeSeriesDB(self.settings)
        self.analytics_db = AnalyticsDB(self.settings)
        self.running = False

    async def start(self):
        """Initialize analytics service"""
        logger.info("Starting VedhaVriddhi Analytics Service")
        
        try:
            await self.timeseries_db.initialize()
            await self.analytics_db.initialize()
            await self.analytics_engine.initialize()
            await self.ml_engine.initialize()
            
            # Start background processing
            asyncio.create_task(self.process_analytics())
            asyncio.create_task(self.update_models())
            
            self.running = True
            logger.info("Analytics Service started successfully")
            
        except Exception as e:
            logger.error("Failed to start Analytics Service", error=str(e))
            raise

    async def stop(self):
        """Stop analytics service"""
        logger.info("Stopping Analytics Service")
        self.running = False
        
        await self.analytics_engine.stop()
        await self.ml_engine.stop()
        await self.timeseries_db.close()
        await self.analytics_db.close()
        
        logger.info("Analytics Service stopped")

    async def process_analytics(self):
        """Main analytics processing loop"""
        while self.running:
            try:
                # Process yield curves
                await self.yield_curve_engine.update_curves()
                
                # Update risk analytics
                await self.risk_analytics.calculate_portfolio_metrics()
                
                # Refresh credit analytics
                await self.credit_analytics.update_spreads()
                
                # Calculate performance metrics
                await self.performance_analytics.update_attribution()
                
                await asyncio.sleep(60)  # Process every minute
                
            except Exception as e:
                logger.error("Error in analytics processing", error=str(e))
                await asyncio.sleep(30)

    async def update_models(self):
        """Update ML models periodically"""
        while self.running:
            try:
                # Retrain models
                await self.ml_engine.retrain_models()
                
                await asyncio.sleep(3600)  # Retrain every hour
                
            except Exception as e:
                logger.error("Error in model updates", error=str(e))
                await asyncio.sleep(600)

# Global service instance
analytics_service = AnalyticsService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await analytics_service.start()
    yield
    # Shutdown
    await analytics_service.stop()

# FastAPI application
app = FastAPI(
    title="VedhaVriddhi Analytics Service",
    description="Advanced analytics and ML engine for bond trading",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
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
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "analytics-service",
        "version": "2.0.0",
        "running": analytics_service.running,
        "models_loaded": analytics_service.ml_engine.models_loaded
    }

@app.get("/yield-curve/{curve_type}")
async def get_yield_curve(curve_type: str, date: Optional[str] = None):
    """Get yield curve data"""
    try:
        curve_data = await analytics_service.yield_curve_engine.get_curve(curve_type, date)
        return {"curve_type": curve_type, "data": curve_data}
    
    except Exception as e:
        logger.error(f"Error getting yield curve {curve_type}", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get yield curve")

@app.get("/analytics/portfolio/{portfolio_id}")
async def get_portfolio_analytics(portfolio_id: str):
    """Get comprehensive portfolio analytics"""
    try:
        analytics = await analytics_service.analytics_engine.get_portfolio_analytics(portfolio_id)
        return analytics
    
    except Exception as e:
        logger.error(f"Error getting portfolio analytics for {portfolio_id}", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get portfolio analytics")

@app.post("/analytics/scenario-analysis")
async def scenario_analysis(request: ScenarioAnalysisRequest):
    """Run scenario analysis"""
    try:
        results = await analytics_service.risk_analytics.run_scenario_analysis(
            request.portfolio_id,
            request.scenarios
        )
        return {"results": results}
    
    except Exception as e:
        logger.error("Error in scenario analysis", error=str(e))
        raise HTTPException(status_code=500, detail="Scenario analysis failed")

@app.get("/analytics/attribution/{portfolio_id}")
async def get_performance_attribution(
    portfolio_id: str,
    start_date: str,
    end_date: str,
    benchmark: str = "NIFTY_GSEC"
):
    """Get performance attribution analysis"""
    try:
        attribution = await analytics_service.performance_analytics.calculate_attribution(
            portfolio_id, start_date, end_date, benchmark
        )
        return attribution
    
    except Exception as e:
        logger.error(f"Error in attribution analysis for {portfolio_id}", error=str(e))
        raise HTTPException(status_code=500, detail="Attribution analysis failed")

@app.get("/analytics/credit-spreads")
async def get_credit_spreads(
    sector: Optional[str] = None,
    rating: Optional[str] = None,
    maturity_bucket: Optional[str] = None
):
    """Get credit spread analysis"""
    try:
        spreads = await analytics_service.credit_analytics.get_spreads(
            sector, rating, maturity_bucket
        )
        return {"spreads": spreads}
    
    except Exception as e:
        logger.error("Error getting credit spreads", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get credit spreads")

@app.post("/ml/predict")
async def ml_prediction(request: MLPredictionRequest):
    """ML-powered predictions"""
    try:
        prediction = await analytics_service.ml_engine.predict(
            request.model_type,
            request.features,
            request.horizon
        )
        return {"prediction": prediction}
    
    except Exception as e:
        logger.error("Error in ML prediction", error=str(e))
        raise HTTPException(status_code=500, detail="ML prediction failed")

@app.get("/analytics/risk/{portfolio_id}")
async def get_risk_analytics(portfolio_id: str):
    """Get comprehensive risk analytics"""
    try:
        risk_metrics = await analytics_service.risk_analytics.calculate_risk_metrics(portfolio_id)
        return risk_metrics
    
    except Exception as e:
        logger.error(f"Error calculating risk for {portfolio_id}", error=str(e))
        raise HTTPException(status_code=500, detail="Risk calculation failed")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8003,
        log_config=None,
        access_log=False,
        reload=False
    )
