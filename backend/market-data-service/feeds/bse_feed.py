import json
from typing import List, Dict, Any
import structlog
from datetime import datetime, timezone
from .base_feed import BaseFeed

logger = structlog.get_logger()

class BSEFeed(BaseFeed):
    """BSE market data feed"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("BSE", config)
        self.base_url = "https://api.bseindia.com/api"
        self.api_key = config.get('api_key', '')
        self.symbols = config.get('symbols', [])
        
    def _get_headers(self) -> Dict[str, str]:
        return {
            'User-Agent': 'VedhaVriddhi/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}' if self.api_key else '',
        }
        
    async def _fetch_data(self) -> List[Dict[str, Any]]:
        """Fetch bond data from BSE"""
        all_data = []
        
        try:
            # Fetch debt securities data
            debt_url = f"{self.base_url}/debt-securities/live-data"
            async with self.session.get(debt_url) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'data' in data:
                        all_data.extend(data['data'])
                        
            # Fetch government securities
            govt_url = f"{self.base_url}/govt-securities/live-data"
            async with self.session.get(govt_url) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'data' in data:
                        all_data.extend(data['data'])
                        
        except Exception as e:
            logger.error("Error fetching BSE data", error=str(e))
            
        return all_data
        
    def _normalize_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize BSE data to standard format"""
        normalized = []
        
        for item in raw_data:
            try:
                normalized_item = {
                    'symbol': item.get('scrip_code', ''),
                    'isin': item.get('isin_code', ''),
                    'scrip_name': item.get('scrip_name', ''),
                    'bid_price': self._safe_float(item.get('bid_price')),
                    'ask_price': self._safe_float(item.get('ask_price')),
                    'last_price': self._safe_float(item.get('last_traded_price')),
                    'volume': self._safe_float(item.get('total_traded_volume', 0)),
                    'value': self._safe_float(item.get('total_traded_value', 0)),
                    'yield_to_maturity': self._safe_float(item.get('ytm')),
                    'modified_duration': self._safe_float(item.get('modified_duration')),
                    'accrued_interest': self._safe_float(item.get('accrued_interest')),
                    'clean_price': self._safe_float(item.get('clean_price')),
                    'dirty_price': self._safe_float(item.get('dirty_price')),
                    'face_value': self._safe_float(item.get('face_value', 100)),
                    'coupon_rate': self._safe_float(item.get('coupon_rate')),
                    'maturity_date': item.get('maturity_date', ''),
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'source': 'BSE',
                    'instrument_type': self._determine_instrument_type(item),
                    'exchange': 'BSE'
                }
                
                if normalized_item['symbol'] and (
                    normalized_item['last_price'] or 
                    normalized_item['bid_price'] or 
                    normalized_item['ask_price']
                ):
                    normalized.append(normalized_item)
                    
            except Exception as e:
                logger.warning(f"Error normalizing BSE data point", error=str(e), item=item)
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
        """Determine instrument type from BSE data"""
        scrip_name = item.get('scrip_name', '').upper()
        series = item.get('series', '').upper()
        
        if 'GOVT' in scrip_name or 'GSEC' in scrip_name:
            return 'government_security'
        elif 'TBILL' in scrip_name or 'TREASURY' in scrip_name:
            return 'treasury_bill'
        elif series == 'CD' or 'CERTIFICATE OF DEPOSIT' in scrip_name:
            return 'certificate_of_deposit'
        elif series == 'CP' or 'COMMERCIAL PAPER' in scrip_name:
            return 'commercial_paper'
        else:
            return 'corporate_bond'
