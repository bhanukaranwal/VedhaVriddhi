import json
from typing import List, Dict, Any
import structlog
from datetime import datetime, timezone
from .base_feed import BaseFeed

logger = structlog.get_logger()

class NSEFeed(BaseFeed):
    """NSE market data feed"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("NSE", config)
        self.base_url = "https://www.nseindia.com/api"
        self.symbols = config.get('symbols', [])
        
    def _get_headers(self) -> Dict[str, str]:
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
    async def _fetch_data(self) -> List[Dict[str, Any]]:
        """Fetch bond data from NSE"""
        all_data = []
        
        try:
            # Fetch government securities data
            gsec_url = f"{self.base_url}/liveEquity-gsec"
            async with self.session.get(gsec_url) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'data' in data:
                        all_data.extend(data['data'])
                        
            # Fetch corporate bond data
            corp_bond_url = f"{self.base_url}/liveEquity-debt"
            async with self.session.get(corp_bond_url) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'data' in data:
                        all_data.extend(data['data'])
                        
        except Exception as e:
            logger.error("Error fetching NSE data", error=str(e))
            
        return all_data
        
    def _normalize_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize NSE data to standard format"""
        normalized = []
        
        for item in raw_data:
            try:
                normalized_item = {
                    'symbol': item.get('symbol', ''),
                    'isin': item.get('isin', ''),
                    'bid_price': self._safe_float(item.get('bidPrice')),
                    'ask_price': self._safe_float(item.get('askPrice')),
                    'last_price': self._safe_float(item.get('lastPrice')),
                    'volume': self._safe_float(item.get('totalTradedVolume', 0)),
                    'value': self._safe_float(item.get('totalTradedValue', 0)),
                    'yield_to_maturity': self._safe_float(item.get('yieldToMaturity')),
                    'modified_duration': self._safe_float(item.get('modifiedDuration')),
                    'accrued_interest': self._safe_float(item.get('accruedInterest')),
                    'clean_price': self._safe_float(item.get('cleanPrice')),
                    'dirty_price': self._safe_float(item.get('dirtyPrice')),
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'source': 'NSE',
                    'instrument_type': self._determine_instrument_type(item)
                }
                
                # Only add if we have essential data
                if normalized_item['symbol'] and (
                    normalized_item['last_price'] or 
                    normalized_item['bid_price'] or 
                    normalized_item['ask_price']
                ):
                    normalized.append(normalized_item)
                    
            except Exception as e:
                logger.warning(f"Error normalizing NSE data point", error=str(e), item=item)
                continue
                
        return normalized
        
    def _safe_float(self, value) -> float:
        """Safely convert value to float"""
        if value is None or value == '' or value == '-':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
            
    def _determine_instrument_type(self, item: Dict[str, Any]) -> str:
        """Determine instrument type from NSE data"""
        symbol = item.get('symbol', '').upper()
        series = item.get('series', '').upper()
        
        if 'GSEC' in symbol or series == 'GS':
            return 'government_security'
        elif 'TBILL' in symbol or 'TB' in symbol:
            return 'treasury_bill'
        elif series == 'CD':
            return 'certificate_of_deposit'
        elif series == 'CP':
            return 'commercial_paper'
        else:
            return 'corporate_bond'
