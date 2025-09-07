import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import structlog

from database.timeseries_db import TimeSeriesDB
from database.analytics_db import AnalyticsDB
from models import PortfolioAnalytics, PerformanceAttribution

logger = structlog.get_logger()

class AnalyticsEngine:
    """Core Analytics Engine for VedhaVriddhi"""
    
    def __init__(self, settings):
        self.settings = settings
        self.timeseries_db = TimeSeriesDB(settings)
        self.analytics_db = AnalyticsDB(settings)
        self.cache = {}
        
    async def initialize(self):
        """Initialize analytics engine"""
        logger.info("Initializing Analytics Engine")
        await self.timeseries_db.initialize()
        await self.analytics_db.initialize()
        
    async def stop(self):
        """Stop analytics engine"""
        await self.timeseries_db.close()
        await self.analytics_db.close()
        
    async def get_portfolio_analytics(self, portfolio_id: str) -> Dict[str, Any]:
        """Get comprehensive portfolio analytics"""
        try:
            # Check cache first
            cache_key = f"portfolio_analytics_{portfolio_id}"
            if cache_key in self.cache:
                cached_data = self.cache[cache_key]
                if (datetime.utcnow() - cached_data['timestamp']).seconds < 300:  # 5 min cache
                    return cached_data['data']
            
            # Fetch portfolio data
            positions = await self.timeseries_db.get_portfolio_positions(portfolio_id)
            if not positions:
                return {"error": "No positions found for portfolio"}
            
            # Calculate analytics
            analytics = await self._calculate_portfolio_analytics(portfolio_id, positions)
            
            # Cache results
            self.cache[cache_key] = {
                'data': analytics,
                'timestamp': datetime.utcnow()
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get portfolio analytics for {portfolio_id}", error=str(e))
            raise
            
    async def _calculate_portfolio_analytics(self, portfolio_id: str, positions: List[Dict]) -> Dict[str, Any]:
        """Calculate comprehensive portfolio analytics"""
        try:
            # Portfolio summary
            total_value = sum(pos['market_value'] for pos in positions)
            total_pnl = sum(pos['unrealized_pnl'] + pos['realized_pnl'] for pos in positions)
            
            # Asset allocation breakdown
            allocation = self._calculate_allocation_breakdown(positions)
            
            # Risk metrics
            risk_metrics = await self._calculate_portfolio_risk(portfolio_id, positions)
            
            # Performance metrics
            performance = await self._calculate_performance_metrics(portfolio_id)
            
            # Duration and convexity
            duration_metrics = self._calculate_duration_metrics(positions)
            
            # Credit quality analysis
            credit_analysis = self._calculate_credit_metrics(positions)
            
            return {
                'portfolio_id': portfolio_id,
                'summary': {
                    'total_value': total_value,
                    'total_pnl': total_pnl,
                    'position_count': len(positions),
                    'last_updated': datetime.utcnow().isoformat()
                },
                'allocation': allocation,
                'risk_metrics': risk_metrics,
                'performance': performance,
                'duration_metrics': duration_metrics,
                'credit_analysis': credit_analysis
            }
            
        except Exception as e:
            logger.error("Portfolio analytics calculation failed", error=str(e))
            raise
    
    def _calculate_allocation_breakdown(self, positions: List[Dict]) -> Dict[str, Any]:
        """Calculate portfolio allocation breakdown"""
        total_value = sum(pos['market_value'] for pos in positions)
        
        if total_value == 0:
            return {}
        
        # By instrument type
        by_instrument = {}
        for pos in positions:
            inst_type = pos.get('instrument_type', 'unknown')
            if inst_type not in by_instrument:
                by_instrument[inst_type] = {'value': 0, 'count': 0}
            by_instrument[inst_type]['value'] += pos['market_value']
            by_instrument[inst_type]['count'] += 1
        
        # Convert to percentages
        for inst_type in by_instrument:
            by_instrument[inst_type]['percentage'] = (
                by_instrument[inst_type]['value'] / total_value * 100
            )
        
        # By sector
        by_sector = {}
        for pos in positions:
            sector = pos.get('sector', 'unknown')
            if sector not in by_sector:
                by_sector[sector] = {'value': 0, 'count': 0}
            by_sector[sector]['value'] += pos['market_value']
            by_sector[sector]['count'] += 1
        
        for sector in by_sector:
            by_sector[sector]['percentage'] = (
                by_sector[sector]['value'] / total_value * 100
            )
        
        # By rating
        by_rating = {}
        for pos in positions:
            rating = pos.get('rating', 'NR')
            if rating not in by_rating:
                by_rating[rating] = {'value': 0, 'count': 0}
            by_rating[rating]['value'] += pos['market_value']
            by_rating[rating]['count'] += 1
        
        for rating in by_rating:
            by_rating[rating]['percentage'] = (
                by_rating[rating]['value'] / total_value * 100
            )
        
        # By maturity bucket
        by_maturity = self._calculate_maturity_buckets(positions, total_value)
        
        return {
            'by_instrument_type': by_instrument,
            'by_sector': by_sector,
            'by_rating': by_rating,
            'by_maturity': by_maturity
        }
    
    def _calculate_maturity_buckets(self, positions: List[Dict], total_value: float) -> Dict[str, Dict]:
        """Calculate allocation by maturity buckets"""
        buckets = {
            '0-1Y': {'value': 0, 'count': 0},
            '1-3Y': {'value': 0, 'count': 0},
            '3-5Y': {'value': 0, 'count': 0},
            '5-10Y': {'value': 0, 'count': 0},
            '10Y+': {'value': 0, 'count': 0}
        }
        
        for pos in positions:
            maturity_date = pos.get('maturity_date')
            if not maturity_date:
                continue
                
            if isinstance(maturity_date, str):
                maturity_date = datetime.fromisoformat(maturity_date.replace('Z', '+00:00'))
            
            years_to_maturity = (maturity_date - datetime.utcnow()).days / 365.25
            
            bucket = '10Y+'
            if years_to_maturity <= 1:
                bucket = '0-1Y'
            elif years_to_maturity <= 3:
                bucket = '1-3Y'
            elif years_to_maturity <= 5:
                bucket = '3-5Y'
            elif years_to_maturity <= 10:
                bucket = '5-10Y'
            
            buckets[bucket]['value'] += pos['market_value']
            buckets[bucket]['count'] += 1
        
        # Calculate percentages
        for bucket in buckets:
            buckets[bucket]['percentage'] = (
                buckets[bucket]['value'] / total_value * 100 if total_value > 0 else 0
            )
        
        return buckets
    
    async def _calculate_portfolio_risk(self, portfolio_id: str, positions: List[Dict]) -> Dict[str, float]:
        """Calculate portfolio risk metrics"""
        try:
            # Get historical portfolio values for volatility calculation
            historical_values = await self.timeseries_db.get_portfolio_history(
                portfolio_id, days=252  # 1 year
            )
            
            risk_metrics = {}
            
            if historical_values and len(historical_values) > 30:
                values_df = pd.DataFrame(historical_values)
                values_df['returns'] = values_df['value'].pct_change().dropna()
                
                # Portfolio volatility
                daily_vol = values_df['returns'].std()
                risk_metrics['volatility'] = daily_vol * np.sqrt(252) * 100  # Annualized %
                
                # Sharpe ratio (assuming 6% risk-free rate)
                risk_free_rate = 0.06
                avg_return = values_df['returns'].mean() * 252
                risk_metrics['sharpe_ratio'] = (
                    (avg_return - risk_free_rate) / (daily_vol * np.sqrt(252))
                    if daily_vol > 0 else 0
                )
                
                # Maximum drawdown
                cumulative = (1 + values_df['returns']).cumprod()
                rolling_max = cumulative.expanding().max()
                drawdown = (cumulative - rolling_max) / rolling_max
                risk_metrics['max_drawdown'] = drawdown.min() * 100  # Percentage
                
                # VaR (Value at Risk) - 95% confidence
                risk_metrics['var_95'] = np.percentile(values_df['returns'], 5) * 100
                risk_metrics['var_99'] = np.percentile(values_df['returns'], 1) * 100
                
            else:
                # Default values if insufficient data
                risk_metrics = {
                    'volatility': 0.0,
                    'sharpe_ratio': 0.0,
                    'max_drawdown': 0.0,
                    'var_95': 0.0,
                    'var_99': 0.0
                }
            
            # Current risk measures
            total_value = sum(pos['market_value'] for pos in positions)
            total_notional = sum(pos.get('notional_value', pos['market_value']) for pos in positions)
            
            risk_metrics.update({
                'total_exposure': total_value,
                'notional_exposure': total_notional,
                'leverage_ratio': total_notional / total_value if total_value > 0 else 0
            })
            
            return risk_metrics
            
        except Exception as e:
            logger.error("Portfolio risk calculation failed", error=str(e))
            return {}
    
    def _calculate_duration_metrics(self, positions: List[Dict]) -> Dict[str, float]:
        """Calculate portfolio duration and convexity"""
        try:
            total_value = sum(pos['market_value'] for pos in positions)
            
            if total_value == 0:
                return {'modified_duration': 0.0, 'macaulay_duration': 0.0, 'convexity': 0.0}
            
            # Weighted duration and convexity
            weighted_mod_duration = 0.0
            weighted_mac_duration = 0.0
            weighted_convexity = 0.0
            
            for pos in positions:
                weight = pos['market_value'] / total_value
                weighted_mod_duration += weight * pos.get('modified_duration', 0.0)
                weighted_mac_duration += weight * pos.get('macaulay_duration', 0.0)
                weighted_convexity += weight * pos.get('convexity', 0.0)
            
            return {
                'modified_duration': weighted_mod_duration,
                'macaulay_duration': weighted_mac_duration,
                'convexity': weighted_convexity,
                'dv01': total_value * weighted_mod_duration / 10000  # Dollar duration
            }
            
        except Exception as e:
            logger.error("Duration calculation failed", error=str(e))
            return {}
    
    def _calculate_credit_metrics(self, positions: List[Dict]) -> Dict[str, Any]:
        """Calculate credit quality metrics"""
        try:
            total_value = sum(pos['market_value'] for pos in positions)
            
            if total_value == 0:
                return {}
            
            # Average credit rating (numerical)
            rating_weights = {
                'AAA': 1, 'AA+': 2, 'AA': 3, 'AA-': 4,
                'A+': 5, 'A': 6, 'A-': 7,
                'BBB+': 8, 'BBB': 9, 'BBB-': 10,
                'BB+': 11, 'BB': 12, 'BB-': 13,
                'B+': 14, 'B': 15, 'B-': 16,
                'CCC+': 17, 'CCC': 18, 'CCC-': 19,
                'CC': 20, 'C': 21, 'D': 22, 'NR': 15  # Default NR to B equivalent
            }
            
            weighted_rating = 0.0
            investment_grade_pct = 0.0
            
            for pos in positions:
                weight = pos['market_value'] / total_value
                rating = pos.get('rating', 'NR')
                
                if rating in rating_weights:
                    weighted_rating += weight * rating_weights[rating]
                    
                    # Investment grade check (BBB- and above)
                    if rating_weights[rating] <= 10:
                        investment_grade_pct += weight * 100
            
            # Convert back to rating
            avg_rating_num = int(round(weighted_rating))
            avg_rating = next(
                (rating for rating, num in rating_weights.items() if num == avg_rating_num),
                'NR'
            )
            
            return {
                'average_rating': avg_rating,
                'average_rating_numeric': weighted_rating,
                'investment_grade_percentage': investment_grade_pct,
                'high_yield_percentage': 100 - investment_grade_pct
            }
            
        except Exception as e:
            logger.error("Credit metrics calculation failed", error=str(e))
            return {}
    
    async def _calculate_performance_metrics(self, portfolio_id: str) -> Dict[str, float]:
        """Calculate portfolio performance metrics"""
        try:
            # Get performance data for different periods
            periods = [1, 7, 30, 90, 365]  # Days
            performance = {}
            
            for days in periods:
                start_date = datetime.utcnow() - timedelta(days=days)
                period_data = await self.timeseries_db.get_portfolio_performance(
                    portfolio_id, start_date
                )
                
                if period_data and len(period_data) >= 2:
                    start_value = period_data[0]['value']
                    end_value = period_data[-1]['value']
                    
                    if start_value > 0:
                        period_return = (end_value - start_value) / start_value * 100
                        performance[f'{days}d_return'] = period_return
                else:
                    performance[f'{days}d_return'] = 0.0
            
            return performance
            
        except Exception as e:
            logger.error("Performance calculation failed", error=str(e))
            return {}
