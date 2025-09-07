import asyncio
import logging
import signal
import sys
from contextlib import asynccontextmanager
from typing import Dict, List, Optional

import structlog
import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from feeds import FeedManager
from processors import DataProcessor
from storage import StorageManager
from config import Settings
from models import MarketDataPoint, InstrumentData

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

class MarketDataService:
    def __init__(self):
        self.settings = Settings()
        self.feed_manager = FeedManager(self.settings)
        self.data_processor = DataProcessor(self.settings)
        self.storage_manager = StorageManager(self.settings)
        self.websocket_connections: Dict[str, List[WebSocket]] = {}
        self.running = False

    async def start(self):
        """Start the market data service"""
        logger.info("Starting VedhaVriddhi Market Data Service")
        
        try:
            await self.storage_manager.initialize()
            await self.feed_manager.initialize()
            await self.data_processor.initialize()
            
            # Start processing tasks
            asyncio.create_task(self.process_market_data())
            asyncio.create_task(self.broadcast_data())
            
            self.running = True
            logger.info("Market Data Service started successfully")
            
        except Exception as e:
            logger.error("Failed to start Market Data Service", error=str(e))
            raise

    async def stop(self):
        """Stop the market data service"""
        logger.info("Stopping VedhaVriddhi Market Data Service")
        
        self.running = False
        
        await self.feed_manager.stop()
        await self.data_processor.stop()
        await self.storage_manager.close()
        
        logger.info("Market Data Service stopped")

    async def process_market_data(self):
        """Main data processing loop"""
        while self.running:
            try:
                # Process data from all feeds
                raw_data = await self.feed_manager.get_latest_data()
                
                if raw_data:
                    # Process and normalize data
                    processed_data = await self.data_processor.process_batch(raw_data)
                    
                    # Store in databases
                    await self.storage_manager.store_market_data(processed_data)
                    
                    # Update real-time cache
                    await self.storage_manager.update_cache(processed_data)
                    
                    logger.debug(f"Processed {len(processed_data)} market data points")
                
                await asyncio.sleep(0.1)  # 100ms processing cycle
                
            except Exception as e:
                logger.error("Error in market data processing", error=str(e))
                await asyncio.sleep(1)

    async def broadcast_data(self):
        """Broadcast data to WebSocket connections"""
        while self.running:
            try:
                # Get latest data for broadcast
                latest_data = await self.storage_manager.get_latest_data()
                
                if latest_data:
                    # Broadcast to all connected clients
                    for symbol, connections in self.websocket_connections.items():
                        if symbol in latest_data:
                            message = latest_data[symbol].dict()
                            
                            # Send to all connections for this symbol
                            disconnected = []
                            for websocket in connections:
                                try:
                                    await websocket.send_json(message)
                                except:
                                    disconnected.append(websocket)
                            
                            # Remove disconnected clients
                            for ws in disconnected:
                                connections.remove(ws)
                
                await asyncio.sleep(0.05)  # 50ms broadcast cycle
                
            except Exception as e:
                logger.error("Error in data broadcasting", error=str(e))
                await asyncio.sleep(1)

    async def add_websocket_subscription(self, websocket: WebSocket, symbol: str):
        """Add WebSocket subscription for a symbol"""
        if symbol not in self.websocket_connections:
            self.websocket_connections[symbol] = []
        
        self.websocket_connections[symbol].append(websocket)
        logger.info(f"Added WebSocket subscription for {symbol}")

    async def remove_websocket_subscription(self, websocket: WebSocket, symbol: str):
        """Remove WebSocket subscription"""
        if symbol in self.websocket_connections:
            if websocket in self.websocket_connections[symbol]:
                self.websocket_connections[symbol].remove(websocket)
                logger.info(f"Removed WebSocket subscription for {symbol}")

# Global service instance
market_data_service = MarketDataService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await market_data_service.start()
    yield
    # Shutdown
    await market_data_service.stop()

# FastAPI application
app = FastAPI(
    title="VedhaVriddhi Market Data Service",
    description="Ultra-fast market data processing for Indian bond markets",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class MarketDataResponse(BaseModel):
    symbol: str
    bid_price: Optional[float]
    ask_price: Optional[float]
    last_price: Optional[float]
    volume: float
    timestamp: str
    yield_to_maturity: Optional[float]
    duration: Optional[float]
    accrued_interest: Optional[float]

class HistoricalDataRequest(BaseModel):
    symbols: List[str]
    start_date: str
    end_date: str
    interval: str = "1min"

# API endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "market-data-service",
        "version": "1.0.0",
        "running": market_data_service.running
    }

@app.get("/market-data/{symbol}", response_model=MarketDataResponse)
async def get_market_data(symbol: str):
    """Get latest market data for a symbol"""
    try:
        data = await market_data_service.storage_manager.get_symbol_data(symbol)
        if not data:
            raise HTTPException(status_code=404, detail=f"No data found for symbol {symbol}")
        
        return MarketDataResponse(**data.dict())
    
    except Exception as e:
        logger.error(f"Error getting market data for {symbol}", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/market-data")
async def get_all_market_data():
    """Get latest market data for all symbols"""
    try:
        data = await market_data_service.storage_manager.get_all_latest_data()
        return {"data": data, "count": len(data)}
    
    except Exception as e:
        logger.error("Error getting all market data", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/historical-data")
async def get_historical_data(request: HistoricalDataRequest):
    """Get historical market data"""
    try:
        data = await market_data_service.storage_manager.get_historical_data(
            request.symbols,
            request.start_date,
            request.end_date,
            request.interval
        )
        return {"data": data, "count": len(data)}
    
    except Exception as e:
        logger.error("Error getting historical data", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/instruments")
async def get_instruments():
    """Get list of available instruments"""
    try:
        instruments = await market_data_service.storage_manager.get_instruments()
        return {"instruments": instruments, "count": len(instruments)}
    
    except Exception as e:
        logger.error("Error getting instruments", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()

@app.websocket("/ws/{symbol}")
async def websocket_endpoint(websocket: WebSocket, symbol: str):
    """WebSocket endpoint for real-time market data"""
    await websocket.accept()
    await market_data_service.add_websocket_subscription(websocket, symbol)
    
    try:
        while True:
            # Keep connection alive and handle client messages
            message = await websocket.receive_text()
            logger.debug(f"Received WebSocket message: {message}")
            
    except WebSocketDisconnect:
        await market_data_service.remove_websocket_subscription(websocket, symbol)
        logger.info(f"WebSocket disconnected for {symbol}")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}")
    sys.exit(0)

if __name__ == "__main__":
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        log_config=None,  # Use structured logging
        access_log=False,
        reload=False
    )
