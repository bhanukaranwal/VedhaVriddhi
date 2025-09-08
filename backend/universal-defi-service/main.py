import asyncio
from contextlib import asynccontextmanager
from typing import Dict, List, Optional
from datetime import datetime
from decimal import Decimal

import structlog
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from core.defi_aggregator import DeFiLiquidityAggregator
from core.cbdc_integration import CBDCIntegrationService
from core.cross_chain_bridge import CrossChainBridge
from core.yield_optimizer import YieldOptimizer
from models import *

logger = structlog.get_logger()

class UniversalDeFiService:
    def __init__(self):
        self.defi_aggregator = DeFiLiquidityAggregator()
        self.cbdc_service = CBDCIntegrationService()
        self.cross_chain_bridge = CrossChainBridge()
        self.yield_optimizer = YieldOptimizer()
        self.active_protocols = set()
        
    async def initialize(self):
        """Initialize Universal DeFi Service"""
        logger.info("Initializing Universal DeFi Service")
        
        try:
            await self.defi_aggregator.initialize()
            await self.cbdc_service.initialize()
            await self.cross_chain_bridge.initialize()
            await self.yield_optimizer.initialize()
            
            # Connect to major DeFi protocols
            protocols = ['uniswap', 'compound', 'aave', 'curve', 'balancer', 'makerdao']
            for protocol in protocols:
                await self._connect_protocol(protocol)
                self.active_protocols.add(protocol)
            
            # Start background services
            asyncio.create_task(self.monitor_liquidity())
            asyncio.create_task(self.optimize_yields())
            asyncio.create_task(self.sync_cbdc_rates())
            
            logger.info(f"Universal DeFi Service initialized with {len(self.active_protocols)} protocols")
            
        except Exception as e:
            logger.error("Failed to initialize Universal DeFi Service", error=str(e))
            raise
    
    async def _connect_protocol(self, protocol_name: str):
        """Connect to specific DeFi protocol"""
        connection_config = {
            'uniswap': {'network': 'ethereum', 'version': 'v3'},
            'compound': {'network': 'ethereum', 'version': 'v3'},
            'aave': {'network': 'ethereum', 'version': 'v3'},
            'curve': {'network': 'ethereum', 'version': 'stable'},
            'balancer': {'network': 'ethereum', 'version': 'v2'},
            'makerdao': {'network': 'ethereum', 'version': 'multi-collateral'}
        }
        
        config = connection_config.get(protocol_name, {})
        await self.defi_aggregator.connect_protocol(protocol_name, config)
        logger.info(f"Connected to {protocol_name}")
    
    async def monitor_liquidity(self):
        """Monitor liquidity across DeFi protocols"""
        while True:
            try:
                liquidity_data = await self.defi_aggregator.get_global_liquidity()
                
                # Analyze liquidity conditions
                liquidity_analysis = await self._analyze_liquidity(liquidity_data)
                
                # Adjust routing based on liquidity
                await self._adjust_routing(liquidity_analysis)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error("Liquidity monitoring error", error=str(e))
                await asyncio.sleep(60)
    
    async def optimize_yields(self):
        """Continuously optimize yield strategies"""
        while True:
            try:
                # Get current yield opportunities
                yield_opportunities = await self.yield_optimizer.scan_opportunities()
                
                # Optimize allocation across protocols
                optimal_allocation = await self.yield_optimizer.optimize_allocation(
                    yield_opportunities
                )
                
                # Execute rebalancing if needed
                if optimal_allocation['rebalance_needed']:
                    await self._execute_rebalancing(optimal_allocation)
                
                await asyncio.sleep(300)  # Optimize every 5 minutes
                
            except Exception as e:
                logger.error("Yield optimization error", error=str(e))
                await asyncio.sleep(600)
    
    async def sync_cbdc_rates(self):
        """Synchronize CBDC exchange rates"""
        while True:
            try:
                # Get latest CBDC rates from central banks
                cbdc_rates = await self.cbdc_service.fetch_all_rates()
                
                # Update internal rate cache
                await self.cbdc_service.update_rate_cache(cbdc_rates)
                
                await asyncio.sleep(60)  # Update every minute
                
            except Exception as e:
                logger.error("CBDC rate sync error", error=str(e))
                await asyncio.sleep(300)
    
    async def _analyze_liquidity(self, liquidity_data: Dict) -> Dict:
        """Analyze current liquidity conditions"""
        total_liquidity = sum(pool['liquidity'] for pool in liquidity_data.values())
        
        return {
            'total_liquidity_usd': total_liquidity,
            'protocol_distribution': {
                protocol: data['liquidity'] / total_liquidity 
                for protocol, data in liquidity_data.items()
            },
            'liquidity_score': min(1.0, total_liquidity / 10**9),  # Normalize to 1B
            'fragmentation_score': len(liquidity_data) / 10  # More protocols = more fragmentation
        }
    
    async def _adjust_routing(self, liquidity_analysis: Dict):
        """Adjust routing based on liquidity analysis"""
        # Update routing weights based on liquidity
        for protocol, weight in liquidity_analysis['protocol_distribution'].items():
            await self.defi_aggregator.update_protocol_weight(protocol, weight)
    
    async def _execute_rebalancing(self, allocation: Dict):
        """Execute portfolio rebalancing across protocols"""
        logger.info("Executing DeFi yield rebalancing")
        
        # Execute rebalancing transactions
        for protocol, target_allocation in allocation['targets'].items():
            current_allocation = allocation['current'].get(protocol, 0)
            
            if abs(target_allocation - current_allocation) > 0.01:  # 1% threshold
                await self._rebalance_protocol(protocol, target_allocation - current_allocation)

