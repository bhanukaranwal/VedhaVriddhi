import asyncio
from contextlib import asynccontextmanager
from typing import Dict, List, Optional
import numpy as np

import structlog
import uvicorn
from fastapi import FastAPI, HTTPException

from core.quantum_neural_networks import QuantumNeuralNetworkEngine
from core.quantum_feature_maps import QuantumFeatureMapper
from core.variational_quantum_classifiers import VQCEngine
from core.quantum_generative_models import QuantumGANEngine
from models import *

logger = structlog.get_logger()

class QuantumMLService:
    def __init__(self):
        self.qnn_engine = QuantumNeuralNetworkEngine()
        self.feature_mapper = QuantumFeatureMapper()
        self.vqc_engine = VQCEngine()
        self.qgan_engine = QuantumGANEngine()
        
    async def initialize(self):
        """Initialize Quantum Machine Learning Service"""
        logger.info("Initializing Quantum ML Service")
        
        await self.qnn_engine.initialize()
        await self.feature_mapper.initialize()
        await self.vqc_engine.initialize()
        await self.qgan_engine.initialize()
        
        logger.info("Quantum ML Service initialized successfully")

quantum_ml_service = QuantumMLService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await quantum_ml_service.initialize()
    yield

app = FastAPI(
    title="VedhaVriddhi Quantum ML Service",
    description="Quantum-enhanced machine learning for finance",
    version="4.0.0",
    lifespan=lifespan
)

@app.post("/quantum-ml/train-model")
async def train_quantum_model(request: QuantumMLTrainingRequest):
    """Train quantum machine learning model"""
    try:
        training_result = await quantum_ml_service.qnn_engine.train_model(
            training_data=request.training_data,
            model_architecture=request.architecture,
            quantum_parameters=request.quantum_params
        )
        
        return {
            "model_id": training_result['model_id'],
            "training_accuracy": training_result['accuracy'],
            "quantum_advantage": training_result['speedup'],
            "model_parameters": training_result['parameters'],
            "training_time": training_result['training_time']
        }
        
    except Exception as e:
        logger.error("Quantum ML training failed", error=str(e))
        raise HTTPException(status_code=500, detail="Quantum ML training failed")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8206, reload=False)
