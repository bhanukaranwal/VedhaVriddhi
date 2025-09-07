import asyncio
from contextlib import asynccontextmanager
from typing import List, Dict, Any
from datetime import datetime
import numpy as np

import structlog
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from core.trading_agents import TradingAgentManager
from core.ml_models import MLModelService  
from core.sentiment_analyzer import SentimentAnalyzer
from core.strategy_optimizer import StrategyOptimizer
from database.ai_db import AITradingDB

logger = structlog.get_logger()

class TradeSignal(BaseModel):
    signal_id: str = Field(..., description="Unique signal identifier")
    symbol: str = Field(..., description="Instrument symbol")
    action: str = Field(..., description="BUY, SELL, HOLD")
    confidence: float = Field(..., ge=0, le=1, description="Signal confidence (0-1)")
    price_target: float = Field(..., description="Target price")
    stop_loss: float = Field(..., description="Stop loss price")
    time_horizon: int = Field(..., description="Time horizon in minutes")
    strategy_name: str = Field(..., description="Strategy that generated signal")
    market_conditions: Dict[str, Any] = Field(default_factory=dict)

class AITradingService:
    def __init__(self):
        self.agent_manager = TradingAgentManager()
        self.ml_service = MLModelService()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.strategy_optimizer = StrategyOptimizer()
        self.db = AITradingDB()
        self.active_strategies = {}
        
    async def initialize(self):
        """Initialize AI trading service"""
        logger.info("Initializing AI Trading Service")
        
        try:
            await self.db.initialize()
            await self.ml_service.initialize()
            await self.sentiment_analyzer.initialize()
            await self.strategy_optimizer.initialize()
            await self.agent_manager.initialize()
            
            # Start AI processing loops
            asyncio.create_task(self.run_market_analysis())
            asyncio.create_task(self.optimize_strategies())
            asyncio.create_task(self.monitor_agent_performance())
            
            logger.info("AI Trading Service initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize AI Trading Service", error=str(e))
            raise
    
    async def run_market_analysis(self):
        """Continuous market analysis and signal generation"""
        while True:
            try:
                # Get market data
                market_data = await self.get_current_market_data()
                
                # Run sentiment analysis
                sentiment_scores = await self.sentiment_analyzer.analyze_market_sentiment()
                
                # Generate ML predictions
                predictions = await self.ml_service.generate_predictions(market_data)
                
                # Combine signals and generate trading recommendations
                signals = await self.generate_trading_signals(market_data, sentiment_scores, predictions)
                
                # Send signals to trading agents
                for signal in signals:
                    await self.agent_manager.process_signal(signal)
                
                await asyncio.sleep(30)  # Analyze every 30 seconds
                
            except Exception as e:
                logger.error("Market analysis error", error=str(e))
                await asyncio.sleep(60)
    
    async def optimize_strategies(self):
        """Optimize trading strategies based on performance"""
        while True:
            try:
                # Get strategy performance data
                performance_data = await self.db.get_strategy_performance()
                
                # Optimize parameters
                optimized_strategies = await self.strategy_optimizer.optimize(performance_data)
                
                # Update active strategies
                for strategy_name, params in optimized_strategies.items():
                    await self.update_strategy_parameters(strategy_name, params)
                
                await asyncio.sleep(3600)  # Optimize every hour
                
            except Exception as e:
                logger.error("Strategy optimization error", error=str(e))
                await asyncio.sleep(1800)
    
    async def monitor_agent_performance(self):
        """Monitor and manage trading agent performance"""
        while True:
            try:
                # Get agent performance metrics
                agent_metrics = await self.agent_manager.get_performance_metrics()
                
                # Adjust agent parameters based on performance
                await self.agent_manager.adjust_agent_parameters(agent_metrics)
                
                await asyncio.sleep(300)  # Monitor every 5 minutes
                
            except Exception as e:
                logger.error("Agent monitoring error", error=str(e))
                await asyncio.sleep(120)
    
    async def generate_trading_signals(self, market_data: Dict, sentiment: Dict, predictions: Dict) -> List[TradeSignal]:
        """Generate trading signals from combined analysis"""
        signals = []
        
        try:
            # Combine different signal sources
            for symbol, data in market_data.items():
                # ML prediction signal
                if symbol in predictions:
                    ml_prediction = predictions[symbol]
                    confidence = ml_prediction.get('confidence', 0.5)
                    
                    if confidence > 0.7:  # High confidence threshold
                        action = "BUY" if ml_prediction['direction'] > 0 else "SELL"
                        
                        signal = TradeSignal(
                            signal_id=f"ml_{symbol}_{datetime.utcnow().timestamp()}",
                            symbol=symbol,
                            action=action,
                            confidence=confidence,
                            price_target=ml_prediction['target_price'],
                            stop_loss=ml_prediction['stop_loss'],
                            time_horizon=ml_prediction['horizon_minutes'],
                            strategy_name="ml_prediction",
                            market_conditions={
                                'sentiment': sentiment.get(symbol, 0.5),
                                'volatility': data.get('volatility', 0),
                                'volume': data.get('volume', 0)
                            }
                        )
                        signals.append(signal)
            
            return signals
            
        except Exception as e:
            logger.error("Signal generation failed", error=str(e))
            return []

ai_service = AITradingService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await ai_service.initialize()
    yield

app = FastAPI(
    title="VedhaVriddhi AI Trading Service",
    description="Advanced AI-powered trading algorithms",
    version="3.0.0", 
    lifespan=lifespan
)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ai-trading-service",
        "version": "3.0.0",
        "active_strategies": len(ai_service.active_strategies),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/signals")
async def receive_external_signal(signal: TradeSignal, background_tasks: BackgroundTasks):
    """Receive external trading signal"""
    try:
        # Validate signal
        if signal.confidence < 0.1:
            raise HTTPException(status_code=400, detail="Signal confidence too low")
        
        # Process signal asynchronously
        background_tasks.add_task(ai_service.agent_manager.process_signal, signal)
        
        return {
            "message": "Signal received and queued for processing",
            "signal_id": signal.signal_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Signal processing failed", error=str(e))
        raise HTTPException(status_code=500, detail="Signal processing failed")

@app.get("/strategies")
async def get_active_strategies():
    """Get currently active trading strategies"""
    try:
        strategies = await ai_service.db.get_active_strategies()
        return {
            "strategies": strategies,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to get strategies", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve strategies")

@app.get("/performance")
async def get_performance_metrics():
    """Get AI trading performance metrics"""
    try:
        metrics = await ai_service.agent_manager.get_performance_metrics()
        return {
            "performance": metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to get performance metrics", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8102, 
        reload=False
    )
