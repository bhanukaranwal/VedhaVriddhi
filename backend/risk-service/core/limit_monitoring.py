import asyncio
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import structlog

logger = structlog.get_logger()

class LimitMonitoringEngine:
    """Real-time risk limit monitoring and enforcement"""
    
    def __init__(self, settings):
        self.settings = settings
        self.active_limits = {}
        self.violation_history = []
        
    async def initialize(self):
        """Initialize limit monitoring engine"""
        logger.info("Initializing Limit Monitoring Engine")
        await self._load_risk_limits()
        
    async def _load_risk_limits(self):
        """Load risk limits from database"""
        # Default risk limits by portfolio type
        self.active_limits = {
            'var_limits': {
                'institutional': {'var_95_1d': 5000000, 'var_99_1d': 8000000},
                'retail': {'var_95_1d': 1000000, 'var_99_1d': 1500000},
                'hedge_fund': {'var_95_1d': 20000000, 'var_99_1d': 35000000}
            },
            'concentration_limits': {
                'single_issuer': 0.15,  # 15%
                'single_sector': 0.25,  # 25%
                'single_rating': 0.40,  # 40%
                'single_maturity_bucket': 0.30  # 30%
            },
            'exposure_limits': {
                'total_portfolio': 500000000,  # 500M
                'leverage_ratio': 3.0,
                'duration_limit': 15.0,
                'credit_exposure': 200000000  # 200M
            },
            'liquidity_limits': {
                'min_liquidity_ratio': 0.20,  # 20% liquid assets
                'max_illiquid_exposure': 0.50,  # 50% max illiquid
                'days_to_liquidate_90pct': 30  # 30 days max
            }
        }
        
    async def check_all_limits(self):
        """Check all active portfolios against limits"""
        try:
            portfolio_ids = await self._get_active_portfolios()
            
            for portfolio_id in portfolio_ids:
                violations = await self.check_portfolio_limits(portfolio_id)
                
                if violations:
                    await self._handle_limit_violations(portfolio_id, violations)
                    
        except Exception as e:
            logger.error("Limit checking failed", error=str(e))
    
    async def check_portfolio_limits(self, portfolio_id: str) -> List[Dict[str, Any]]:
        """Check all limits for a specific portfolio"""
        try:
            violations = []
            
            # Get portfolio data
            portfolio_data = await self._get_portfolio_data(portfolio_id)
            if not portfolio_data:
                return violations
            
            # Check VaR limits
            var_violations = await self._check_var_limits(portfolio_id, portfolio_data)
            violations.extend(var_violations)
            
            # Check concentration limits
            concentration_violations = await self._check_concentration_limits(portfolio_id, portfolio_data)
            violations.extend(concentration_violations)
            
            # Check exposure limits
            exposure_violations = await self._check_exposure_limits(portfolio_id, portfolio_data)
            violations.extend(exposure_violations)
            
            # Check liquidity limits
            liquidity_violations = await self._check_liquidity_limits(portfolio_id, portfolio_data)
            violations.extend(liquidity_violations)
            
            return violations
            
        except Exception as e:
            logger.error(f"Portfolio limit check failed for {portfolio_id}", error=str(e))
            return []
    
    async def _check_var_limits(self, portfolio_id: str, portfolio_data: Dict) -> List[Dict[str, Any]]:
        """Check VaR limits"""
        violations = []
        
        try:
            portfolio_type = portfolio_data.get('type', 'institutional')
            var_limits = self.active_limits['var_limits'].get(portfolio_type, {})
            
            current_var_95 = portfolio_data.get('var_95_1d', 0)
            current_var_99 = portfolio_data.get('var_99_1d', 0)
            
            # Check 95% VaR limit
            var_95_limit = var_limits.get('var_95_1d', float('inf'))
            if current_var_95 > var_95_limit:
                violations.append({
                    'type': 'var_limit_breach',
                    'severity': 'high',
                    'limit_type': 'var_95_1d',
                    'current_value': current_var_95,
                    'limit_value': var_95_limit,
                    'utilization': (current_var_95 / var_95_limit) * 100,
                    'description': f'VaR 95% ({current_var_95:,.0f}) exceeds limit ({var_95_limit:,.0f})'
                })
            
            # Check 99% VaR limit  
            var_99_limit = var_limits.get('var_99_1d', float('inf'))
            if current_var_99 > var_99_limit:
                violations.append({
                    'type': 'var_limit_breach',
                    'severity': 'critical',
                    'limit_type': 'var_99_1d',
                    'current_value': current_var_99,
                    'limit_value': var_99_limit,
                    'utilization': (current_var_99 / var_99_limit) * 100,
                    'description': f'VaR 99% ({current_var_99:,.0f}) exceeds limit ({var_99_limit:,.0f})'
                })
            
        except Exception as e:
            logger.error("VaR limit check failed", error=str(e))
            
        return violations
    
    async def _check_concentration_limits(self, portfolio_id: str, portfolio_data: Dict) -> List[Dict[str, Any]]:
        """Check concentration limits"""
        violations = []
        
        try:
            positions = portfolio_data.get('positions', [])
            total_value = sum(pos['market_value'] for pos in positions)
            
            if total_value == 0:
                return violations
            
            concentration_limits = self.active_limits['concentration_limits']
            
            # Check issuer concentration
            issuer_exposure = {}
            for pos in positions:
                issuer = pos.get('issuer', 'Unknown')
                issuer_exposure[issuer] = issuer_exposure.get(issuer, 0) + pos['market_value']
            
            max_issuer_exposure = max(issuer_exposure.values()) if issuer_exposure else 0
            max_issuer_pct = max_issuer_exposure / total_value
            
            if max_issuer_pct > concentration_limits['single_issuer']:
                violations.append({
                    'type': 'concentration_limit_breach',
                    'severity': 'medium',
                    'limit_type': 'single_issuer',
                    'current_value': max_issuer_pct,
                    'limit_value': concentration_limits['single_issuer'],
                    'utilization': (max_issuer_pct / concentration_limits['single_issuer']) * 100,
                    'description': f'Single issuer concentration ({max_issuer_pct:.1%}) exceeds limit ({concentration_limits["single_issuer"]:.1%})'
                })
            
            # Check sector concentration
            sector_exposure = {}
            for pos in positions:
                sector = pos.get('sector', 'Unknown')
                sector_exposure[sector] = sector_exposure.get(sector, 0) + pos['market_value']
            
            max_sector_exposure = max(sector_exposure.values()) if sector_exposure else 0
            max_sector_pct = max_sector_exposure / total_value
            
            if max_sector_pct > concentration_limits['single_sector']:
                violations.append({
                    'type': 'concentration_limit_breach',
                    'severity': 'medium',
                    'limit_type': 'single_sector',
                    'current_value': max_sector_pct,
                    'limit_value': concentration_limits['single_sector'],
                    'utilization': (max_sector_pct / concentration_limits['single_sector']) * 100,
                    'description': f'Single sector concentration ({max_sector_pct:.1%}) exceeds limit ({concentration_limits["single_sector"]:.1%})'
                })
            
        except Exception as e:
            logger.error("Concentration limit check failed", error=str(e))
            
        return violations
    
    async def _check_exposure_limits(self, portfolio_id: str, portfolio_data: Dict) -> List[Dict[str, Any]]:
        """Check exposure limits"""
        violations = []
        
        try:
            total_value = portfolio_data.get('total_value', 0)
            notional_exposure = portfolio_data.get('notional_exposure', total_value)
            duration = portfolio_data.get('modified_duration', 0)
            
            exposure_limits = self.active_limits['exposure_limits']
            
            # Check total portfolio limit
            if total_value > exposure_limits['total_portfolio']:
                violations.append({
                    'type': 'exposure_limit_breach',
                    'severity': 'high',
                    'limit_type': 'total_portfolio',
                    'current_value': total_value,
                    'limit_value': exposure_limits['total_portfolio'],
                    'utilization': (total_value / exposure_limits['total_portfolio']) * 100,
                    'description': f'Total portfolio value ({total_value:,.0f}) exceeds limit ({exposure_limits["total_portfolio"]:,.0f})'
                })
            
            # Check leverage ratio
            leverage_ratio = notional_exposure / total_value if total_value > 0 else 0
            if leverage_ratio > exposure_limits['leverage_ratio']:
                violations.append({
                    'type': 'exposure_limit_breach',
                    'severity': 'high',
                    'limit_type': 'leverage_ratio',
                    'current_value': leverage_ratio,
                    'limit_value': exposure_limits['leverage_ratio'],
                    'utilization': (leverage_ratio / exposure_limits['leverage_ratio']) * 100,
                    'description': f'Leverage ratio ({leverage_ratio:.2f}) exceeds limit ({exposure_limits["leverage_ratio"]:.2f})'
                })
            
            # Check duration limit
            if duration > exposure_limits['duration_limit']:
                violations.append({
                    'type': 'exposure_limit_breach',
                    'severity': 'medium',
                    'limit_type': 'duration_limit',
                    'current_value': duration,
                    'limit_value': exposure_limits['duration_limit'],
                    'utilization': (duration / exposure_limits['duration_limit']) * 100,
                    'description': f'Portfolio duration ({duration:.2f}) exceeds limit ({exposure_limits["duration_limit"]:.2f})'
                })
                
        except Exception as e:
            logger.error("Exposure limit check failed", error=str(e))
            
        return violations
    
    async def _check_liquidity_limits(self, portfolio_id: str, portfolio_data: Dict) -> List[Dict[str, Any]]:
        """Check liquidity limits"""
        violations = []
        
        try:
            positions = portfolio_data.get('positions', [])
            total_value = sum(pos['market_value'] for pos in positions)
            
            if total_value == 0:
                return violations
            
            liquidity_limits = self.active_limits['liquidity_limits']
            
            # Calculate liquidity metrics
            liquid_value = sum(pos['market_value'] for pos in positions 
                             if pos.get('liquidity_score', 0.5) >= 0.7)
            liquidity_ratio = liquid_value / total_value
            
            # Check minimum liquidity ratio
            if liquidity_ratio < liquidity_limits['min_liquidity_ratio']:
                violations.append({
                    'type': 'liquidity_limit_breach',
                    'severity': 'high',
                    'limit_type': 'min_liquidity_ratio',
                    'current_value': liquidity_ratio,
                    'limit_value': liquidity_limits['min_liquidity_ratio'],
                    'utilization': (liquidity_ratio / liquidity_limits['min_liquidity_ratio']) * 100,
                    'description': f'Liquidity ratio ({liquidity_ratio:.1%}) below minimum ({liquidity_limits["min_liquidity_ratio"]:.1%})'
                })
                
        except Exception as e:
            logger.error("Liquidity limit check failed", error=str(e))
            
        return violations
    
    async def _handle_limit_violations(self, portfolio_id: str, violations: List[Dict[str, Any]]):
        """Handle limit violations"""
        try:
            for violation in violations:
                # Log violation
                logger.warning(
                    "Risk limit violation detected",
                    portfolio_id=portfolio_id,
                    violation_type=violation['type'],
                    severity=violation['severity'],
                    description=violation['description']
                )
                
                # Store violation history
                violation_record = {
                    'portfolio_id': portfolio_id,
                    'timestamp': datetime.utcnow(),
                    **violation
                }
                self.violation_history.append(violation_record)
                
                # Send alerts based on severity
                if violation['severity'] in ['high', 'critical']:
                    await self._send_violation_alert(portfolio_id, violation)
                    
        except Exception as e:
            logger.error("Failed to handle limit violations", error=str(e))
    
    async def _send_violation_alert(self, portfolio_id: str, violation: Dict[str, Any]):
        """Send violation alert to risk managers"""
        # This would integrate with notification service
        logger.critical(
            "CRITICAL RISK LIMIT VIOLATION",
            portfolio_id=portfolio_id,
            violation=violation
        )
    
    async def _get_active_portfolios(self) -> List[str]:
        """Get list of active portfolio IDs"""
        # Placeholder - would fetch from database
        return ['portfolio-1', 'portfolio-2', 'portfolio-3']
    
    async def _get_portfolio_data(self, portfolio_id: str) -> Dict[str, Any]:
        """Get portfolio data for limit checking"""
        # Placeholder - would fetch comprehensive portfolio data
        return {
            'portfolio_id': portfolio_id,
            'type': 'institutional',
            'total_value': 100000000,
            'notional_exposure': 120000000,
            'var_95_1d': 3000000,
            'var_99_1d': 5000000,
            'modified_duration': 6.5,
            'positions': [
                {
                    'symbol': 'GSEC10Y',
                    'market_value': 50000000,
                    'issuer': 'Government of India',
                    'sector': 'Government',
                    'rating': 'AAA',
                    'liquidity_score': 0.95
                },
                {
                    'symbol': 'CORP5Y_AA',
                    'market_value': 30000000,
                    'issuer': 'Corporation ABC',
                    'sector': 'Financial Services',
                    'rating': 'AA',
                    'liquidity_score': 0.75
                }
            ]
        }
    
    async def get_portfolio_limits(self, portfolio_id: str) -> Dict[str, Any]:
        """Get current limits and utilization for portfolio"""
        try:
            portfolio_data = await self._get_portfolio_data(portfolio_id)
            if not portfolio_data:
                return {}
            
            portfolio_type = portfolio_data.get('type', 'institutional')
            
            limits_status = {
                'var_limits': {},
                'concentration_limits': {},
                'exposure_limits': {},
                'liquidity_limits': {}
            }
            
            # VaR limits status
            var_limits = self.active_limits['var_limits'].get(portfolio_type, {})
            current_var_95 = portfolio_data.get('var_95_1d', 0)
            current_var_99 = portfolio_data.get('var_99_1d', 0)
            
            if 'var_95_1d' in var_limits:
                limits_status['var_limits']['var_95_1d'] = {
                    'current': current_var_95,
                    'limit': var_limits['var_95_1d'],
                    'utilization': (current_var_95 / var_limits['var_95_1d']) * 100,
                    'status': 'green' if current_var_95 <= var_limits['var_95_1d'] * 0.8 else 
                             'yellow' if current_var_95 <= var_limits['var_95_1d'] else 'red'
                }
            
            return limits_status
            
        except Exception as e:
            logger.error(f"Failed to get portfolio limits for {portfolio_id}", error=str(e))
            return {}
