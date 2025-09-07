from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import asyncio
import aiohttp
import structlog
from datetime import datetime, timezone

logger = structlog.get_logger()

class BaseFeed(ABC):
    """Base class for all market data feeds"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.running = False
        self.data_queue = asyncio.Queue(maxsize=10000)
        
    async def initialize(self):
        """Initialize the feed"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers=self._get_headers()
        )
        self.running = True
        logger.info(f"Initialized {self.name} feed")
        
    async def stop(self):
        """Stop the feed"""
        self.running = False
        if self.session:
            await self.session.close()
        logger.info(f"Stopped {self.name} feed")
        
    @abstractmethod
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for requests"""
        pass
        
    @abstractmethod
    async def _fetch_data(self) -> List[Dict[str, Any]]:
        """Fetch data from the feed source"""
        pass
        
    @abstractmethod
    def _normalize_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize raw data to standard format"""
        pass
        
    async def start_feed(self):
        """Start the data feed"""
        while self.running:
            try:
                raw_data = await self._fetch_data()
                if raw_data:
                    normalized_data = self._normalize_data(raw_data)
                    
                    for data_point in normalized_data:
                        try:
                            await self.data_queue.put_nowait(data_point)
                        except asyncio.QueueFull:
                            # Remove oldest item and add new one
                            try:
                                await self.data_queue.get_nowait()
                                await self.data_queue.put_nowait(data_point)
                            except asyncio.QueueEmpty:
                                pass
                                
                    logger.debug(f"{self.name}: Processed {len(normalized_data)} data points")
                    
            except Exception as e:
                logger.error(f"Error in {self.name} feed", error=str(e))
                await asyncio.sleep(5)  # Back off on error
                
            await asyncio.sleep(self.config.get('poll_interval', 1))
            
    async def get_data(self) -> List[Dict[str, Any]]:
        """Get available data from the queue"""
        data = []
        try:
            while True:
                item = await asyncio.wait_for(self.data_queue.get(), timeout=0.01)
                data.append(item)
        except asyncio.TimeoutError:
            pass
        return data
