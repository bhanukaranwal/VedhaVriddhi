import asyncio
from contextlib import asynccontextmanager
from typing import Dict, List, Optional
from datetime import datetime

import structlog
import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from core.consciousness_processor import ConsciousnessProcessor
from core.collective_intelligence import CollectiveIntelligenceEngine
from core.mindfulness_monitor import MindfulnessMonitor
from core.wisdom_synthesis import WisdomSynthesisEngine
from models import *

logger = structlog.get_logger()

class ConsciousnessGatewayService:
    def __init__(self):
        self.consciousness_processor = ConsciousnessProcessor()
        self.collective_intelligence = CollectiveIntelligenceEngine()
        self.mindfulness_monitor = MindfulnessMonitor()
        self.wisdom_synthesis = WisdomSynthesisEngine()
        self.active_consciousness_streams = {}
        
    async def initialize(self):
        """Initialize Consciousness Interface Gateway"""
        logger.info("Initializing Consciousness Interface Gateway")
        
        await self.consciousness_processor.initialize()
        await self.collective_intelligence.initialize()
        await self.mindfulness_monitor.initialize()
        await self.wisdom_synthesis.initialize()
        
        # Start consciousness monitoring
        asyncio.create_task(self.monitor_collective_consciousness())
        asyncio.create_task(self.synthesize_wisdom())
        
        logger.info("Consciousness Gateway Service initialized successfully")
    
    async def monitor_collective_consciousness(self):
        """Monitor and analyze collective consciousness patterns"""
        while True:
            try:
                consciousness_state = await self.collective_intelligence.assess_global_state()
                
                # Analyze consciousness coherence
                coherence_level = consciousness_state['coherence_level']
                
                if coherence_level < 0.3:  # Low coherence
                    await self._initiate_coherence_restoration()
                elif coherence_level > 0.8:  # High coherence
                    await self._amplify_collective_wisdom()
                
                await asyncio.sleep(60)  # Monitor every minute
                
            except Exception as e:
                logger.error("Consciousness monitoring error", error=str(e))
                await asyncio.sleep(120)

consciousness_gateway_service = ConsciousnessGatewayService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await consciousness_gateway_service.initialize()
    yield

app = FastAPI(
    title="VedhaVriddhi Consciousness Interface Gateway",
    description="Advanced consciousness-aware financial interfaces",
    version="4.0.0",
    lifespan=lifespan
)

@app.websocket("/consciousness/stream/{user_id}")
async def consciousness_stream(websocket: WebSocket, user_id: str):
    """Real-time consciousness monitoring stream"""
    await websocket.accept()
    
    try:
        consciousness_gateway_service.active_consciousness_streams[user_id] = websocket
        
        while True:
            consciousness_data = await consciousness_gateway_service.consciousness_processor.get_user_state(user_id)
            await websocket.send_json({
                "consciousness_level": consciousness_data['level'],
                "mindfulness_score": consciousness_data['mindfulness'],
                "emotional_balance": consciousness_data['emotional_balance'],
                "trading_readiness": consciousness_data['trading_readiness'],
                "wisdom_insights": consciousness_data['insights']
            })
            
            await asyncio.sleep(5)  # Update every 5 seconds
            
    except WebSocketDisconnect:
        if user_id in consciousness_gateway_service.active_consciousness_streams:
            del consciousness_gateway_service.active_consciousness_streams[user_id]
    except Exception as e:
        logger.error("Consciousness stream error", error=str(e))
        await websocket.close()

@app.post("/consciousness/wisdom-synthesis")
async def wisdom_synthesis(request: WisdomSynthesisRequest):
    """Synthesize wisdom from collective intelligence"""
    try:
        wisdom = await consciousness_gateway_service.wisdom_synthesis.synthesize(
            question=request.question,
            context=request.context,
            participants=request.participants
        )
        
        return {
            "synthesized_wisdom": wisdom['insight'],
            "confidence_level": wisdom['confidence'],
            "contributing_perspectives": wisdom['perspectives'],
            "practical_guidance": wisdom['guidance'],
            "consciousness_coherence": wisdom['coherence']
        }
        
    except Exception as e:
        logger.error("Wisdom synthesis failed", error=str(e))
        raise HTTPException(status_code=500, detail="Wisdom synthesis failed")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8211, reload=False)
