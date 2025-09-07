import asyncpg
import asyncio
import structlog
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd

logger = structlog.get_logger()

class AnalyticsDB:
    """Analytics database layer for portfolio analytics storage"""
    
    def __init__(self, settings):
        self.settings = settings
        self.pool = None
        
    async def initialize(self):
        """Initialize database connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                dsn=self.settings.analytics_db_url,
                min_size=5,
                max_size=20
            )
            logger.info("Analytics DB connection pool initialized")
            
            # Create tables if they don't exist
            await self._create_tables()
            
        except Exception as e:
            logger.error("Failed to initialize Analytics DB", error=str(e))
            raise
    
    async def _create_tables(self):
        """Create necessary tables"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS portfolio_analytics (
                    id SERIAL PRIMARY KEY,
                    portfolio_id VARCHAR(255) NOT NULL,
                    metric_name VARCHAR(255) NOT NULL,
                    metric_value DECIMAL(20,8) NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata JSONB,
                    INDEX(portfolio_id, timestamp)
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS ml_predictions (
                    id SERIAL PRIMARY KEY,
                    model_type VARCHAR(255) NOT NULL,
                    input_features JSONB NOT NULL,
                    prediction_value DECIMAL(20,8) NOT NULL,
                    confidence_score DECIMAL(10,4),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
    async def store_portfolio_analytics(self, portfolio_id: str, metrics: Dict[str, Any]):
        """Store portfolio analytics metrics"""
        try:
            async with self.pool.acquire() as conn:
                for metric_name, metric_value in metrics.items():
                    await conn.execute(
                        """
                        INSERT INTO portfolio_analytics (portfolio_id, metric_name, metric_value, metadata)
                        VALUES ($1, $2, $3, $4)
                        """,
                        portfolio_id, metric_name, float(metric_value), {}
                    )
                    
            logger.debug(f"Stored analytics for portfolio {portfolio_id}")
            
        except Exception as e:
            logger.error(f"Failed to store analytics for {portfolio_id}", error=str(e))
            raise
    
    async def get_portfolio_analytics_history(self, portfolio_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get historical analytics for a portfolio"""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(
                    """
                    SELECT metric_name, metric_value, timestamp
                    FROM portfolio_analytics
                    WHERE portfolio_id = $1 AND timestamp >= NOW() - INTERVAL '%s days'
                    ORDER BY timestamp DESC
                    """,
                    portfolio_id, days
                )
                
                return [
                    {
                        'metric_name': row['metric_name'],
                        'metric_value': float(row['metric_value']),
                        'timestamp': row['timestamp'].isoformat()
                    }
                    for row in rows
                ]
                
        except Exception as e:
            logger.error(f"Failed to get analytics history for {portfolio_id}", error=str(e))
            return []
    
    async def store_ml_prediction(self, model_type: str, features: List[float], 
                                prediction: float, confidence: float):
        """Store ML model prediction"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO ml_predictions (model_type, input_features, prediction_value, confidence_score)
                    VALUES ($1, $2, $3, $4)
                    """,
                    model_type, features, prediction, confidence
                )
                
        except Exception as e:
            logger.error("Failed to store ML prediction", error=str(e))
            raise
    
    async def close(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Analytics DB connection pool closed")
