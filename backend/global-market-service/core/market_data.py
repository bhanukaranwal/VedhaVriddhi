import asyncio
from typing import Dict, List, Optional
from datetime import datetime
import structlog

from models import MarketData, Currency, GlobalMarketStatus, MarketSession

logger = structlog.get_logger()

class GlobalMarketDataService:
    """Global market data aggregation service"""
    
    def __init__(self, settings):
        self.settings = settings
        self.market_data_cache = {}
        self.market_status = {}
        self.data_providers = {}
        
    async def initialize(self):
        """Initialize market data service"""
        logger.info("Initializing Global Market Data Service")
        
        # Initialize data providers
        await self._setup_data_providers()
        
        # Start data streaming
        asyncio.create_task(self._stream_market_data())
        asyncio.create_task(self._update_market_status())
        
    async def _setup_data_providers(self):
        """Setup connections to market data providers"""
        self.data_providers = {
            'bloomberg': {'status': 'connected', 'priority': 1},
            'refinitiv': {'status': 'connected', 'priority': 2},
            'ice': {'status': 'connected', 'priority': 3},
            'tradeweb': {'status': 'connected', 'priority': 4}
        }
        
    async def _stream_market_data(self):
        """Stream real-time market data"""
        while True:
            try:
                # Simulate data streaming from multiple providers
                new_data = await self._fetch_latest_data()
                
                # Update cache
                for symbol, data in new_data.items():
                    self.market_data_cache[symbol] = data
                
                await asyncio.sleep(1)  # Update every second
                
            except Exception as e:
                logger.error("Market data streaming error", error=str(e))
                await asyncio.sleep(5)
    
    async def _fetch_latest_data(self) -> Dict[str, MarketData]:
        """Fetch latest market data from providers"""
        # Placeholder implementation
        # In production, this would fetch from actual data providers
        
        sample_data = {}
        symbols = ['UST_10Y', 'GILT_10Y', 'BUND_10Y', 'JGB_10Y', 'SGS_10Y']
        
        for symbol in symbols:
            sample_data[symbol] = MarketData(
                symbol=symbol,
                bid_price=100.25,
                ask_price=100.27,
                last_price=100.26,
                volume=10000,
                market=self._get_market_for_symbol(symbol),
                currency=self._get_currency_for_symbol(symbol),
                timestamp=datetime.utcnow()
            )
        
        return sample_data
    
    def _get_market_for_symbol(self, symbol: str) -> str:
        """Get market code for symbol"""
        if 'UST' in symbol:
            return 'NYSE_BONDS'
        elif 'GILT' in symbol:
            return 'LSE_BONDS'
        elif 'BUND' in symbol:
            return 'XETRA_BONDS'
        elif 'JGB' in symbol:
            return 'TSE_BONDS'
        elif 'SGS' in symbol:
            return 'SGX_BONDS'
        return 'UNKNOWN'
    
    def _get_currency_for_symbol(self, symbol: str) -> Currency:
        """Get currency for symbol"""
        if 'UST' in symbol:
            return Currency.USD
        elif 'GILT' in symbol:
            return Currency.GBP
        elif 'BUND' in symbol:
            return Currency.EUR
        elif 'JGB' in symbol:
            return Currency.JPY
        elif 'SGS' in symbol:
            return Currency.SGD
        return Currency.USD
    
    async def _update_market_status(self):
        """Update global market status"""
        while True:
            try:
                current_time = datetime.utcnow()
                
                markets = [
                    {'code': 'NYSE_BONDS', 'name': 'NYSE Bonds', 'country': 'US', 
                     'currency': Currency.USD, 'session': MarketSession.AMERICAN, 'tz': 'America/New_York'},
                    {'code': 'LSE_BONDS', 'name': 'LSE Bonds', 'country': 'UK',
                     'currency': Currency.GBP, 'session': MarketSession.EUROPEAN, 'tz': 'Europe/London'},
                    {'code': 'XETRA_BONDS', 'name': 'XETRA Bonds', 'country': 'DE',
                     'currency': Currency.EUR, 'session': MarketSession.EUROPEAN, 'tz': 'Europe/Frankfurt'},
                    {'code': 'TSE_BONDS', 'name': 'TSE Bonds', 'country': 'JP',
                     'currency': Currency.JPY, 'session': MarketSession.ASIAN, 'tz': 'Asia/Tokyo'},
                    {'code': 'SGX_BONDS', 'name': 'SGX Bonds', 'country': 'SG',
                     'currency': Currency.SGD, 'session': MarketSession.ASIAN, 'tz': 'Asia/Singapore'}
                ]
                
                for market in markets:
                    is_open = self._is_market_open(market['session'], current_time)
                    
                    self.market_status[market['code']] = GlobalMarketStatus(
                        market_code=market['code'],
                        market_name=market['name'],
                        country=market['country'],
                        currency=market['currency'],
                        session=market['session'],
                        is_open=is_open,
                        timezone=market['tz'],
                        last_updated=current_time
                    )
                
                await asyncio.sleep(300)  # Update every 5 minutes
                
            except Exception as e:
                logger.error("Market status update error", error=str(e))
                await asyncio.sleep(60)
    
    def _is_market_open(self, session: MarketSession, current_time: datetime) -> bool:
        """Determine if market is currently open"""
        hour = current_time.hour
        
        if session == MarketSession.ASIAN:
            return hour >= 23 or hour <= 8
        elif session == MarketSession.EUROPEAN:
            return 7 <= hour <= 16
        elif session == MarketSession.AMERICAN:
            return 13 <= hour <= 22
        
        return False
    
    async def get_market_data(self, symbol: str) -> Optional[MarketData]:
        """Get current market data for symbol"""
        return self.market_data_cache.get(symbol)
    
    async def get_active_markets(self) -> List[GlobalMarketStatus]:
        """Get all active market statuses"""
        return [status for status in self.market_status.values() if status.is_open]
    
    async def get_all_market_data(self) -> Dict[str, MarketData]:
        """Get all cached market data"""
        return self.market_data_cache.copy()
