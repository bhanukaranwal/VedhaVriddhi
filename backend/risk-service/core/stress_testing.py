import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio
import structlog

logger = structlog.get_logger()

class StressTestingEngine:
    """Advanced stress testing for portfolio risk assessment"""
    
    def __init__(self, settings):
        self.settings = settings
        self.scenarios = {}
        
    async def initialize(self):
        """Initialize stress testing engine"""
        logger.info("Initializing Stress Testing Engine")
        await self._load_scenarios()
        
    async def _load_scenarios(self):
        """Load predefined stress test scenarios"""
        self.scenarios = {
            'interest_rate_shock': {
                'name': 'Interest Rate Shock',
                'description': 'Parallel shift in yield curve',
                'parameters': {
                    'yield_shift_up': [0.5, 1.0, 2.0, 3.0],  # basis points * 100
                    'yield_shift_down': [-0.5, -1.0, -2.0, -3.0]
                }
            },
            'credit_spread_widening': {
                'name': 'Credit Spread Widening', 
                'description': 'Credit spreads widen across ratings',
                'parameters': {
                    'spread_multiplier': [1.5, 2.0, 3.0, 5.0]
                }
            },
            'liquidity_crisis': {
                'name': 'Liquidity Crisis',
                'description': 'Severe liquidity constraints',
                'parameters': {
                    'liquidity_discount': [0.05, 0.10, 0.20, 0.30]
                }
            },
            'inflation_shock': {
                'name': 'Inflation Shock',
                'description': 'Unexpected inflation increase',
                'parameters': {
                    'inflation_increase': [2.0, 3.0, 5.0, 7.0]  # percentage points
                }
            },
            'default_cluster': {
                'name': 'Default Cluster',
                'description': 'Multiple defaults in sector',
                'parameters': {
                    'default_rate_multiplier': [2.0, 5.0, 10.0, 20.0]
                }
            }
        }
        
    async def run_scenarios(self, portfolio_id: str, scenario_names: List[str], 
                          confidence_level: float = 0.95) -> Dict[str, Any]:
        """Run stress test scenarios on portfolio"""
        try:
            # Get portfolio data
            positions = await self._get_portfolio_positions(portfolio_id)
            if not positions:
                return {"error": "No portfolio positions found"}
            
            results = {}
            baseline_value = sum(pos['market_value'] for pos in positions)
            
            for scenario_name in scenario_names:
                if scenario_name not in self.scenarios:
                    logger.warning(f"Unknown scenario: {scenario_name}")
                    continue
                    
                scenario_results = await self._run_single_scenario(
                    positions, scenario_name, baseline_value
                )
                results[scenario_name] = scenario_results
            
            # Summary statistics
            results['summary'] = self._calculate_scenario_summary(results, baseline_value)
            
            return results
            
        except Exception as e:
            logger.error(f"Stress testing failed for {portfolio_id}", error=str(e))
            return {"error": str(e)}
    
    async def _run_single_scenario(self, positions: List[Dict], scenario_name: str, 
                                 baseline_value: float) -> Dict[str, Any]:
        """Run a single stress test scenario"""
        try:
            scenario = self.scenarios[scenario_name]
            results = {
                'scenario_name': scenario_name,
                'description': scenario['description'],
                'impacts': []
            }
            
            if scenario_name == 'interest_rate_shock':
                results['impacts'] = await self._interest_rate_shock(positions, scenario['parameters'])
            elif scenario_name == 'credit_spread_widening':
                results['impacts'] = await self._credit_spread_shock(positions, scenario['parameters'])
            elif scenario_name == 'liquidity_crisis':
                results['impacts'] = await self._liquidity_shock(positions, scenario['parameters'])
            elif scenario_name == 'inflation_shock':
                results['impacts'] = await self._inflation_shock(positions, scenario['parameters'])
            elif scenario_name == 'default_cluster':
                results['impacts'] = await self._default_shock(positions, scenario['parameters'])
            
            # Calculate portfolio level impacts
            for impact in results['impacts']:
                impact['portfolio_impact_pct'] = (impact['portfolio_value_change'] / baseline_value) * 100
                impact['portfolio_impact_absolute'] = impact['portfolio_value_change']
            
            return results
            
        except Exception as e:
            logger.error(f"Single scenario {scenario_name} failed", error=str(e))
            return {"error": str(e)}
    
    async def _interest_rate_shock(self, positions: List[Dict], parameters: Dict) -> List[Dict]:
        """Simulate interest rate shock"""
        impacts = []
        
        for shift_type, shifts in parameters.items():
            for shift in shifts:
                total_impact = 0
                position_impacts = []
                
                for position in positions:
                    # Calculate duration-based impact
                    duration = position.get('modified_duration', 5.0)  # Default 5 years
                    market_value = position['market_value']
                    
                    # Price impact = -Duration × Yield Change × Market Value
                    price_impact = -duration * (shift / 100) * market_value
                    total_impact += price_impact
                    
                    position_impacts.append({
                        'symbol': position['symbol'],
                        'market_value': market_value,
                        'duration': duration,
                        'price_impact': price_impact,
                        'impact_pct': (price_impact / market_value) * 100 if market_value > 0 else 0
                    })
                
                impacts.append({
                    'scenario_parameter': f"{shift_type}_{shift}%",
                    'yield_shift': shift,
                    'portfolio_value_change': total_impact,
                    'position_impacts': position_impacts
                })
        
        return impacts
    
    async def _credit_spread_shock(self, positions: List[Dict], parameters: Dict) -> List[Dict]:
        """Simulate credit spread widening"""
        impacts = []
        
        for multiplier in parameters['spread_multiplier']:
            total_impact = 0
            position_impacts = []
            
            for position in positions:
                # Only apply to credit-sensitive instruments
                if position.get('instrument_type') in ['corporate_bond', 'cd', 'cp']:
                    current_spread = position.get('credit_spread', 1.0)  # Default 1%
                    spread_change = current_spread * (multiplier - 1)
                    
                    duration = position.get('modified_duration', 5.0)
                    market_value = position['market_value']
                    
                    # Impact = -Duration × Spread Change × Market Value
                    price_impact = -duration * (spread_change / 100) * market_value
                    total_impact += price_impact
                    
                    position_impacts.append({
                        'symbol': position['symbol'],
                        'current_spread': current_spread,
                        'spread_change': spread_change,
                        'price_impact': price_impact,
                        'impact_pct': (price_impact / market_value) * 100 if market_value > 0 else 0
                    })
            
            impacts.append({
                'scenario_parameter': f"spread_multiplier_{multiplier}x",
                'spread_multiplier': multiplier,
                'portfolio_value_change': total_impact,
                'position_impacts': position_impacts
            })
        
        return impacts
    
    async def _liquidity_shock(self, positions: List[Dict], parameters: Dict) -> List[Dict]:
        """Simulate liquidity crisis"""
        impacts = []
        
        for discount in parameters['liquidity_discount']:
            total_impact = 0
            position_impacts = []
            
            for position in positions:
                # Apply liquidity discount based on instrument liquidity
                liquidity_score = position.get('liquidity_score', 0.5)  # 0-1 scale
                effective_discount = discount * (1 - liquidity_score)
                
                market_value = position['market_value']
                price_impact = -effective_discount * market_value
                total_impact += price_impact
                
                position_impacts.append({
                    'symbol': position['symbol'],
                    'liquidity_score': liquidity_score,
                    'effective_discount': effective_discount,
                    'price_impact': price_impact,
                    'impact_pct': (price_impact / market_value) * 100 if market_value > 0 else 0
                })
            
            impacts.append({
                'scenario_parameter': f"liquidity_discount_{discount*100}%",
                'liquidity_discount': discount,
                'portfolio_value_change': total_impact,
                'position_impacts': position_impacts
            })
        
        return impacts
    
    async def _inflation_shock(self, positions: List[Dict], parameters: Dict) -> List[Dict]:
        """Simulate inflation shock"""
        impacts = []
        
        for inflation_increase in parameters['inflation_increase']:
            total_impact = 0  
            position_impacts = []
            
            for position in positions:
                # Inflation-linked bonds benefit, others suffer
                instrument_type = position.get('instrument_type', 'corporate_bond')
                market_value = position['market_value']
                
                if 'inflation_linked' in instrument_type.lower():
                    # Inflation-linked bonds benefit
                    price_impact = (inflation_increase / 100) * market_value * 0.8
                else:
                    # Regular bonds suffer from higher rates
                    duration = position.get('modified_duration', 5.0)
                    # Assume 70% of inflation shock translates to rate increase
                    rate_impact = inflation_increase * 0.7
                    price_impact = -duration * (rate_impact / 100) * market_value
                
                total_impact += price_impact
                
                position_impacts.append({
                    'symbol': position['symbol'],
                    'instrument_type': instrument_type,
                    'price_impact': price_impact,
                    'impact_pct': (price_impact / market_value) * 100 if market_value > 0 else 0
                })
            
            impacts.append({
                'scenario_parameter': f"inflation_increase_{inflation_increase}%",
                'inflation_increase': inflation_increase,
                'portfolio_value_change': total_impact,
                'position_impacts': position_impacts
            })
        
        return impacts
    
    async def _default_shock(self, positions: List[Dict], parameters: Dict) -> List[Dict]:
        """Simulate default cluster scenario"""
        impacts = []
        
        for multiplier in parameters['default_rate_multiplier']:
            total_impact = 0
            position_impacts = []
            
            for position in positions:
                # Only credit-sensitive instruments affected
                if position.get('instrument_type') in ['corporate_bond', 'cd', 'cp']:
                    rating = position.get('rating', 'BBB')
                    base_default_prob = self._get_default_probability(rating)
                    
                    # Increase default probability
                    stressed_default_prob = min(base_default_prob * multiplier, 0.5)  # Cap at 50%
                    
                    # Loss given default assumption
                    lgd = 0.6  # 60% loss given default
                    expected_loss = stressed_default_prob * lgd
                    
                    market_value = position['market_value']
                    price_impact = -expected_loss * market_value
                    total_impact += price_impact
                    
                    position_impacts.append({
                        'symbol': position['symbol'],
                        'rating': rating,
                        'base_default_prob': base_default_prob,
                        'stressed_default_prob': stressed_default_prob,
                        'expected_loss': expected_loss,
                        'price_impact': price_impact,
                        'impact_pct': (price_impact / market_value) * 100 if market_value > 0 else 0
                    })
            
            impacts.append({
                'scenario_parameter': f"default_multiplier_{multiplier}x",
                'default_multiplier': multiplier,
                'portfolio_value_change': total_impact,
                'position_impacts': position_impacts
            })
        
        return impacts
    
    def _get_default_probability(self, rating: str) -> float:
        """Get annual default probability by rating"""
        default_probs = {
            'AAA': 0.0001, 'AA+': 0.0002, 'AA': 0.0003, 'AA-': 0.0005,
            'A+': 0.0008, 'A': 0.0012, 'A-': 0.0018,
            'BBB+': 0.0025, 'BBB': 0.0035, 'BBB-': 0.0050,
            'BB+': 0.0075, 'BB': 0.0125, 'BB-': 0.0200,
            'B+': 0.0350, 'B': 0.0600, 'B-': 0.1000,
            'CCC': 0.2000, 'CC': 0.3000, 'C': 0.5000
        }
        return default_probs.get(rating, 0.05)  # Default 5%
    
    def _calculate_scenario_summary(self, results: Dict, baseline_value: float) -> Dict[str, Any]:
        """Calculate summary statistics across scenarios"""
        try:
            all_impacts = []
            worst_case = {'scenario': '', 'impact': 0}
            best_case = {'scenario': '', 'impact': 0}
            
            for scenario_name, scenario_data in results.items():
                if scenario_name == 'summary':
                    continue
                    
                for impact in scenario_data.get('impacts', []):
                    impact_pct = impact.get('portfolio_impact_pct', 0)
                    all_impacts.append(impact_pct)
                    
                    if impact_pct < worst_case['impact']:
                        worst_case = {
                            'scenario': scenario_name,
                            'parameter': impact.get('scenario_parameter', ''),
                            'impact': impact_pct
                        }
                    
                    if impact_pct > best_case['impact']:
                        best_case = {
                            'scenario': scenario_name,
                            'parameter': impact.get('scenario_parameter', ''),
                            'impact': impact_pct
                        }
            
            return {
                'total_scenarios_tested': len([s for s in results.keys() if s != 'summary']),
                'worst_case_scenario': worst_case,
                'best_case_scenario': best_case,
                'average_impact': np.mean(all_impacts) if all_impacts else 0,
                'impact_volatility': np.std(all_impacts) if all_impacts else 0,
                'percentile_95': np.percentile(all_impacts, 5) if all_impacts else 0,  # 5th percentile (worst 5%)
                'percentile_99': np.percentile(all_impacts, 1) if all_impacts else 0   # 1st percentile (worst 1%)
            }
            
        except Exception as e:
            logger.error("Failed to calculate scenario summary", error=str(e))
            return {}
    
    async def _get_portfolio_positions(self, portfolio_id: str) -> List[Dict]:
        """Get portfolio positions (placeholder)"""
        # This would fetch from database
        return [
            {
                'symbol': 'GSEC10Y',
                'market_value': 10000000,
                'modified_duration': 8.5,
                'instrument_type': 'government_security',
                'rating': 'AAA',
                'liquidity_score': 0.9
            },
            {
                'symbol': 'CORP5Y_AA',
                'market_value': 5000000,
                'modified_duration': 4.2,
                'instrument_type': 'corporate_bond',
                'rating': 'AA',
                'credit_spread': 1.5,
                'liquidity_score': 0.6
            }
        ]
