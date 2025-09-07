import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import structlog

from models import GlobalOrder, MarketSession, Currency
from database.global_db import GlobalTradingDB

logger = structlog.get_logger()

class GlobalOrderRouter:
    """Intelligent global order routing with session awareness"""
    
    def __init__(self, settings):
        self.settings = settings
        self.db = GlobalTradingDB(settings)
        self.market_sessions = {}
        self.routing_rules = {}
        
    async def initialize(self):
        """Initialize order router"""
        logger.info("Initializing Global Order Router")
        
        # Define market routing rules
        self.routing_rules = {
            'US_TREASURIES': {
                'primary_market': 'NYSE_BONDS',
                'sessions': [MarketSession.AMERICAN],
                'currencies': [Currency.USD],
                'settlement_days': 1
            },
            'UK_GILTS': {
                'primary_market': 'LSE_BONDS', 
                'sessions': [MarketSession.EUROPEAN],
                'currencies': [Currency.GBP],
                'settlement_days': 1
            },
            'GERMAN_BUNDS': {
                'primary_market': 'XETRA_BONDS',
                'sessions': [MarketSession.EUROPEAN],
                'currencies': [Currency.EUR],
                'settlement_days': 2
            },
            'JAPANESE_BONDS': {
                'primary_market': 'TSE_BONDS',
                'sessions': [MarketSession.ASIAN],
                'currencies': [Currency.JPY],
                'settlement_days': 2
            },
            'SINGAPORE_BONDS': {
                'primary_market': 'SGX_BONDS',
                'sessions': [MarketSession.ASIAN],
                'currencies': [Currency.SGD],
                'settlement_days': 2
            }
        }
        
        await self._load_market_sessions()
        
    async def _load_market_sessions(self):
        """Load current market session information"""
        current_time = datetime.now(timezone.utc)
        hour = current_time.hour
        
        # Determine active sessions based on UTC time
        self.market_sessions = {
            MarketSession.ASIAN: self._is_asian_session_active(hour),
            MarketSession.EUROPEAN: self._is_european_session_active(hour), 
            MarketSession.AMERICAN: self._is_american_session_active(hour)
        }
    
    def _is_asian_session_active(self, utc_hour: int) -> bool:
        """Check if Asian session is active (23:00-08:00 UTC)"""
        return utc_hour >= 23 or utc_hour <= 8
    
    def _is_european_session_active(self, utc_hour: int) -> bool:
        """Check if European session is active (07:00-16:00 UTC)"""
        return 7 <= utc_hour <= 16
    
    def _is_american_session_active(self, utc_hour: int) -> bool:
        """Check if American session is active (13:00-22:00 UTC)"""
        return 13 <= utc_hour <= 22
    
    async def validate_order(self, order: GlobalOrder) -> Dict[str, Any]:
        """Validate global order for routing"""
        validation_errors = []
        
        try:
            # Basic validation
            if order.quantity <= 0:
                validation_errors.append("Order quantity must be positive")
            
            if order.order_type != 'market' and (not order.price or order.price <= 0):
                validation_errors.append("Limit orders must have positive price")
            
            # Currency validation
            if order.currency not in Currency:
                validation_errors.append(f"Unsupported currency: {order.currency}")
            
            # Market validation
            routing_rule = await self._get_routing_rule(order.symbol)
            if not routing_rule:
                validation_errors.append(f"No routing rule found for symbol: {order.symbol}")
            
            # Session validation
            if routing_rule:
                required_sessions = routing_rule.get('sessions', [])
                active_sessions = [s for s, active in self.market_sessions.items() if active]
                
                if not any(session in active_sessions for session in required_sessions):
                    validation_errors.append(f"Target market not currently active")
            
            return {
                'valid': len(validation_errors) == 0,
                'errors': validation_errors,
                'routing_rule': routing_rule
            }
            
        except Exception as e:
            logger.error("Order validation failed", error=str(e))
            return {
                'valid': False,
                'errors': [f"Validation error: {str(e)}"],
                'routing_rule': None
            }
    
    async def route_order(self, order_dict: Dict[str, Any]):
        """Route order to appropriate market"""
        try:
            order = GlobalOrder(**order_dict)
            
            # Get routing rule
            routing_rule = await self._get_routing_rule(order.symbol)
            if not routing_rule:
                raise ValueError(f"No routing rule for {order.symbol}")
            
            # Determine target market
            target_market = routing_rule['primary_market']
            
            # Check if currency conversion needed
            if order.currency != routing_rule['currencies'][0]:
                await self._handle_currency_conversion(order, routing_rule['currencies'][0])
            
            # Route to target market
            await self._send_to_market(order, target_market)
            
            logger.info(f"Order {order.order_id} routed to {target_market}")
            
        except Exception as e:
            logger.error("Order routing failed", error=str(e))
            raise
    
    async def _get_routing_rule(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get routing rule for symbol"""
        # Simplified symbol classification
        if 'UST' in symbol or 'TREASURY' in symbol:
            return self.routing_rules['US_TREASURIES']
        elif 'GILT' in symbol or 'UKT' in symbol:
            return self.routing_rules['UK_GILTS']
        elif 'BUND' in symbol or 'DBR' in symbol:
            return self.routing_rules['GERMAN_BUNDS']
        elif 'JGB' in symbol:
            return self.routing_rules['JAPANESE_BONDS']
        elif 'SGS' in symbol:
            return self.routing_rules['SINGAPORE_BONDS']
        
        return None
    
    async def _handle_currency_conversion(self, order: GlobalOrder, target_currency: Currency):
        """Handle currency conversion for cross-currency orders"""
        logger.info(f"Currency conversion needed: {order.currency} -> {target_currency}")
        # This would integrate with FX service
        # For now, just log the requirement
        
    async def _send_to_market(self, order: GlobalOrder, market: str):
        """Send order to target market"""
        # This would integrate with market-specific adapters
        logger.info(f"Sending order {order.order_id} to {market}")
        
        # Store order in database
        await self.db.store_order(order.dict())
        
    async def update_session_routing(self, active_sessions: set):
        """Update routing based on active sessions"""
        self.market_sessions = {
            session: session in active_sessions 
            for session in MarketSession
        }
        logger.info(f"Updated active sessions: {active_sessions}")
