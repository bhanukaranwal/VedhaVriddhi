import asyncio
from typing import Dict, Optional
from datetime import datetime
from decimal import Decimal
import structlog

from models import Currency, CurrencyPair

logger = structlog.get_logger()

class CurrencyConverter:
    """Professional currency conversion service"""
    
    def __init__(self, settings):
        self.settings = settings
        self.fx_rates = {}
        self.rate_providers = {}
        
    async def initialize(self):
        """Initialize currency converter"""
        logger.info("Initializing Currency Converter")
        
        # Setup FX rate providers
        self.rate_providers = {
            'reuters': {'priority': 1, 'status': 'active'},
            'bloomberg': {'priority': 2, 'status': 'active'},
            'xe': {'priority': 3, 'status': 'active'}
        }
        
        # Start rate streaming
        asyncio.create_task(self._stream_fx_rates())
        
    async def _stream_fx_rates(self):
        """Stream real-time FX rates"""
        while True:
            try:
                # Fetch latest rates from providers
                new_rates = await self._fetch_fx_rates()
                
                # Update rate cache
                for pair, rate_data in new_rates.items():
                    self.fx_rates[pair] = rate_data
                
                await asyncio.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                logger.error("FX rate streaming error", error=str(e))
                await asyncio.sleep(10)
    
    async def _fetch_fx_rates(self) -> Dict[str, CurrencyPair]:
        """Fetch FX rates from providers"""
        # Placeholder implementation with sample rates
        # In production, this would fetch from actual FX data providers
        
        sample_rates = {
            'USD/EUR': CurrencyPair(
                base_currency=Currency.USD,
                quote_currency=Currency.EUR,
                rate=Decimal('0.85'),
                timestamp=datetime.utcnow()
            ),
            'USD/GBP': CurrencyPair(
                base_currency=Currency.USD,
                quote_currency=Currency.GBP,
                rate=Decimal('0.75'),
                timestamp=datetime.utcnow()
            ),
            'USD/JPY': CurrencyPair(
                base_currency=Currency.USD,
                quote_currency=Currency.JPY,
                rate=Decimal('110.50'),
                timestamp=datetime.utcnow()
            ),
            'USD/SGD': CurrencyPair(
                base_currency=Currency.USD,
                quote_currency=Currency.SGD,
                rate=Decimal('1.35'),
                timestamp=datetime.utcnow()
            ),
            'USD/HKD': CurrencyPair(
                base_currency=Currency.USD,
                quote_currency=Currency.HKD,
                rate=Decimal('7.85'),
                timestamp=datetime.utcnow()
            ),
            'USD/INR': CurrencyPair(
                base_currency=Currency.USD,
                quote_currency=Currency.INR,
                rate=Decimal('83.25'),
                timestamp=datetime.utcnow()
            )
        }
        
        return sample_rates
    
    async def get_rate(self, base_currency: Currency, quote_currency: Currency) -> Optional[Decimal]:
        """Get current FX rate between currencies"""
        if base_currency == quote_currency:
            return Decimal('1.0')
        
        # Try direct rate
        pair_key = f"{base_currency}/{quote_currency}"
        if pair_key in self.fx_rates:
            return self.fx_rates[pair_key].rate
        
        # Try inverse rate
        inverse_key = f"{quote_currency}/{base_currency}"
        if inverse_key in self.fx_rates:
            return Decimal('1.0') / self.fx_rates[inverse_key].rate
        
        # Try cross rate via USD
        if base_currency != Currency.USD and quote_currency != Currency.USD:
            usd_base = await self.get_rate(Currency.USD, base_currency)
            usd_quote = await self.get_rate(Currency.USD, quote_currency)
            
            if usd_base and usd_quote:
                return usd_quote / usd_base
        
        logger.warning(f"No FX rate available for {base_currency}/{quote_currency}")
        return None
    
    async def convert_amount(self, amount: Decimal, from_currency: Currency, 
                           to_currency: Currency) -> Optional[Decimal]:
        """Convert amount between currencies"""
        rate = await self.get_rate(from_currency, to_currency)
        if rate:
            return amount * rate
        return None
    
    async def get_all_rates(self, base_currency: Currency) -> Dict[str, Decimal]:
        """Get all rates for base currency"""
        rates = {}
        
        for currency in Currency:
            if currency != base_currency:
                rate = await self.get_rate(base_currency, currency)
                if rate:
                    rates[currency.value] = rate
        
        return rates
    
    async def requires_conversion(self, order) -> bool:
        """Check if order requires currency conversion"""
        # This would check if the order currency matches the market currency
        # For now, return True if not USD (simplified logic)
        return order.currency != Currency.USD
