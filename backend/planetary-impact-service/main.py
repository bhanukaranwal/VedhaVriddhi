import asyncio
from contextlib import asynccontextmanager
from typing import Dict, List, Optional
from datetime import datetime
from decimal import Decimal

import structlog
import uvicorn
from fastapi import FastAPI, HTTPException

from core.planetary_health_monitor import PlanetaryHealthMonitor
from core.ecosystem_optimizer import EcosystemOptimizer
from core.regenerative_finance import RegenerativeFinanceEngine
from core.gaian_intelligence import GaianIntelligenceSystem
from models import *

logger = structlog.get_logger()

class PlanetaryImpactService:
    def __init__(self):
        self.planetary_monitor = PlanetaryHealthMonitor()
        self.ecosystem_optimizer = EcosystemOptimizer()
        self.regenerative_engine = RegenerativeFinanceEngine()
        self.gaian_intelligence = GaianIntelligenceSystem()
        self.planetary_health_score = 0.0
        
    async def initialize(self):
        """Initialize Planetary Impact Optimization Service"""
        logger.info("Initializing Planetary Impact Optimization Service")
        
        await self.planetary_monitor.initialize()
        await self.ecosystem_optimizer.initialize()
        await self.regenerative_engine.initialize()
        await self.gaian_intelligence.initialize()
        
        # Start planetary monitoring
        asyncio.create_task(self.monitor_planetary_health())
        asyncio.create_task(self.optimize_ecosystem_impact())
        asyncio.create_task(self.enhance_regenerative_flows())
        
        logger.info("Planetary Impact Service initialized successfully")
    
    async def monitor_planetary_health(self):
        """Monitor global planetary health indicators"""
        while True:
            try:
                health_data = await self.planetary_monitor.assess_global_health()
                
                self.planetary_health_score = health_data['overall_score']
                
                # Trigger interventions if health declining
                if health_data['trend'] == 'declining':
                    await self._initiate_planetary_healing_protocols()
                
                await asyncio.sleep(3600)  # Monitor every hour
                
            except Exception as e:
                logger.error("Planetary health monitoring error", error=str(e))
                await asyncio.sleep(1800)

planetary_impact_service = PlanetaryImpactService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await planetary_impact_service.initialize()
    yield

app = FastAPI(
    title="VedhaVriddhi Planetary Impact Service",
    description="Planetary health optimization and regenerative finance",
    version="4.0.0",
    lifespan=lifespan
)

@app.get("/planetary/health-score")
async def get_planetary_health_score():
    """Get current planetary health score"""
    try:
        health_data = await planetary_impact_service.planetary_monitor.get_comprehensive_score()
        
        return {
            "overall_health_score": health_data['overall_score'],
            "climate_stability": health_data['climate_score'],
            "biodiversity_index": health_data['biodiversity_score'],
            "ocean_health": health_data['ocean_score'],
            "atmospheric_quality": health_data['atmosphere_score'],
            "soil_health": health_data['soil_score'],
            "regeneration_rate": health_data['regeneration_rate'],
            "improvement_trends": health_data['trends']
        }
        
    except Exception as e:
        logger.error("Failed to get planetary health score", error=str(e))
        raise HTTPException(status_code=500, detail="Health score retrieval failed")

@app.post("/planetary/optimize-impact")
async def optimize_planetary_impact(request: PlanetaryOptimizationRequest):
    """Optimize financial decisions for planetary impact"""
    try:
        optimization_result = await planetary_impact_service.ecosystem_optimizer.optimize(
            portfolio=request.portfolio,
            impact_objectives=request.objectives,
            planetary_constraints=request.constraints
        )
        
        return {
            "optimized_allocation": optimization_result['allocation'],
            "projected_impact": optimization_result['impact_projection'],
            "regenerative_potential": optimization_result['regenerative_score'],
            "planetary_benefit": optimization_result['planetary_benefit'],
            "consciousness_alignment": optimization_result['consciousness_score']
        }
        
    except Exception as e:
        logger.error("Planetary impact optimization failed", error=str(e))
        raise HTTPException(status_code=500, detail="Impact optimization failed")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8212, reload=False)
