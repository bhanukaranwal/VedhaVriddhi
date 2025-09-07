import asyncio
from contextlib import asynccontextmanager
from typing import Dict, List, Optional
from datetime import datetime, timedelta

import structlog
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from core.smart_contracts import SmartContractEngine
from core.settlement_engine import BlockchainSettlementEngine
from core.tokenization import TokenizationService
from database.blockchain_db import BlockchainDB
from models import *

logger = structlog.get_logger()

class BlockchainService:
    def __init__(self):
        self.settings = Settings()
        self.smart_contracts = SmartContractEngine(self.settings)
        self.settlement_engine = BlockchainSettlementEngine(self.settings)
        self.tokenization = TokenizationService(self.settings)
        self.db = BlockchainDB(self.settings)
        self.active_networks = set()
        
    async def initialize(self):
        """Initialize blockchain service"""
        logger.info("Initializing Blockchain Service")
        
        try:
            await self.db.initialize()
            await self.smart_contracts.initialize()
            await self.settlement_engine.initialize()
            await self.tokenization.initialize()
            
            # Start blockchain monitoring
            asyncio.create_task(self.monitor_networks())
            asyncio.create_task(self.process_settlements())
            
            self.active_networks = {'ethereum', 'polygon', 'hyperledger'}
            
            logger.info("Blockchain Service initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize Blockchain Service", error=str(e))
            raise
    
    async def monitor_networks(self):
        """Monitor blockchain network status"""
        while True:
            try:
                # Check network connectivity and status
                network_status = await self._check_network_status()
                
                for network, status in network_status.items():
                    if not status['healthy']:
                        logger.warning(f"Network {network} unhealthy: {status}")
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error("Network monitoring error", error=str(e))
                await asyncio.sleep(30)
    
    async def process_settlements(self):
        """Process pending settlements"""
        while True:
            try:
                pending_settlements = await self.db.get_pending_settlements()
                
                for settlement in pending_settlements:
                    await self.settlement_engine.process_settlement(settlement)
                
                await asyncio.sleep(30)  # Process every 30 seconds
                
            except Exception as e:
                logger.error("Settlement processing error", error=str(e))
                await asyncio.sleep(60)
    
    async def _check_network_status(self) -> Dict[str, Dict]:
        """Check status of blockchain networks"""
        # Mock implementation - would check actual networks
        return {
            'ethereum': {'healthy': True, 'block_height': 18500000, 'gas_price': 25},
            'polygon': {'healthy': True, 'block_height': 50000000, 'gas_price': 30},
            'hyperledger': {'healthy': True, 'peers': 5, 'channels': 3}
        }

blockchain_service = BlockchainService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await blockchain_service.initialize()
    yield

app = FastAPI(
    title="VedhaVriddhi Blockchain Service",
    description="Blockchain integration and smart contract service",
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
        "service": "blockchain-service",
        "version": "3.0.0",
        "active_networks": list(blockchain_service.active_networks),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/settlement/create")
async def create_settlement(settlement_request: SettlementRequest, background_tasks: BackgroundTasks):
    """Create blockchain settlement"""
    try:
        settlement_id = await blockchain_service.settlement_engine.create_settlement(settlement_request)
        
        background_tasks.add_task(
            blockchain_service.settlement_engine.process_settlement_async,
            settlement_id
        )
        
        return {
            "settlement_id": settlement_id,
            "status": "created",
            "estimated_completion": (datetime.utcnow() + timedelta(minutes=5)).isoformat(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Settlement creation failed", error=str(e))
        raise HTTPException(status_code=500, detail="Settlement creation failed")

@app.get("/settlement/{settlement_id}")
async def get_settlement_status(settlement_id: str):
    """Get settlement status"""
    try:
        settlement = await blockchain_service.db.get_settlement(settlement_id)
        
        if not settlement:
            raise HTTPException(status_code=404, detail="Settlement not found")
        
        return settlement
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get settlement {settlement_id}", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve settlement")

@app.post("/contracts/deploy")
async def deploy_smart_contract(contract_request: SmartContractRequest):
    """Deploy smart contract"""
    try:
        contract_address = await blockchain_service.smart_contracts.deploy_contract(contract_request)
        
        return {
            "contract_address": contract_address,
            "network": contract_request.network,
            "status": "deployed",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Smart contract deployment failed", error=str(e))
        raise HTTPException(status_code=500, detail="Contract deployment failed")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8103,
        reload=False
    )
