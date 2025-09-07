import asyncio
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import structlog

logger = structlog.get_logger()

class TimeSeriesDB:
    """InfluxDB time series database for analytics data"""
    
    def __init__(self, settings):
        self.settings = settings
        self.client = None
        self.write_api = None
        self.query_api = None
        
    async def initialize(self):
        """Initialize database connection"""
        try:
            self.client = InfluxDBClient(
                url=self.settings.timeseries_db_url,
                token=f"{self.settings.timeseries_db_username}:{self.settings.timeseries_db_password}",
                org="vedhavriddhi"
            )
            
            self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
            self.query_api = self.client.query_api()
            
            # Test connection
            await self._test_connection()
            logger.info("TimeSeries DB initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize TimeSeries DB", error=str(e))
            raise
    
    async def _test_connection(self):
        """Test database connection"""
        try:
            query = f'from(bucket:"{self.settings.timeseries_db_name}") |> range(start: -1m) |> limit(n:1)'
            result = self.query_api.query(org="vedhavriddhi", query=query)
            logger.info("TimeSeries DB connection successful")
        except Exception as e:
            logger.warning("TimeSeries DB connection test failed", error=str(e))
    
    async def store_portfolio_timeseries(self, portfolio_id: str, timestamp: datetime, 
                                       value: float, metadata: Dict[str, Any] = None):
        """Store portfolio time series data"""
        try:
            point = Point("portfolio_value") \
                .tag("portfolio_id", portfolio_id) \
                .field("value", value) \
                .time(timestamp, WritePrecision.NS)
            
            if metadata:
                for key, val in metadata.items():
                    if isinstance(val, (int, float)):
                        point.field(key, val)
                    else:
                        point.tag(key, str(val))
            
            self.write_api.write(bucket=self.settings.timeseries_db_name, org="vedhavriddhi", record=point)
            
        except Exception as e:
            logger.error(f"Failed to store portfolio timeseries for {portfolio_id}", error=str(e))
            raise
    
    async def get_portfolio_history(self, portfolio_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get portfolio historical data"""
        try:
            query = f'''
            from(bucket:"{self.settings.timeseries_db_name}")
              |> range(start: -{days}d)
              |> filter(fn: (r) => r._measurement == "portfolio_value")
              |> filter(fn: (r) => r.portfolio_id == "{portfolio_id}")
              |> filter(fn: (r) => r._field == "value")
              |> sort(columns: ["_time"])
            '''
            
            result = self.query_api.query(org="vedhavriddhi", query=query)
            
            data = []
            for table in result:
                for record in table.records:
                    data.append({
                        'timestamp': record.get_time(),
                        'value': record.get_value(),
                        'portfolio_id': record.values.get('portfolio_id')
                    })
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to get portfolio history for {portfolio_id}", error=str(e))
            return []
    
    async def get_portfolio_returns(self, portfolio_id: str, days: int = 252) -> List[float]:
        """Get portfolio returns for risk calculations"""
        try:
            history = await self.get_portfolio_history(portfolio_id, days + 1)
            
            if len(history) < 2:
                return []
            
            returns = []
            for i in range(1, len(history)):
                prev_value = history[i-1]['value']
                curr_value = history[i]['value']
                
                if prev_value > 0:
                    return_pct = (curr_value - prev_value) / prev_value
                    returns.append(return_pct)
            
            return returns
            
        except Exception as e:
            logger.error(f"Failed to calculate returns for {portfolio_id}", error=str(e))
            return []
    
    async def store_yield_curve(self, curve_type: str, points: List[Dict[str, Any]]):
        """Store yield curve data"""
        try:
            timestamp = datetime.utcnow()
            
            for point_data in points:
                point = Point("yield_curve") \
                    .tag("curve_type", curve_type) \
                    .tag("tenor", str(point_data['tenor'])) \
                    .field("yield", point_data['yield']) \
                    .time(timestamp, WritePrecision.NS)
                
                self.write_api.write(bucket=self.settings.timeseries_db_name, org="vedhavriddhi", record=point)
            
            logger.debug(f"Stored yield curve data for {curve_type}")
            
        except Exception as e:
            logger.error(f"Failed to store yield curve for {curve_type}", error=str(e))
            raise
    
    async def get_latest_yields(self, curve_type: str, rating: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get latest yield data for curve construction"""
        try:
            filter_clause = f'|> filter(fn: (r) => r.curve_type == "{curve_type}")'
            if rating:
                filter_clause += f' |> filter(fn: (r) => r.rating == "{rating}")'
            
            query = f'''
            from(bucket:"{self.settings.timeseries_db_name}")
              |> range(start: -1d)
              |> filter(fn: (r) => r._measurement == "yield_curve")
              {filter_clause}
              |> filter(fn: (r) => r._field == "yield")
              |> group(columns: ["tenor"])
              |> sort(columns: ["_time"], desc: true)
              |> first()
            '''
            
            result = self.query_api.query(org="vedhavriddhi", query=query)
            
            data = []
            for table in result:
                for record in table.records:
                    data.append({
                        'tenor': record.values.get('tenor'),
                        'yield': record.get_value(),
                        'timestamp': record.get_time(),
                        'curve_type': curve_type
                    })
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to get latest yields for {curve_type}", error=str(e))
            return []
    
    async def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("TimeSeries DB connection closed")
