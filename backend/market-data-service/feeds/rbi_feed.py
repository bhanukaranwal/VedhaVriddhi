import json
from typing import List, Dict, Any
import structlog
from datetime import datetime, timezone
from .base_feed import BaseFeed

logger = structlog.get_logger()

class RBIFeed(BaseFeed):
    """RBI market data feed for government securities and policy rates"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("RBI", config)
        self.base_url = "https://rbi.org.in/api"
        self.symbols = config.get('symbols', [])
        
    def _get_headers(self) -> Dict[str, str]:
        return {
            'User-Agent': 'VedhaVriddhi/1.0 (RBI Data Consumer)',
            'Accept': 'application/json',
            'Accept-Language': 'en-IN,en;q=0.9',
        }
        
    async def _fetch_data(self) -> List[Dict[str, Any]]:
        """Fetch data from RBI"""
        all_data = []
        
        try:
            # Fetch yield curve data
            yield_url = f"{self.base_url}/yield-curve/daily"
            async with self.session.get(yield_url) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'yield_data' in data:
                        all_data.extend(data['yield_data'])
                        
            # Fetch policy rates
            policy_url = f"{self.base_url}/policy-rates/current"
            async with self.session.get(policy_url) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'policy_rates' in data:
                        all_data.extend(data['policy_rates'])
                        
            # Fetch government securities auction data
            auction_url = f"{self.base_url}/auctions/government-securities/latest"
            async with self.session.get(auction_url) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'auction_data' in data:
                        all_data.extend(data['auction_data'])
                        
        except Exception as e:
            logger.error("Error fetching RBI data", error=str(e))
            
        return all_data
        
    def _normalize_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize RBI data to standard format"""
        normalized = []
        
        for item in raw_data:
            try:
                data_type = item.get('data_type', '')
                
                if data_type == 'yield_curve':
                    normalized_item = self._normalize_yield_data(item)
                elif data_type == 'policy_rate':
                    normalized_item = self._normalize_policy_rate(item)
                elif data_type == 'auction':
                    normalized_item = self._normalize_auction_data(item)
                else:
                    continue
                    
                if normalized_item:
                    normalized.append(normalized_item)
                    
            except Exception as e:
                logger.warning(f"Error normalizing RBI data point", error=str(e), item=item)
                continue
                
        return normalized
        
    def _normalize_yield_data(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize yield curve data"""
        return {
            'symbol': f"GSEC{item.get('tenor', '')}",
            'isin': item.get('isin', ''),
            'tenor': item.get('tenor', ''),
            'yield_to_maturity': self._safe_float(item.get('yield')),
            'price': self._safe_float(item.get('price')),
            'modified_duration': self._safe_float(item.get('modified_duration')),
            'timestamp': item.get('date', datetime.now(timezone.utc).isoformat()),
            'source': 'RBI',
            'instrument_type': 'government_security',
            'data_type': 'yield_curve'
        }
        
    def _normalize_policy_rate(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize policy rate data"""
        return {
            'symbol': item.get('rate_type', '').upper(),
            'rate_value': self._safe_float(item.get('rate')),
            'effective_date': item.get('effective_date', ''),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'source': 'RBI',
            'data_type': 'policy_rate'
        }
        
    def _normalize_auction_data(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize auction data"""
        return {
            'symbol': item.get('symbol', ''),
            'isin': item.get('isin', ''),
            'auction_date': item.get('auction_date', ''),
            'cut_off_yield': self._safe_float(item.get('cut_off_yield')),
            'weighted_average_yield': self._safe_float(item.get('weighted_avg_yield')),
            'notified_amount': self._safe_float(item.get('notified_amount')),
            'accepted_amount': self._safe_float(item.get('accepted_amount')),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'source': 'RBI',
            'instrument_type': 'government_security',
            'data_type': 'auction'
        }
        
    def _safe_float(self, value) -> float:
        """Safely convert value to float"""
        if value is None or value == '' or value == '-':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
