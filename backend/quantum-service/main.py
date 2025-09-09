import asyncio
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
from contextlib import asynccontextmanager

import structlog
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from core.quantum_processor import QuantumProcessorInterface, IBMQuantumProcessor, GoogleQuantumProcessor
from core.quantum_algorithms import QuantumPortfolioOptimizer, QuantumRiskAnalyzer
from models import *

logger = structlog.get_logger()

class QuantumService:
    def __init__(self):
        self.processors = {}
        self.portfolio_optimizer = QuantumPortfolioOptimizer()
        self.risk_analyzer = QuantumRiskAnalyzer()
        self.active_jobs = {}
        
    async def initialize(self):
        """Initialize quantum computing infrastructure"""
        logger.info("Initializing Quantum Computing Service")
        
        # Initialize quantum processors
        self.processors['ibm'] = IBMQuantumProcessor('IBM Quantum', '', '')
        self.processors['google'] = GoogleQuantumProcessor('Google Quantum AI', '', '')
        
        await self.portfolio_optimizer.initialize()
        await self.risk_analyzer.initialize()
        
        logger.info("Quantum Computing Service initialized successfully")

quantum_service = QuantumService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await quantum_service.initialize()
    yield

app = FastAPI(
    title="VedhaVriddhi Quantum Computing Service",
    description="Quantum-enhanced financial computations",
    version="4.0.0",
    lifespan=lifespan
)

@app.post("/quantum/optimize-portfolio")
async def quantum_portfolio_optimization(request: QuantumPortfolioRequest):
    """Execute quantum portfolio optimization"""
    try:
        result = await quantum_service.portfolio_optimizer.optimize(
            assets=request.assets,
            expected_returns=request.expected_returns,
            covariance_matrix=request.covariance_matrix,
            risk_tolerance=request.risk_tolerance
        )
        
        return {
            "optimized_weights": result['weights'],
            "expected_return": result['expected_return'],
            "risk_level": result['risk'],
            "quantum_advantage": result['speedup'],
            "computation_time": result['time'],
            "confidence": result['confidence']
        }
        
    except Exception as e:
        logger.error("Quantum portfolio optimization failed", error=str(e))
        raise HTTPException(status_code=500, detail="Quantum optimization failed")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8200, reload=False)