universal_defi = UniversalDeFiService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await universal_defi.initialize()
    yield

app = FastAPI(
    title="VedhaVriddhi Universal DeFi Service",
    description="Universal decentralized finance integration platform",
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
        "service": "universal-defi-service",
        "version": "4.0.0",
        "active_protocols": list(universal_defi.active_protocols),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/defi/swap")
async def execute_defi_swap(swap_request: DeFiSwapRequest):
    """Execute optimal DeFi token swap"""
    try:
        # Find optimal swap route
        optimal_route = await universal_defi.defi_aggregator.find_optimal_route(
            swap_request.token_in,
            swap_request.token_out,
            swap_request.amount_in
        )
        
        # Execute swap
        swap_result = await universal_defi.defi_aggregator.execute_swap(optimal_route)
        
        return {
            "swap_id": swap_result['transaction_hash'],
            "amount_out": swap_result['amount_out'],
            "gas_used": swap_result['gas_used'],
            "route": optimal_route['path'],
            "slippage": swap_result['slippage'],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("DeFi swap failed", error=str(e))
        raise HTTPException(status_code=500, detail="Swap execution failed")

@app.post("/cbdc/transfer")
async def cbdc_transfer(transfer_request: CBDCTransferRequest):
    """Execute CBDC transfer"""
    try:
        transfer_result = await universal_defi.cbdc_service.execute_transfer(
            transfer_request.from_account,
            transfer_request.to_account,
            transfer_request.amount,
            transfer_request.cbdc_type
        )
        
        return {
            "transfer_id": transfer_result['transfer_id'],
            "status": transfer_result['status'],
            "settlement_time": transfer_result['settlement_time'],
            "fee": transfer_result['fee'],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("CBDC transfer failed", error=str(e))
        raise HTTPException(status_code=500, detail="CBDC transfer failed")

@app.get("/yield/opportunities")
async def get_yield_opportunities():
    """Get current yield farming opportunities"""
    try:
        opportunities = await universal_defi.yield_optimizer.get_opportunities()
        return {
            "opportunities": opportunities,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to get yield opportunities", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve opportunities")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8107,
        reload=False
    )
