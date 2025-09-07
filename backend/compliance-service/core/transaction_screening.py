import asyncio
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import structlog

logger = structlog.get_logger()

class TransactionScreening:
    """Advanced transaction screening for AML and compliance"""
    
    def __init__(self, settings):
        self.settings = settings
        self.screening_rules = {}
        self.blacklists = {}
        self.pattern_matchers = {}
        
    async def initialize(self):
        """Initialize screening engine"""
        logger.info("Initializing Transaction Screening Engine")
        await self._load_screening_rules()
        await self._load_blacklists()
        await self._compile_pattern_matchers()
        
    async def _load_screening_rules(self):
        """Load transaction screening rules"""
        self.screening_rules = {
            'large_transaction': {
                'threshold': self.settings.suspicious_transaction_threshold,
                'severity': 'warning',
                'description': 'Large transaction requiring review'
            },
            'frequent_transactions': {
                'count_threshold': 10,
                'time_window_minutes': 60,
                'severity': 'warning',
                'description': 'Multiple transactions in short time'
            },
            'round_number_transactions': {
                'pattern': r'^[1-9]0{4,}$',  # Round numbers like 10000, 100000
                'severity': 'info',
                'description': 'Round number transaction'
            },
            'unusual_counterparty': {
                'severity': 'violation',
                'description': 'Transaction with flagged counterparty'
            },
            'cross_border': {
                'severity': 'warning',
                'description': 'Cross-border transaction requiring documentation'
            },
            'structuring': {
                'threshold': 500000,  # 5L INR
                'pattern_window_hours': 24,
                'severity': 'critical',
                'description': 'Potential structuring activity'
            }
        }
    
    async def _load_blacklists(self):
        """Load blacklists and watchlists"""
        # In production, these would be loaded from databases or external APIs
        self.blacklists = {
            'sanctioned_entities': [
                'SANCTIONED_ENTITY_1',
                'SANCTIONED_ENTITY_2'
            ],
            'pep_list': [  # Politically Exposed Persons
                'PEP_PERSON_1',
                'PEP_PERSON_2'
            ],
            'high_risk_countries': [
                'AF',  # Afghanistan
                'IR',  # Iran
                'KP',  # North Korea
            ],
            'blocked_accounts': []
        }
    
    async def _compile_pattern_matchers(self):
        """Compile regex patterns for screening"""
        self.pattern_matchers = {
            'round_numbers': re.compile(r'^[1-9]0{4,}$'),
            'sequential_amounts': re.compile(r'(\d)\1{3,}'),  # 1111, 2222, etc.
        }
    
    async def screen_transaction(self, transaction: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Screen a single transaction"""
        violations = []
        
        try:
            # Large transaction screening
            violations.extend(await self._screen_large_transaction(transaction))
            
            # Counterparty screening
            violations.extend(await self._screen_counterparty(transaction))
            
            # Pattern-based screening
            violations.extend(await self._screen_patterns(transaction))
            
            # Frequency screening
            violations.extend(await self._screen_frequency(transaction))
            
            # Geographic screening
            violations.extend(await self._screen_geography(transaction))
            
            # Structuring detection
            violations.extend(await self._screen_structuring(transaction))
            
            return violations
            
        except Exception as e:
            logger.error(f"Transaction screening failed for {transaction.get('id')}", error=str(e))
            return []
    
    async def _screen_large_transaction(self, transaction: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Screen for large transactions"""
        violations = []
        
        amount = transaction.get('amount', 0)
        threshold = self.screening_rules['large_transaction']['threshold']
        
        if amount >= threshold:
            violations.append({
                'rule_type': 'large_transaction',
                'severity': 'warning',
                'description': f'Large transaction amount: {amount:,.2f} (threshold: {threshold:,.2f})',
                'transaction_id': transaction.get('id'),
                'amount': amount,
                'threshold': threshold,
                'timestamp': datetime.utcnow().isoformat()
            })
        
        return violations
    
    async def _screen_counterparty(self, transaction: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Screen counterparty against blacklists"""
        violations = []
        
        counterparty = transaction.get('counterparty', '').upper()
        counterparty_country = transaction.get('counterparty_country', '')
        
        # Check sanctioned entities
        if counterparty in self.blacklists['sanctioned_entities']:
            violations.append({
                'rule_type': 'sanctioned_entity',
                'severity': 'critical',
                'description': f'Transaction with sanctioned entity: {counterparty}',
                'transaction_id': transaction.get('id'),
                'counterparty': counterparty,
                'timestamp': datetime.utcnow().isoformat()
            })
        
        # Check PEP list
        if counterparty in self.blacklists['pep_list']:
            violations.append({
                'rule_type': 'pep_transaction',
                'severity': 'warning',
                'description': f'Transaction with PEP: {counterparty}',
                'transaction_id': transaction.get('id'),
                'counterparty': counterparty,
                'timestamp': datetime.utcnow().isoformat()
            })
        
        # Check high-risk countries
        if counterparty_country in self.blacklists['high_risk_countries']:
            violations.append({
                'rule_type': 'high_risk_country',
                'severity': 'warning',
                'description': f'Transaction with high-risk country: {counterparty_country}',
                'transaction_id': transaction.get('id'),
                'country': counterparty_country,
                'timestamp': datetime.utcnow().isoformat()
            })
        
        return violations
    
    async def _screen_patterns(self, transaction: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Screen for suspicious patterns"""
        violations = []
        
        amount = str(int(transaction.get('amount', 0)))
        
        # Check for round numbers
        if self.pattern_matchers['round_numbers'].match(amount):
            violations.append({
                'rule_type': 'round_number_transaction',
                'severity': 'info',
                'description': f'Round number transaction: {amount}',
                'transaction_id': transaction.get('id'),
                'amount': transaction.get('amount'),
                'timestamp': datetime.utcnow().isoformat()
            })
        
        return violations
    
    async def _screen_frequency(self, transaction: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Screen for frequency-based violations"""
        violations = []
        
        # This would require database access to check recent transactions
        # For now, return empty list
        return violations
    
    async def _screen_geography(self, transaction: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Screen for geographic risk"""
        violations = []
        
        counterparty_country = transaction.get('counterparty_country')
        if counterparty_country and counterparty_country != 'IN':
            violations.append({
                'rule_type': 'cross_border_transaction',
                'severity': 'info',
                'description': f'Cross-border transaction to {counterparty_country}',
                'transaction_id': transaction.get('id'),
                'country': counterparty_country,
                'timestamp': datetime.utcnow().isoformat()
            })
        
        return violations
    
    async def _screen_structuring(self, transaction: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Screen for potential structuring (smurfing)"""
        violations = []
        
        # This would require complex analysis of transaction patterns
        # For now, return empty list
        return violations
    
    async def screen_batch(self, transactions: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Screen multiple transactions"""
        results = {}
        
        for transaction in transactions:
            transaction_id = transaction.get('id', 'unknown')
            try:
                violations = await self.screen_transaction(transaction)
                results[transaction_id] = violations
                
                if violations:
                    logger.info(f"Found {len(violations)} violations for transaction {transaction_id}")
                    
            except Exception as e:
                logger.error(f"Failed to screen transaction {transaction_id}", error=str(e))
                results[transaction_id] = []
        
        return results
    
    async def add_to_blacklist(self, list_name: str, entity: str):
        """Add entity to blacklist"""
        if list_name in self.blacklists:
            if entity not in self.blacklists[list_name]:
                self.blacklists[list_name].append(entity.upper())
                logger.info(f"Added {entity} to {list_name}")
    
    async def remove_from_blacklist(self, list_name: str, entity: str):
        """Remove entity from blacklist"""
        if list_name in self.blacklists:
            try:
                self.blacklists[list_name].remove(entity.upper())
                logger.info(f"Removed {entity} from {list_name}")
            except ValueError:
                logger.warning(f"Entity {entity} not found in {list_name}")
