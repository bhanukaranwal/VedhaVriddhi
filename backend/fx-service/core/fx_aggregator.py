import asyncio
from typing import Dict, List, Optional
from datetime import datetime
from decimal import Decimal
import structlog

from models import FXQuote, FXProvider, Currency

logger = structlog.get_logger()

class FXRateAggregator:
    """Aggregates FX rates from multiple providers"""
    
    def __init__(self):
        self.providers = {}
        self.rate_cache = {}
        self.provider_weights = {}
        
    async def initialize(self):
        """Initialize FX rate aggregation"""
        logger.info("Initializing FX Rate Aggregator")
        
        # Setup provider configurations
        self.providers = {
            FXProvider.BLOOMBERG: {
                'priority': 1,
                'weight': 0.4,
                'status': 'active',
                'latency_ms': 50
            },
            FXProvider.REFINITIV: {
                'priority': 2,
                'weight': 0.3,
                'status': 'active',
                'latency_ms': 75
            },
            FXProvider.ICE: {
                'priority': 3,
                'weight': 0.2,
                'status': 'active',
                'latency_ms': 100
            },
            FXProvider.OANDA: {
                'priority': 4,
                'weight': 0.1,
                'status': 'active',
                'latency_ms': 200
            }
        }
        
        # Initialize provider connections
        await self._initialize_providers()
        
    async def _initialize_providers(self):
        """Initialize connections to FX providers"""
        for provider in self.providers:
            try:
                await self._connect_provider(provider)
                logger.info(f"Connected to FX provider: {provider}")
            except Exception as e:
                logger.error(f"Failed to connect to {provider}", error=str(e))
                self.providers[provider]['status'] = 'disconnected'
    
    async def _connect_provider(self, provider: FXProvider):
        """Connect to specific FX provider"""
        # Placeholder for actual provider connections
        # In production, this would establish API connections
        await asyncio.sleep(0.1)  # Simulate connection time
        
    async def get_all_rates(self) -> Dict[str, FXQuote]:
        """Get aggregated rates from all providers"""
        all_rates = {}
        
        # Major currency pairs
        currency_pairs = [
            ('USD', 'EUR'), ('USD', 'GBP'), ('USD', 'JPY'), 
            ('USD', 'SGD'), ('USD', 'HKD'), ('USD', 'INR'),
            ('EUR', 'GBP'), ('EUR', 'JPY'), ('GBP', 'JPY')
        ]
        
        for base, quote in currency_pairs:
            pair_key = f"{base}/{quote}"
            
            # Get rates from all active providers
            provider_rates = await self._get_rates_from_providers(base, quote)
            
            # Aggregate rates using weighted average
            aggregated_rate = await self._aggregate_rates(provider_rates)
            
            if aggregated_rate:
                all_rates[pair_key] = aggregated_rate
        
        return all_rates
    
    async def _get_rates_from_providers(self, base_currency: str, quote_currency: str) -> List[FXQuote]:
        """Get rates for currency pair from all providers"""
        provider_rates = []
        
        for provider, config in self.providers.items():
            if config['status'] != 'active':
                continue
                
            try:
                rate = await self._fetch_rate_from_provider(provider, base_currency, quote_currency)
                if rate:
                    provider_rates.append(rate)
                    
            except Exception as e:
                logger.warning(f"Failed to get rate from {provider}", error=str(e))
        
        return provider_rates
    
    async def _fetch_rate_from_provider(self, provider: FXProvider, 
                                       base: str, quote: str) -> Optional[FXQuote]:
        """Fetch rate from specific provider"""
        # Simulate provider API call with sample data
        # In production, this would make actual API calls
        
        await asyncio.sleep(0.01)  # Simulate network latency
        
        # Sample rates (in production, these would come from providers)
        sample_rates = {
            'USD/EUR': {'bid': 0.8450, 'ask': 0.8452, 'mid': 0.8451},
            'USD/GBP': {'bid': 0.7498, 'ask': 0.7501, 'mid': 0.7499},
            'USD/JPY': {'bid': 110.45, 'ask': 110.55, 'mid': 110.50},
            'USD/SGD': {'bid': 1.3485, 'ask': 1.3495, 'mid': 1.3490},
            'USD/HKD': {'bid': 7.8485, 'ask': 7.8495, 'mid': 7.8490},
            'USD/INR': {'bid': 83.20, 'ask': 83.30, 'mid': 83.25}
        }
        
        pair_key = f"{base}/{quote}"
        if pair_key not in sample_rates:
            return None
        
        rate_data = sample_rates[pair_key]
        bid_rate = Decimal(str(rate_data['bid']))
        ask_rate = Decimal(str(rate_data['ask']))
        mid_rate = Decimal(str(rate_data['mid']))
        
        # Calculate spread in basis points
        spread_bps = int((ask_rate - bid_rate) / mid_rate * 10000)
        
        return FXQuote(
            currency_pair=pair_key,
            base_currency=Currency(base),
            quote_currency=Currency(quote),
            bid_rate=bid_rate,
            ask_rate=ask_rate,
            mid_rate=mid_rate,
            spread_bps=spread_bps,
            liquidity=Decimal('1000000'),  # 1M sample liquidity
            provider=provider,
            timestamp=datetime.utcnow()
        )
    
    async def _aggregate_rates(self, provider_rates: List[FXQuote]) -> Optional[FXQuote]:
        """Aggregate rates from multiple providers"""
        if not provider_rates:
            return None
        
        # Weighted average calculation
        total_weight = Decimal('0')
        weighted_bid = Decimal('0')
        weighted_ask = Decimal('0')
        weighted_mid = Decimal('0')
        total_liquidity = Decimal('0')
        
        for rate in provider_rates:
            provider_config = self.providers[rate.provider]
            weight = Decimal(str(provider_config['weight']))
            
            weighted_bid += rate.bid_rate * weight
            weighted_ask += rate.ask_rate * weight
            weighted_mid += rate.mid_rate * weight
            total_liquidity += rate.liquidity
            total_weight += weight
        
        if total_weight == 0:
            return None
        
        # Calculate aggregated rates
        agg_bid = weighted_bid / total_weight
        agg_ask = weighted_ask / total_weight
        agg_mid = weighted_mid / total_weight
        
        # Use the first rate as template
        template_rate = provider_rates[0]
        
        return FXQuote(
            currency_pair=template_rate.currency_pair,
            base_currency=template_rate.base_currency,
            quote_currency=template_rate.quote_currency,
            bid_rate=agg_bid,
            ask_rate=agg_ask,
            mid_rate=agg_mid,
            spread_bps=int((agg_ask - agg_bid) / agg_mid * 10000),
            liquidity=total_liquidity,
            provider=FXProvider.BLOOMBERG,  # Use primary provider as reference
            timestamp=datetime.utcnow()
        )
    
    async def get_rate(self, base_currency: Currency, quote_currency: Currency) -> Optional[FXQuote]:
        """Get current rate for specific currency pair"""
        pair_key = f"{base_currency}/{quote_currency}"
        
        # Check cache first
        if pair_key in self.rate_cache:
            cached_rate = self.rate_cache[pair_key]
            # Return if less than 5 seconds old
            if (datetime.utcnow() - cached_rate.timestamp).seconds < 5:
                return cached_rate
        
        # Fetch fresh rate
        provider_rates = await self._get_rates_from_providers(base_currency.value, quote_currency.value)
        aggregated_rate = await self._aggregate_rates(provider_rates)
        
        if aggregated_rate:
            self.rate_cache[pair_key] = aggregated_rate
        
        return aggregated_rate
