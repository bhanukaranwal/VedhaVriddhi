import asyncio
from contextlib import asynccontextmanager
from typing import Dict, List, Optional
from datetime import datetime

import structlog
import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from core.virtual_environment import VirtualTradingEnvironment
from core.avatar_manager import AvatarManager
from core.spatial_interface import SpatialInterfaceManager
from core.vr_session import VRSessionManager
from models import *

logger = structlog.get_logger()

class MetaverseService:
    def __init__(self):
        self.virtual_environment = VirtualTradingEnvironment()
        self.avatar_manager = AvatarManager()
        self.spatial_interface = SpatialInterfaceManager()
        self.vr_session_manager = VRSessionManager()
        self.active_sessions = {}
        self.connected_users = {}
        
    async def initialize(self):
        """Initialize Metaverse Trading Service"""
        logger.info("Initializing Metaverse Trading Service")
        
        try:
            await self.virtual_environment.initialize()
            await self.avatar_manager.initialize()
            await self.spatial_interface.initialize()
            await self.vr_session_manager.initialize()
            
            # Create default trading environments
            await self._create_default_environments()
            
            logger.info("Metaverse Trading Service initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize Metaverse Service", error=str(e))
            raise
    
    async def _create_default_environments(self):
        """Create default virtual trading environments"""
        environments = [
            {
                'name': 'NYSE Trading Floor',
                'type': 'traditional_exchange',
                'capacity': 100,
                'features': ['voice_trading', 'gesture_controls', 'holographic_displays']
            },
            {
                'name': 'Quantum Analytics Lab',
                'type': 'analytics_workspace',
                'capacity': 20,
                'features': ['3d_visualizations', 'quantum_simulations', 'collaborative_tools']
            },
            {
                'name': 'DeFi Protocol Plaza',
                'type': 'defi_environment',
                'capacity': 50,
                'features': ['protocol_interactions', 'yield_visualizations', 'liquidity_pools']
            }
        ]
        
        for env_config in environments:
            await self.virtual_environment.create_environment(env_config)

metaverse_service = MetaverseService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await metaverse_service.initialize()
    yield

app = FastAPI(
    title="VedhaVriddhi Metaverse Trading Service",
    description="Immersive virtual reality trading environments",
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
        "service": "metaverse-service",
        "version": "4.0.0",
        "active_sessions": len(metaverse_service.active_sessions),
        "connected_users": len(metaverse_service.connected_users),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/vr/session/create")
async def create_vr_session(session_request: VRSessionRequest):
    """Create new VR trading session"""
    try:
        session = await metaverse_service.vr_session_manager.create_session(
            user_id=session_request.user_id,
            environment_type=session_request.environment_type,
            device_type=session_request.device_type
        )
        
        metaverse_service.active_sessions[session['session_id']] = session
        
        return {
            "session_id": session['session_id'],
            "environment_url": session['environment_url'],
            "avatar_id": session['avatar_id'],
            "spatial_coordinates": session['initial_position'],
            "session_token": session['access_token'],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to create VR session", error=str(e))
        raise HTTPException(status_code=500, detail="VR session creation failed")

@app.websocket("/vr/session/{session_id}/connect")
async def vr_session_websocket(websocket: WebSocket, session_id: str):
    """WebSocket connection for VR session"""
    await websocket.accept()
    
    try:
        # Register user connection
        user_id = await metaverse_service.vr_session_manager.authenticate_session(session_id)
        metaverse_service.connected_users[user_id] = websocket
        
        logger.info(f"User {user_id} connected to VR session {session_id}")
        
        while True:
            # Receive VR events
            data = await websocket.receive_json()
            
            # Process VR interaction
            response = await metaverse_service.spatial_interface.process_interaction(
                user_id, data
            )
            
            # Send response back to VR client
            await websocket.send_json(response)
            
    except WebSocketDisconnect:
        # Clean up on disconnect
        if user_id in metaverse_service.connected_users:
            del metaverse_service.connected_users[user_id]
        logger.info(f"User {user_id} disconnected from VR session")
    
    except Exception as e:
        logger.error("VR session WebSocket error", error=str(e))
        await websocket.close()

@app.post("/avatar/create")
async def create_avatar(avatar_request: AvatarCreationRequest):
    """Create user avatar for metaverse"""
    try:
        avatar = await metaverse_service.avatar_manager.create_avatar(
            user_id=avatar_request.user_id,
            appearance=avatar_request.appearance,
            capabilities=avatar_request.capabilities
        )
        
        return {
            "avatar_id": avatar['avatar_id'],
            "appearance_hash": avatar['appearance_hash'],
            "capabilities": avatar['capabilities'],
            "created_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Avatar creation failed", error=str(e))
        raise HTTPException(status_code=500, detail="Avatar creation failed")

@app.get("/environments")
async def get_available_environments():
    """Get available virtual trading environments"""
    try:
        environments = await metaverse_service.virtual_environment.get_all_environments()
        return {
            "environments": environments,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to get environments", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve environments")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8108,
        reload=False
    )
