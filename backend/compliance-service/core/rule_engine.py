import asyncio
import json
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import structlog

logger = structlog.get_logger()

class RuleType(Enum):
    POSITION_LIMIT = "position_limit"
    CONCENTRATION_LIMIT = "concentration_limit"
    TRANSACTION_LIMIT = "transaction_limit"
    TRADING_RESTRICTION = "trading_restriction"
    DISCLOSURE_REQUIREMENT = "disclosure_requirement"
    REPORTING_REQUIREMENT = "reporting_requirement"

class RuleSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    VIOLATION = "violation"
    CRITICAL = "critical"

@dataclass
class ComplianceRule:
    rule_id: str
    name: str
    description: str
    rule_type: RuleType
    regulation_source: str  # SEBI, RBI, FEMA, Internal
    parameters: Dict[str, Any]
    condition_logic: str
    action_required: str
    severity: RuleSeverity
    active: bool = True
    created_at: datetime = None
    updated_at: datetime = None

class RuleEngine:
    """Advanced compliance rule engine for regulatory monitoring"""
    
    def __init__(self, settings):
        self.settings = settings
        self.rules = {}
        self.rule_evaluators = {}
        self.violation_history = []
        
    async def initialize(self):
        """Initialize rule engine with predefined rules"""
        logger.info("Initializing Compliance Rule Engine")
        await self._load_regulatory_rules()
        await self._setup_rule_evaluators()
        
    async def _load_regulatory_rules(self):
        """Load predefined regulatory compliance rules"""
        # SEBI Rules
        sebi_rules = [
            ComplianceRule(
                rule_id="SEBI_001",
                name="Large Position Disclosure",
                description="Disclosure required for positions >5% of outstanding",
                rule_type=RuleType.DISCLOSURE_REQUIREMENT,
                regulation_source="SEBI",
                parameters={"threshold_percentage": 5.0, "disclosure_period_days": 2},
                condition_logic="position_percentage > threshold_percentage",
                action_required="File disclosure within 2 working days",
                severity=RuleSeverity.VIOLATION
            ),
            ComplianceRule(
                rule_id="SEBI_002", 
                name="Insider Trading Prevention",
                description="Trading restrictions during sensitive periods",
                rule_type=RuleType.TRADING_RESTRICTION,
                regulation_source="SEBI",
                parameters={"blackout_periods": ["earnings", "material_events"], "restriction_days": 30},
                condition_logic="current_date in blackout_period",
                action_required="Block trading during restriction period",
                severity=RuleSeverity.CRITICAL
            ),
            ComplianceRule(
                rule_id="SEBI_003",
                name="Portfolio Concentration Limit",
                description="Single issuer exposure limit for mutual funds",
                rule_type=RuleType.CONCENTRATION_LIMIT,
                regulation_source="SEBI",
                parameters={"max_single_issuer_percentage": 10.0, "fund_type": "debt_fund"},
                condition_logic="single_issuer_exposure > max_single_issuer_percentage",
                action_required="Reduce exposure or seek exemption",
                severity=RuleSeverity.VIOLATION
            )
        ]
        
        # RBI Rules
        rbi_rules = [
            ComplianceRule(
                rule_id="RBI_001",
                name="Bank Investment Limit",
                description="Banks' investment in corporate bonds limit",
                rule_type=RuleType.POSITION_LIMIT,
                regulation_source="RBI",
                parameters={"max_corporate_bond_percentage": 10.0, "entity_type": "bank"},
                condition_logic="corporate_bond_exposure > max_corporate_bond_percentage",
                action_required="Reduce corporate bond holdings",
                severity=RuleSeverity.VIOLATION
            ),
            ComplianceRule(
                rule_id="RBI_002",
                name="Liquidity Coverage Ratio",
                description="Minimum liquidity requirement for banks",
                rule_type=RuleType.POSITION_LIMIT,
                regulation_source="RBI", 
                parameters={"min_lcr_percentage": 100.0, "entity_type": "bank"},
                condition_logic="liquidity_coverage_ratio < min_lcr_percentage",
                action_required="Increase liquid assets",
                severity=RuleSeverity.CRITICAL
            )
        ]
        
        # FEMA Rules
        fema_rules = [
            ComplianceRule(
                rule_id="FEMA_001",
                name="Foreign Investment Limit",
                description="FPI investment limits in debt securities",
                rule_type=RuleType.POSITION_LIMIT,
                regulation_source="FEMA",
                parameters={"max_fpi_debt_percentage": 6.0, "investor_type": "fpi"},
                condition_logic="fpi_debt_investment > max_fpi_debt_percentage",
                action_required="Comply with FPI limits",
                severity=RuleSeverity.VIOLATION
            )
        ]
        
        # Internal Rules
        internal_rules = [
            ComplianceRule(
                rule_id="INT_001",
                name="Daily Trading Limit",
                description="Maximum daily trading volume limit",
                rule_type=RuleType.TRANSACTION_LIMIT,
                regulation_source="Internal",
                parameters={"max_daily_volume": 1000000000, "currency": "INR"},
                condition_logic="daily_trading_volume > max_daily_volume", 
                action_required="Review large trading activity",
                severity=RuleSeverity.WARNING
            ),
            ComplianceRule(
                rule_id="INT_002",
                name="After Hours Trading",
                description="Restriction on after-hours trading",
                rule_type=RuleType.TRADING_RESTRICTION,
                regulation_source="Internal",
                parameters={"market_hours": {"start": "09:00", "end": "15:30"}, "timezone": "Asia/Kolkata"},
                condition_logic="current_time outside market_hours",
                action_required="Block after-hours trading",
                severity=RuleSeverity.WARNING
            )
        ]
        
        # Store all rules
        all_rules = sebi_rules + rbi_rules + fema_rules + internal_rules
        for rule in all_rules:
            rule.created_at = datetime.utcnow()
            rule.updated_at = datetime.utcnow()
            self.rules[rule.rule_id] = rule
            
        logger.info(f"Loaded {len(all_rules)} compliance rules")
    
    async def _setup_rule_evaluators(self):
        """Setup rule evaluation functions"""
        self.rule_evaluators = {
            RuleType.POSITION_LIMIT: self._evaluate_position_limit,
            RuleType.CONCENTRATION_LIMIT: self._evaluate_concentration_limit,
            RuleType.TRANSACTION_LIMIT: self._evaluate_transaction_limit,
            RuleType.TRADING_RESTRICTION: self._evaluate_trading_restriction,
            RuleType.DISCLOSURE_REQUIREMENT: self._evaluate_disclosure_requirement,
            RuleType.REPORTING_REQUIREMENT: self._evaluate_reporting_requirement
        }
    
    async def evaluate_transaction(self, transaction: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evaluate a transaction against all applicable rules"""
        violations = []
        
        try:
            for rule_id, rule in self.rules.items():
                if not rule.active:
                    continue
                    
                evaluator = self.rule_evaluators.get(rule.rule_type)
                if not evaluator:
                    logger.warning(f"No evaluator found for rule type {rule.rule_type}")
                    continue
                
                try:
                    violation = await evaluator(rule, transaction)
                    if violation:
                        violations.append(violation)
                        
                except Exception as e:
                    logger.error(f"Rule evaluation failed for {rule_id}", error=str(e))
                    
        except Exception as e:
            logger.error("Transaction evaluation failed", error=str(e))
            
        return violations
    
    async def _evaluate_position_limit(self, rule: ComplianceRule, transaction: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Evaluate position limit rules"""
        try:
            # Get current portfolio state after transaction
            portfolio_data = await self._get_post_transaction_portfolio(transaction)
            
            if rule.rule_id == "RBI_001":  # Bank corporate bond limit
                entity_type = portfolio_data.get('entity_type')
                if entity_type != 'bank':
                    return None
                    
                corporate_bond_exposure = portfolio_data.get('corporate_bond_percentage', 0)
                max_allowed = rule.parameters['max_corporate_bond_percentage']
                
                if corporate_bond_exposure > max_allowed:
                    return {
                        'rule_id': rule.rule_id,
                        'rule_name': rule.name,
                        'violation_type': 'position_limit_breach',
                        'severity': rule.severity.value,
                        'current_value': corporate_bond_exposure,
                        'limit_value': max_allowed,
                        'description': f"Corporate bond exposure ({corporate_bond_exposure:.1f}%) exceeds RBI limit ({max_allowed:.1f}%)",
                        'action_required': rule.action_required,
                        'regulation_source': rule.regulation_source,
                        'transaction_id': transaction.get('id'),
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    
            elif rule.rule_id == "RBI_002":  # LCR requirement
                entity_type = portfolio_data.get('entity_type')
                if entity_type != 'bank':
                    return None
                    
                lcr = portfolio_data.get('liquidity_coverage_ratio', 0)
                min_required = rule.parameters['min_lcr_percentage']
                
                if lcr < min_required:
                    return {
                        'rule_id': rule.rule_id,
                        'rule_name': rule.name,
                        'violation_type': 'liquidity_requirement_breach',
                        'severity': rule.severity.value,
                        'current_value': lcr,
                        'limit_value': min_required,
                        'description': f"LCR ({lcr:.1f}%) below RBI minimum ({min_required:.1f}%)",
                        'action_required': rule.action_required,
                        'regulation_source': rule.regulation_source,
                        'transaction_id': transaction.get('id'),
                        'timestamp': datetime.utcnow().isoformat()
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Position limit evaluation failed for {rule.rule_id}", error=str(e))
            return None
    
    async def _evaluate_concentration_limit(self, rule: ComplianceRule, transaction: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Evaluate concentration limit rules"""
        try:
            portfolio_data = await self._get_post_transaction_portfolio(transaction)
            
            if rule.rule_id == "SEBI_003":  # Portfolio concentration limit
                fund_type = portfolio_data.get('fund_type')
                if fund_type != 'debt_fund':
                    return None
                
                max_single_issuer = portfolio_data.get('max_single_issuer_percentage', 0)
                limit = rule.parameters['max_single_issuer_percentage']
                
                if max_single_issuer > limit:
                    return {
                        'rule_id': rule.rule_id,
                        'rule_name': rule.name,
                        'violation_type': 'concentration_limit_breach',
                        'severity': rule.severity.value,
                        'current_value': max_single_issuer,
                        'limit_value': limit,
                        'description': f"Single issuer exposure ({max_single_issuer:.1f}%) exceeds SEBI limit ({limit:.1f}%)",
                        'action_required': rule.action_required,
                        'regulation_source': rule.regulation_source,
                        'transaction_id': transaction.get('id'),
                        'timestamp': datetime.utcnow().isoformat()
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Concentration limit evaluation failed for {rule.rule_id}", error=str(e))
            return None
    
    async def _evaluate_transaction_limit(self, rule: ComplianceRule, transaction: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Evaluate transaction limit rules"""
        try:
            if rule.rule_id == "INT_001":  # Daily trading limit
                daily_volume = await self._get_daily_trading_volume(transaction.get('account_id', ''))
                transaction_value = transaction.get('quantity', 0) * transaction.get('price', 0)
                projected_volume = daily_volume + transaction_value
                
                max_volume = rule.parameters['max_daily_volume']
                
                if projected_volume > max_volume:
                    return {
                        'rule_id': rule.rule_id,
                        'rule_name': rule.name,
                        'violation_type': 'daily_limit_breach',
                        'severity': rule.severity.value,
                        'current_value': projected_volume,
                        'limit_value': max_volume,
                        'description': f"Daily trading volume ({projected_volume:,.0f}) would exceed limit ({max_volume:,.0f})",
                        'action_required': rule.action_required,
                        'regulation_source': rule.regulation_source,
                        'transaction_id': transaction.get('id'),
                        'timestamp': datetime.utcnow().isoformat()
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Transaction limit evaluation failed for {rule.rule_id}", error=str(e))
            return None
    
    async def _evaluate_trading_restriction(self, rule: ComplianceRule, transaction: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Evaluate trading restriction rules"""
        try:
            if rule.rule_id == "INT_002":  # After hours trading
                current_time = datetime.now().time()
                market_start = datetime.strptime(rule.parameters['market_hours']['start'], '%H:%M').time()
                market_end = datetime.strptime(rule.parameters['market_hours']['end'], '%H:%M').time()
                
                if not (market_start <= current_time <= market_end):
                    return {
                        'rule_id': rule.rule_id,
                        'rule_name': rule.name,
                        'violation_type': 'trading_restriction_breach',
                        'severity': rule.severity.value,
                        'current_value': current_time.strftime('%H:%M'),
                        'limit_value': f"{market_start.strftime('%H:%M')}-{market_end.strftime('%H:%M')}",
                        'description': f"Trading attempted outside market hours ({current_time.strftime('%H:%M')})",
                        'action_required': rule.action_required,
                        'regulation_source': rule.regulation_source,
                        'transaction_id': transaction.get('id'),
                        'timestamp': datetime.utcnow().isoformat()
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Trading restriction evaluation failed for {rule.rule_id}", error=str(e))
            return None
    
    async def _evaluate_disclosure_requirement(self, rule: ComplianceRule, transaction: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Evaluate disclosure requirement rules"""
        try:
            if rule.rule_id == "SEBI_001":  # Large position disclosure
                # Calculate position percentage after transaction
                post_transaction_percentage = await self._calculate_position_percentage_after_transaction(transaction)
                threshold = rule.parameters['threshold_percentage']
                
                if post_transaction_percentage > threshold:
                    # Check if disclosure already filed
                    disclosure_filed = await self._check_disclosure_status(transaction)
                    
                    if not disclosure_filed:
                        return {
                            'rule_id': rule.rule_id,
                            'rule_name': rule.name,
                            'violation_type': 'disclosure_requirement',
                            'severity': rule.severity.value,
                            'current_value': post_transaction_percentage,
                            'limit_value': threshold,
                            'description': f"Position ({post_transaction_percentage:.1f}%) requires disclosure (threshold: {threshold:.1f}%)",
                            'action_required': rule.action_required,
                            'regulation_source': rule.regulation_source,
                            'transaction_id': transaction.get('id'),
                            'timestamp': datetime.utcnow().isoformat(),
                            'due_date': (datetime.utcnow() + timedelta(days=rule.parameters['disclosure_period_days'])).isoformat()
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"Disclosure requirement evaluation failed for {rule.rule_id}", error=str(e))
            return None
    
    async def _evaluate_reporting_requirement(self, rule: ComplianceRule, transaction: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Evaluate reporting requirement rules"""
        # Placeholder for reporting requirements
        return None
    
    async def _get_post_transaction_portfolio(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Get portfolio state after applying transaction"""
        # Placeholder - would calculate portfolio metrics after transaction
        return {
            'entity_type': 'bank',
            'fund_type': 'debt_fund',
            'corporate_bond_percentage': 8.5,
            'liquidity_coverage_ratio': 105.0,
            'max_single_issuer_percentage': 12.0
        }
    
    async def _get_daily_trading_volume(self, account_id: str) -> float:
        """Get current daily trading volume"""
        # Placeholder - would query database for today's volume
        return 50000000.0  # 50M
    
    async def _calculate_position_percentage_after_transaction(self, transaction: Dict[str, Any]) -> float:
        """Calculate position percentage after transaction"""
        # Placeholder - would calculate actual position percentage
        return 6.5  # 6.5%
    
    async def _check_disclosure_status(self, transaction: Dict[str, Any]) -> bool:
        """Check if required disclosure has been filed"""
        # Placeholder - would check disclosure database
        return False
    
    async def get_active_rules(self) -> List[Dict[str, Any]]:
        """Get all active compliance rules"""
        active_rules = []
        
        for rule_id, rule in self.rules.items():
            if rule.active:
                active_rules.append({
                    'rule_id': rule.rule_id,
                    'name': rule.name,
                    'description': rule.description,
                    'rule_type': rule.rule_type.value,
                    'regulation_source': rule.regulation_source,
                    'severity': rule.severity.value,
                    'parameters': rule.parameters,
                    'created_at': rule.created_at.isoformat() if rule.created_at else None,
                    'updated_at': rule.updated_at.isoformat() if rule.updated_at else None
                })
        
        return active_rules
    
    async def add_custom_rule(self, rule_data: Dict[str, Any]) -> str:
        """Add a custom compliance rule"""
        try:
            rule = ComplianceRule(
                rule_id=rule_data['rule_id'],
                name=rule_data['name'],
                description=rule_data['description'],
                rule_type=RuleType(rule_data['rule_type']),
                regulation_source=rule_data.get('regulation_source', 'Internal'),
                parameters=rule_data.get('parameters', {}),
                condition_logic=rule_data.get('condition_logic', ''),
                action_required=rule_data.get('action_required', ''),
                severity=RuleSeverity(rule_data.get('severity', 'warning')),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.rules[rule.rule_id] = rule
            logger.info(f"Added custom rule: {rule.rule_id}")
            
            return rule.rule_id
            
        except Exception as e:
            logger.error("Failed to add custom rule", error=str(e))
            raise
    
    async def deactivate_rule(self, rule_id: str):
        """Deactivate a compliance rule"""
        if rule_id in self.rules:
            self.rules[rule_id].active = False
            self.rules[rule_id].updated_at = datetime.utcnow()
            logger.info(f"Deactivated rule: {rule_id}")
        else:
            raise ValueError(f"Rule {rule_id} not found")
