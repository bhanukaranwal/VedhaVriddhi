import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from scipy import stats
import structlog

logger = structlog.get_logger()

class VaREngine:
    """Value at Risk calculation engine with multiple methodologies"""
    
    def __init__(self, settings):
        self.settings = settings
        
    async def initialize(self):
        logger.info("Initializing VaR Engine")
        
    async def calculate_portfolio_var(self, portfolio_id: str) -> Dict[str, float]:
        """Calculate VaR using multiple methods"""
        try:
            # Get portfolio data
            positions = await self._get_portfolio_positions(portfolio_id)
            returns = await self._get_portfolio_returns(portfolio_id, days=252)
            
            if not returns or len(returns) < 30:
                logger.warning(f"Insufficient data for VaR calculation: {portfolio_id}")
                return self._default_var_metrics()
            
            portfolio_value = sum(pos['market_value'] for pos in positions)
            returns_array = np.array(returns)
            
            # Calculate VaR using different methods
            var_metrics = {}
            
            # Historical VaR
            var_metrics.update(self._historical_var(returns_array, portfolio_value))
            
            # Parametric VaR
            var_metrics.update(self._parametric_var(returns_array, portfolio_value))
            
            # Monte Carlo VaR
            var_metrics.update(self._monte_carlo_var(returns_array, portfolio_value))
            
            # Expected Shortfall (Conditional VaR)
            var_metrics.update(self._expected_shortfall(returns_array, portfolio_value))
            
            return var_metrics
            
        except Exception as e:
            logger.error(f"VaR calculation failed for {portfolio_id}", error=str(e))
            return self._default_var_metrics()
    
    def _historical_var(self, returns: np.ndarray, portfolio_value: float) -> Dict[str, float]:
        """Historical simulation VaR"""
        try:
            # 1-day VaR
            var_95 = np.percentile(returns, 5) * portfolio_value
            var_99 = np.percentile(returns, 1) * portfolio_value
            
            # 10-day VaR (scaling)
            var_95_10d = var_95 * np.sqrt(10)
            var_99_10d = var_99 * np.sqrt(10)
            
            return {
                'historical_var_95_1d': abs(var_95),
                'historical_var_99_1d': abs(var_99),
                'historical_var_95_10d': abs(var_95_10d),
                'historical_var_99_10d': abs(var_99_10d)
            }
            
        except Exception as e:
            logger.error("Historical VaR calculation failed", error=str(e))
            return {}
    
    def _parametric_var(self, returns: np.ndarray, portfolio_value: float) -> Dict[str, float]:
        """Parametric (Normal distribution) VaR"""
        try:
            mean_return = np.mean(returns)
            std_return = np.std(returns, ddof=1)
            
            # Z-scores for confidence levels
            z_95 = stats.norm.ppf(0.05)  # -1.645
            z_99 = stats.norm.ppf(0.01)  # -2.33
            
            # 1-day VaR
            var_95 = (mean_return + z_95 * std_return) * portfolio_value
            var_99 = (mean_return + z_99 * std_return) * portfolio_value
            
            # 10-day VaR
            var_95_10d = (mean_return * 10 + z_95 * std_return * np.sqrt(10)) * portfolio_value
            var_99_10d = (mean_return * 10 + z_99 * std_return * np.sqrt(10)) * portfolio_value
            
            return {
                'parametric_var_95_1d': abs(var_95),
                'parametric_var_99_1d': abs(var_99),
                'parametric_var_95_10d': abs(var_95_10d),
                'parametric_var_99_10d': abs(var_99_10d)
            }
            
        except Exception as e:
            logger.error("Parametric VaR calculation failed", error=str(e))
            return {}
    
    def _monte_carlo_var(self, returns: np.ndarray, portfolio_value: float, 
                        simulations: int = 10000) -> Dict[str, float]:
        """Monte Carlo VaR simulation"""
        try:
            mean_return = np.mean(returns)
            std_return = np.std(returns, ddof=1)
            
            # Generate random scenarios
            np.random.seed(42)  # For reproducibility
            simulated_returns = np.random.normal(mean_return, std_return, simulations)
            simulated_values = simulated_returns * portfolio_value
            
            # Calculate VaR
            var_95 = np.percentile(simulated_values, 5)
            var_99 = np.percentile(simulated_values, 1)
            
            # 10-day scaling
            simulated_returns_10d = np.random.normal(
                mean_return * 10, 
                std_return * np.sqrt(10), 
                simulations
            )
            simulated_values_10d = simulated_returns_10d * portfolio_value
            
            var_95_10d = np.percentile(simulated_values_10d, 5)
            var_99_10d = np.percentile(simulated_values_10d, 1)
            
            return {
                'monte_carlo_var_95_1d': abs(var_95),
                'monte_carlo_var_99_1d': abs(var_99),
                'monte_carlo_var_95_10d': abs(var_95_10d),
                'monte_carlo_var_99_10d': abs(var_99_10d)
            }
            
        except Exception as e:
            logger.error("Monte Carlo VaR calculation failed", error=str(e))
            return {}
    
    def _expected_shortfall(self, returns: np.ndarray, portfolio_value: float) -> Dict[str, float]:
        """Expected Shortfall (Conditional VaR)"""
        try:
            # Sort returns
            sorted_returns = np.sort(returns)
            
            # 95% Expected Shortfall
            cutoff_95 = int(0.05 * len(sorted_returns))
            es_95 = np.mean(sorted_returns[:cutoff_95]) * portfolio_value
            
            # 99% Expected Shortfall
            cutoff_99 = int(0.01 * len(sorted_returns))
            es_99 = np.mean(sorted_returns[:cutoff_99]) * portfolio_value
            
            return {
                'expected_shortfall_95': abs(es_95),
                'expected_shortfall_99': abs(es_99)
            }
            
        except Exception as e:
            logger.error("Expected Shortfall calculation failed", error=str(e))
            return {}
    
    def _default_var_metrics(self) -> Dict[str, float]:
        """Default VaR metrics when calculation fails"""
        return {
            'historical_var_95_1d': 0.0,
            'historical_var_99_1d': 0.0,
            'parametric_var_95_1d': 0.0,
            'parametric_var_99_1d': 0.0,
            'monte_carlo_var_95_1d': 0.0,
            'monte_carlo_var_99_1d': 0.0,
            'expected_shortfall_95': 0.0,
            'expected_shortfall_99': 0.0
        }
    
    async def _get_portfolio_positions(self, portfolio_id: str) -> List[Dict]:
        """Get current portfolio positions"""
        # This would fetch from database
        # Placeholder implementation
        return [
            {'symbol': 'GSEC10Y', 'market_value': 10000000, 'quantity': 100},
            {'symbol': 'GSEC5Y', 'market_value': 5000000, 'quantity': 50}
        ]
    
    async def _get_portfolio_returns(self, portfolio_id: str, days: int) -> List[float]:
        """Get historical portfolio returns"""
        # This would fetch from timeseries database
        # Placeholder: generate synthetic returns
        np.random.seed(42)
        return np.random.normal(0.0001, 0.02, days).tolist()
