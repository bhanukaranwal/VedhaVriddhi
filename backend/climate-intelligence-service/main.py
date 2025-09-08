import asyncio
from contextlib import asynccontextmanager
from typing import Dict, List, Optional
from datetime import datetime
from decimal import Decimal

import structlog
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from core.carbon_accounting import CarbonAccountingEngine
from core.biodiversity_tracker import BiodiversityTracker
from core.climate_risk_analyzer import ClimateRiskAnalyzer
from core.renewable_energy_trader import RenewableEnergyTrader
from models import *

logger = structlog.get_logger()

class ClimateIntelligenceService:
    def __init__(self):
        self.carbon_accounting = CarbonAccountingEngine()
        self.biodiversity_tracker = BiodiversityTracker()
        self.climate_risk_analyzer = ClimateRiskAnalyzer()
        self.renewable_trader = RenewableEnergyTrader()
        self.carbon_negative_target = True
        
    async def initialize(self):
        """Initialize Climate Intelligence Service"""
        logger.info("Initializing Climate Intelligence Service")
        
        try:
            await self.carbon_accounting.initialize()
            await self.biodiversity_tracker.initialize()
            await self.climate_risk_analyzer.initialize()
            await self.renewable_trader.initialize()
            
            # Start real-time monitoring
            asyncio.create_task(self.monitor_carbon_footprint())
            asyncio.create_task(self.track_biodiversity_impact())
            asyncio.create_task(self.analyze_climate_risks())
            
            logger.info("Climate Intelligence Service initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize Climate Intelligence Service", error=str(e))
            raise
    
    async def monitor_carbon_footprint(self):
        """Continuously monitor and optimize carbon footprint"""
        while True:
            try:
                # Calculate current carbon footprint
                current_footprint = await self.carbon_accounting.calculate_total_footprint()
                
                # If not carbon negative, purchase offsets
                if current_footprint > 0:
                    offset_amount = current_footprint * 1.1  # 110% to be carbon negative
                    await self.carbon_accounting.purchase_carbon_offsets(offset_amount)
                
                # Update carbon negative status
                net_footprint = await self.carbon_accounting.get_net_footprint()
                self.carbon_negative_target = net_footprint < 0
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error("Carbon footprint monitoring error", error=str(e))
                await asyncio.sleep(600)
    
    async def track_biodiversity_impact(self):
        """Track and improve biodiversity impact"""
        while True:
            try:
                # Assess current biodiversity impact
                impact_assessment = await self.biodiversity_tracker.assess_portfolio_impact()
                
                # If negative impact, invest in biodiversity restoration
                if impact_assessment['net_impact'] < 0:
                    restoration_investment = abs(impact_assessment['net_impact']) * 1000  # USD per impact unit
                    await self.biodiversity_tracker.invest_in_restoration(restoration_investment)
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                logger.error("Biodiversity tracking error", error=str(e))
                await asyncio.sleep(1800)
    
    async def analyze_climate_risks(self):
        """Analyze climate risks across portfolios"""
        while True:
            try:
                # Run comprehensive climate risk analysis
                risk_analysis = await self.climate_risk_analyzer.analyze_all_portfolios()
                
                # Generate risk mitigation recommendations
                mitigation_strategies = await self.climate_risk_analyzer.generate_mitigation_strategies(
                    risk_analysis
                )
                
                # Automatically implement low-risk strategies
                for strategy in mitigation_strategies:
                    if strategy['risk_level'] == 'low' and strategy['auto_implement']:
                        await self._implement_mitigation_strategy(strategy)
                
                await asyncio.sleep(1800)  # Analyze every 30 minutes
                
            except Exception as e:
                logger.error("Climate risk analysis error", error=str(e))
                await asyncio.sleep(3600)

climate_service = ClimateIntelligenceService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await climate_service.initialize()
    yield

app = FastAPI(
    title="VedhaVriddhi Climate Intelligence Service",
    description="Advanced climate and sustainability analytics",
    version="4.0.0",
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
        "service": "climate-intelligence-service",
        "version": "4.0.0",
        "carbon_negative": climate_service.carbon_negative_target,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/carbon/footprint")
async def get_carbon_footprint():
    """Get current carbon footprint analysis"""
    try:
        footprint_data = await climate_service.carbon_accounting.get_detailed_footprint()
        return {
            "total_emissions_tons_co2": footprint_data['total_emissions'],
            "offset_tons_co2": footprint_data['total_offsets'],
            "net_emissions_tons_co2": footprint_data['net_emissions'],
            "carbon_negative": footprint_data['net_emissions'] < 0,
            "breakdown_by_activity": footprint_data['activity_breakdown'],
            "offset_projects": footprint_data['offset_projects'],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to get carbon footprint", error=str(e))
        raise HTTPException(status_code=500, detail="Carbon footprint analysis failed")

@app.get("/biodiversity/impact")
async def get_biodiversity_impact():
    """Get biodiversity impact assessment"""
    try:
        impact_data = await climate_service.biodiversity_tracker.get_comprehensive_impact()
        return {
            "overall_impact_score": impact_data['overall_score'],
            "ecosystem_impacts": impact_data['ecosystem_breakdown'],
            "species_affected": impact_data['species_count'],
            "restoration_investments": impact_data['restoration_projects'],
            "net_biodiversity_benefit": impact_data['net_benefit'],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to get biodiversity impact", error=str(e))
        raise HTTPException(status_code=500, detail="Biodiversity impact analysis failed")

@app.post("/climate/risk-assessment")
async def assess_climate_risk(risk_request: ClimateRiskRequest):
    """Assess climate risk for specific portfolio or instrument"""
    try:
        risk_analysis = await climate_service.climate_risk_analyzer.assess_specific_risk(
            asset_id=risk_request.asset_id,
            time_horizon=risk_request.time_horizon,
            scenarios=risk_request.scenarios
        )
        
        return {
            "asset_id": risk_request.asset_id,
            "physical_risk_score": risk_analysis['physical_risk'],
            "transition_risk_score": risk_analysis['transition_risk'],
            "overall_climate_risk": risk_analysis['overall_risk'],
            "risk_factors": risk_analysis['key_factors'],
            "mitigation_recommendations": risk_analysis['recommendations'],
            "confidence_level": risk_analysis['confidence'],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Climate risk assessment failed", error=str(e))
        raise HTTPException(status_code=500, detail="Climate risk assessment failed")

@app.get("/renewable-energy/opportunities")
async def get_renewable_energy_opportunities():
    """Get renewable energy investment opportunities"""
    try:
        opportunities = await climate_service.renewable_trader.get_investment_opportunities()
        return {
            "opportunities": opportunities,
            "total_projects": len(opportunities),
            "total_capacity_mw": sum(opp['capacity_mw'] for opp in opportunities),
            "average_roi": sum(opp['expected_roi'] for opp in opportunities) / len(opportunities),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to get renewable energy opportunities", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve opportunities")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8109,
        reload=False
    )
