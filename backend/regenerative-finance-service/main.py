import asyncio
from contextlib import asynccontextmanager
from typing import Dict, List, Optional
from decimal import Decimal

import structlog
import uvicorn
from fastapi import FastAPI, HTTPException

from core.regenerative_economics import RegenerativeEconomicsEngine
from core.circular_finance import CircularFinanceSystem
from core.ecosystem_restoration import EcosystemRestorationFinancing
from core.abundance_creation import AbundanceCreationEngine
from models import *

logger = structlog.get_logger()

class RegenerativeFinanceService:
    def __init__(self):
        self.regenerative_economics = RegenerativeEconomicsEngine()
        self.circular_finance = CircularFinanceSystem()
        self.ecosystem_restoration = EcosystemRestorationFinancing()
        self.abundance_creation = AbundanceCreationEngine()
        self.regeneration_projects = {}
        
    async def initialize(self):
        """Initialize Regenerative Finance Service"""
        logger.info("Initializing Planetary Regenerative Finance Service")
        
        await self.regenerative_economics.initialize()
        await self.circular_finance.initialize()
        await self.ecosystem_restoration.initialize()
        await self.abundance_creation.initialize()
        
        # Start regenerative monitoring
        asyncio.create_task(self.monitor_planetary_regeneration())
        asyncio.create_task(self.optimize_circular_flows())
        asyncio.create_task(self.scale_abundance_creation())
        
        logger.info("Regenerative Finance Service initialized successfully")

regenerative_service = RegenerativeFinanceService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await regenerative_service.initialize()
    yield

app = FastAPI(
    title="VedhaVriddhi Regenerative Finance Service",
    description="Planetary regeneration through conscious finance",
    version="4.2.0",
    lifespan=lifespan
)

@app.post("/regenerative/create-restoration-project")
async def create_ecosystem_restoration_project(request: EcosystemRestorationRequest):
    """Create ecosystem restoration financing project"""
    try:
        project = await regenerative_service.ecosystem_restoration.create_project(
            ecosystem_type=request.ecosystem_type,
            restoration_scope=request.scope,
            funding_requirements=request.funding_needed,
            impact_metrics=request.expected_outcomes,
            regeneration_timeline=request.timeline
        )
        
        regenerative_service.regeneration_projects[project['project_id']] = project
        
        return {
            "project_id": project['project_id'],
            "ecosystem_type": project['ecosystem_type'],
            "funding_allocated": project['funding_amount'],
            "expected_carbon_sequestration": project['carbon_impact'],
            "biodiversity_restoration": project['biodiversity_metrics'],
            "community_benefits": project['social_impact'],
            "roi_planetary_health": project['planetary_roi']
        }
        
    except Exception as e:
        logger.error("Restoration project creation failed", error=str(e))
        raise HTTPException(status_code=500, detail="Project creation failed")

@app.post("/regenerative/circular-economy-optimization")
async def optimize_circular_economy_flows(request: CircularEconomyRequest):
    """Optimize circular economy financial flows"""
    try:
        optimization_result = await regenerative_service.circular_finance.optimize_flows(
            resource_streams=request.resource_flows,
            waste_transformation=request.waste_to_value_pathways,
            regenerative_loops=request.regeneration_cycles,
            stakeholder_network=request.stakeholders
        )
        
        return {
            "optimization_id": optimization_result['optimization_id'],
            "waste_elimination_percentage": optimization_result['waste_reduction'],
            "resource_efficiency_gain": optimization_result['efficiency_improvement'],
            "value_creation_multiplier": optimization_result['value_multiplier'],
            "regeneration_rate": optimization_result['regeneration_velocity'],
            "circular_economy_score": optimization_result['circularity_index']
        }
        
    except Exception as e:
        logger.error("Circular economy optimization failed", error=str(e))
        raise HTTPException(status_code=500, detail="Optimization failed")

@app.get("/regenerative/abundance-metrics")
async def get_abundance_creation_metrics():
    """Get abundance creation metrics"""
    try:
        abundance_data = await regenerative_service.abundance_creation.get_comprehensive_metrics()
        
        return {
            "total_abundance_created": abundance_data['total_abundance_value'],
            "resource_multiplication_factor": abundance_data['multiplication_factor'],
            "scarcity_elimination_progress": abundance_data['scarcity_reduction'],
            "post_scarcity_indicators": abundance_data['post_scarcity_metrics'],
            "collective_prosperity_index": abundance_data['prosperity_index'],
            "planetary_wellbeing_score": abundance_data['wellbeing_score']
        }
        
    except Exception as e:
        logger.error("Failed to get abundance metrics", error=str(e))
        raise HTTPException(status_code=500, detail="Abundance metrics retrieval failed")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8218, reload=False)
