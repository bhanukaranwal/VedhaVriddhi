import asyncio
from contextlib import asynccontextmanager
from typing import Dict, List, Optional
from datetime import datetime

import structlog
import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from core.biometric_processor import BiometricProcessor
from core.consciousness_bridge import ConsciousnessBridge
from core.emotion_analyzer import EmotionAnalyzer
from core.neural_feedback_loop import NeuralFeedbackLoop
from models import *

logger = structlog.get_logger()

class NeuralInterfaceService:
    def __init__(self):
        self.biometric_processor = BiometricProcessor()
        self.consciousness_bridge = ConsciousnessBridge()
        self.emotion_analyzer = EmotionAnalyzer()
        self.neural_feedback_loop = NeuralFeedbackLoop()
        self.active_neural_sessions = {}
        
    async def initialize(self):
        """Initialize Neural Interface Service"""
        logger.info("Initializing Neural Interface & Consciousness Service")
        
        await self.biometric_processor.initialize()
        await self.consciousness_bridge.initialize()
        await self.emotion_analyzer.initialize()
        await self.neural_feedback_loop.initialize()
        
        # Start consciousness monitoring
        asyncio.create_task(self.monitor_collective_consciousness())
        asyncio.create_task(self.analyze_trading_emotions())
        
        logger.info("Neural Interface Service initialized successfully")
    
    async def monitor_collective_consciousness(self):
        """Monitor collective trading consciousness"""
        while True:
            try:
                consciousness_state = await self.consciousness_bridge.assess_market_consciousness()
                
                # Adjust trading algorithms based on collective emotional state
                if consciousness_state['fear_greed_index'] > 0.8:  # Extreme greed
                    await self._implement_emotional_circuit_breakers()
                elif consciousness_state['fear_greed_index'] < 0.2:  # Extreme fear
                    await self._activate_confidence_restoration_protocols()
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error("Consciousness monitoring error", error=str(e))
                await asyncio.sleep(120)

neural_interface_service = NeuralInterfaceService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await neural_interface_service.initialize()
    yield

app = FastAPI(
    title="VedhaVriddhi Neural Interface Service",
    description="Consciousness-aware neural interface for finance",
    version="4.0.0",
    lifespan=lifespan
)

@app.post("/neural/biometric-auth")
async def biometric_authentication(request: BiometricAuthRequest):
    """Authenticate using biometric data"""
    try:
        auth_result = await neural_interface_service.biometric_processor.authenticate(
            user_id=request.user_id,
            biometric_data=request.biometric_data,
            auth_type=request.auth_type
        )
        
        return {
            "authenticated": auth_result['success'],
            "confidence": auth_result['confidence'],
            "emotional_state": auth_result['emotional_state'],
            "stress_level": auth_result['stress_level'],
            "trading_clearance": auth_result['trading_approved']
        }
        
    except Exception as e:
        logger.error("Biometric authentication failed", error=str(e))
        raise HTTPException(status_code=500, detail="Biometric authentication failed")

@app.websocket("/neural/consciousness-stream/{user_id}")
async def consciousness_stream(websocket: WebSocket, user_id: str):
    """Real-time consciousness state monitoring"""
    await websocket.accept()
    
    try:
        while True:
            consciousness_data = await neural_interface_service.consciousness_bridge.get_user_state(user_id)
            await websocket.send_json(consciousness_data)
            await asyncio.sleep(5)  # Update every 5 seconds
            
    except Exception as e:
        logger.error("Consciousness stream error", error=str(e))
        await websocket.close()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8205, reload=False)
