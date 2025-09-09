import asyncio
from contextlib import asynccontextmanager
from typing import Dict, List, Optional
from datetime import datetime
from decimal import Decimal

import structlog
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from core.protocol_adapter_factory import ProtocolAdapterFactory
from core.cross_protocol_transaction_engine import CrossProtocolTransactionEngine
from core.liquidity_optimization import LiquidityOptimizationEngine
from core.regulatory_compliance_engine import RegulatoryComplianceEngine
from models import *

logger = structlog.get_logger()

class ProtocolIntegrationService:
    def __init__(self):
        self.adapter_factory = ProtocolAdapterFactory()
        self.transaction_engine = CrossProtocolTransactionEngine()
        self.liquidity_optimizer = LiquidityOptimizationEngine()
        self.compliance_engine = RegulatoryComplianceEngine()
        self.connected_protocols = {}
        
    async def initialize(self):
        """Initialize Protocol Integration Service"""
        logger.info("Initializing Universal Protocol Integration Service")
        
        await self.adapter_factory.initialize()
        await self.transaction_engine.initialize()
        await self.liquidity_optimizer.initialize()
        await self.compliance_engine.initialize()
        
        # Connect to protocols
        protocols_to_connect = [
            ('ethereum', {'network': 'mainnet', 'web3_url': 'https://mainnet.infura.io/v3/...'}),
            ('polygon', {'network': 'mainnet', 'web3_url': 'https://polygon-mainnet.infura.io/v3/...'}),
            ('binance_smart_chain', {'network': 'mainnet', 'web3_url': 'https://bsc-dataseed.binance.org/'}),
            ('solana', {'network': 'mainnet-beta', 'rpc_url': 'https://api.mainnet-beta.solana.com'}),
            ('avalanche', {'network': 'mainnet', 'rpc_url': 'https://api.avax.network/ext/bc/C/rpc'}),
            ('cosmos', {'network': 'cosmoshub-4', 'rpc_url': 'https://cosmos-rpc.polkachu.com'}),
            ('polkadot', {'network': 'polkadot', 'rpc_url': 'wss://rpc.polkadot.io'}),
            ('near', {'network': 'mainnet', 'rpc_url': 'https://rpc.mainnet.near.org'})
        ]
        
        for protocol_name, config in protocols_to_connect:
            try:
                adapter = await self.adapter_factory.create_adapter(protocol_name, config)
                self.connected_protocols[protocol_name] = adapter
                logger.info(f"Connected to protocol: {protocol_name}")
            except Exception as e:
                logger.error(f"Failed to connect to {protocol_name}", error=str(e))
        
        # Start optimization loops
        asyncio.create_task(self.optimize_cross_protocol_liquidity())
        asyncio.create_task(self.monitor_regulatory_compliance())
        
        logger.info(f"Protocol Integration Service initialized with {len(self.connected_protocols)} protocols")

protocol_integration_service = ProtocolIntegrationService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await protocol_integration_service.initialize()
    yield

app = FastAPI(
    title="VedhaVriddhi Protocol Integration Service",
    description="Universal blockchain and DeFi protocol integration",
    version="4.0.0",
    lifespan=lifespan
)

@app.post("/protocol/cross-chain-swap")
async def execute_cross_chain_swap(request: CrossChainSwapRequest):
    """Execute cross-chain token swap"""
    try:
        # Validate protocols are connected
        if request.source_protocol not in protocol_integration_service.connected_protocols:
            raise HTTPException(status_code=400, detail=f"Source protocol {request.source_protocol} not connected")
        if request.target_protocol not in protocol_integration_service.connected_protocols:
            raise HTTPException(status_code=400, detail=f"Target protocol {request.target_protocol} not connected")
        
        # Execute cross-chain swap
        swap_result = await protocol_integration_service.transaction_engine.execute_cross_chain_swap(
            source_protocol=request.source_protocol,
            target_protocol=request.target_protocol,
            source_token=request.source_token,
            target_token=request.target_token,
            amount=request.amount,
            recipient=request.recipient
        )
        
        return {
            "swap_id": swap_result['swap_id'],
            "source_tx_hash": swap_result['source_tx_hash'],
            "target_tx_hash": swap_result['target_tx_hash'],
            "amount_received": swap_result['amount_received'],
            "bridge_fee": swap_result['bridge_fee'],
            "completion_time": swap_result['completion_time']
        }
        
    except Exception as e:
        logger.error("Cross-chain swap failed", error=str(e))
        raise HTTPException(status_code=500, detail="Cross-chain swap failed")

@app.get("/protocol/optimal-liquidity-routes")
async def get_optimal_liquidity_routes(token_in: str, token_out: str, amount: Decimal):
    """Get optimal liquidity routes across all protocols"""
    try:
        routes = await protocol_integration_service.liquidity_optimizer.find_optimal_routes(
            token_in=token_in,
            token_out=token_out,
            amount=amount,
            protocols=list(protocol_integration_service.connected_protocols.keys())
        )
        
        return {
            "optimal_routes": routes['routes'],
            "best_price": routes['best_price'],
            "total_liquidity": routes['total_liquidity'],
            "estimated_slippage": routes['estimated_slippage'],
            "gas_estimates": routes['gas_costs']
        }
        
    except Exception as e:
        logger.error("Failed to get optimal routes", error=str(e))
        raise HTTPException(status_code=500, detail="Route optimization failed")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8209, reload=False)
