import asyncio
from contextlib import asynccontextmanager
from typing import Dict, List, Optional
from datetime import datetime

import structlog
import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from core.speech_processor import SpeechProcessor
from core.nlp_engine import NLPEngine
from core.voice_commands import VoiceCommandProcessor
from models import *

logger = structlog.get_logger()

class VoiceCommand(BaseModel):
    user_id: str = Field(..., description="User identifier")
    command_text: str = Field(..., description="Voice command text")
    language: str = Field(default="en-US", description="Language code")
    confidence: float = Field(default=0.0, description="Speech recognition confidence")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    session_id: Optional[str] = Field(None, description="Voice session ID")

class VoiceResponse(BaseModel):
    status: str = Field(..., description="Response status")
    message: str = Field(..., description="Response message")
    action_taken: Optional[str] = Field(None, description="Action taken")
    confidence: float = Field(..., description="Command confidence")
    parameters: Dict = Field(default_factory=dict, description="Extracted parameters")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class VoiceTradingService:
    def __init__(self):
        self.speech_processor = SpeechProcessor()
        self.nlp_engine = NLPEngine()
        self.command_processor = VoiceCommandProcessor()
        self.active_sessions = {}
        
    async def initialize(self):
        """Initialize voice trading service"""
        logger.info("Initializing Voice Trading Service")
        
        await self.speech_processor.initialize()
        await self.nlp_engine.initialize()
        await self.command_processor.initialize()
        
        logger.info("Voice Trading Service initialized successfully")

voice_service = VoiceTradingService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await voice_service.initialize()
    yield

app = FastAPI(
    title="VedhaVriddhi Voice Trading Service",
    description="Natural language voice trading interface",
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
        "service": "voice-trading-service",
        "version": "3.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/voice/process-audio")
async def process_audio(audio_file: UploadFile = File(...), user_id: str = ""):
    """Process audio file and execute voice command"""
    try:
        # Convert audio to text
        audio_data = await audio_file.read()
        transcription = await voice_service.speech_processor.transcribe(audio_data)
        
        # Process voice command
        command = VoiceCommand(
            user_id=user_id,
            command_text=transcription['text'],
            confidence=transcription['confidence']
        )
        
        response = await process_voice_command(command)
        return response
        
    except Exception as e:
        logger.error("Audio processing failed", error=str(e))
        raise HTTPException(status_code=500, detail="Audio processing failed")

@app.post("/voice/process-text")
async def process_voice_command(command: VoiceCommand) -> VoiceResponse:
    """Process voice command from text"""
    try:
        logger.info(f"Processing voice command from user {command.user_id}: {command.command_text}")
        
        # Parse command using NLP
        parsed_command = await voice_service.nlp_engine.parse_command(command.command_text)
        
        if not parsed_command['valid']:
            return VoiceResponse(
                status="error",
                message="Sorry, I didn't understand that command. Please try again.",
                confidence=0.0
            )
        
        # Execute command
        execution_result = await voice_service.command_processor.execute_command(
            parsed_command, command.user_id
        )
        
        return VoiceResponse(
            status="success",
            message=execution_result['message'],
            action_taken=execution_result['action'],
            confidence=parsed_command['confidence'],
            parameters=parsed_command['parameters']
        )
        
    except Exception as e:
        logger.error(f"Voice command processing failed for {command.user_id}", error=str(e))
        return VoiceResponse(
            status="error",
            message="I encountered an error processing your command. Please try again.",
            confidence=0.0
        )

@app.get("/voice/supported-commands")
async def get_supported_commands():
    """Get list of supported voice commands"""
    return {
        "trading_commands": [
            "Buy 1000 shares of AAPL",
            "Sell all my Microsoft positions",
            "Show my portfolio balance",
            "What's the current price of Tesla?",
            "Cancel all pending orders",
            "Set a stop loss at 95 for Google"
        ],
        "information_commands": [
            "What's my total portfolio value?",
            "Show me today's top performers",
            "Get market summary",
            "What's the VIX level?",
            "Show me my recent trades"
        ],
        "system_commands": [
            "Switch to dark mode",
            "Show help",
            "Logout",
            "Set alert for Apple above 150"
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8104,
        reload=False
    )
