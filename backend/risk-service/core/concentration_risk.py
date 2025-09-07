import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime
import structlog

logger = structlog.get_logger()

class ConcentrationRiskEngine:
    """Portfolio concentration risk analysis"""
    
    def __init__(self, settings):
        self.settings = settings
        
    async def analyze_portfolio(self, portfolio_id: str) -> Dict[str, Any]:
        """Comprehensive concentration risk analysis"""
        try:
            positions = await self._get_portfolio_positions(portfolio_id)
            if not positions:
                return {"error": "No positions found"}
            
            total_value = sum(pos['market_value'] for pos in positions)
            
            analysis = {
                'portfolio_id': portfolio_id,
                'total_value': total_value,
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'concentration_by_issuer': self._analyze_issuer_concentration(positions, total_value),
                'concentration_by_sector': self._analyze_sector_concentration(positions, total_value),
                'concentration_by_rating': self._analyze_rating_concentration(positions, total_value),
                'concentration_by_maturity': self._analyze_maturity_concentration(positions, total_value),
                'concentration_by_currency': self._analyze_currency_concentration(positions, total_value),
                'diversification_metrics': self._calculate_diversification_metrics(positions, total_value),
                'concentration_risk_score': 0.0,
                'recommendations': []
            }
            
            # Calculate overall concentration risk score
            analysis['concentration_risk_score'] = self._calculate_concentration_risk_score(analysis)
            
            # Generate recommendations
            analysis['recommendations'] = self._generate_recommendations(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Concentration analysis failed for {portfolio_id}", error=str(e))
            return {"error": str(e)}
    
    def _analyze_issuer_concentration(self, positions: List[Dict], total_value: float) -> Dict[str, Any]:
        """Analyze concentration by issuer"""
        issuer_exposure = {}
        
        for pos in positions:
            issuer = pos.get('issuer', 'Unknown')
            if issuer not in issuer_exposure:
                issuer_exposure[issuer] = {
                    'market_value': 0,
                    'positions': 0,
                    'instruments': []
                }
            
            issuer_exposure[issuer]['market_value'] += pos['market_value']
            issuer_exposure[issuer]['positions'] += 1
            issuer_exposure[issuer]['instruments'].append(pos['symbol'])
        
        # Calculate percentages and sort by exposure
        issuer_analysis = []
        for issuer, data in issuer_exposure.items():
            percentage = (data['market_value'] / total_value) * 100 if total_value > 0 else 0
            issuer_analysis.append({
                'issuer': issuer,
                'market_value': data['market_value'],
                'percentage': percentage,
                'position_count': data['positions'],
                'instruments': data['instruments']
            })
        
        issuer_analysis.sort(key=lambda x: x['market_value'], reverse=True)
        
        # Calculate concentration metrics
        top_5_concentration = sum(item['percentage'] for item in issuer_analysis[:5])
        top_10_concentration = sum(item['percentage'] for item in issuer_analysis[:10])
        max_single_issuer = issuer_analysis[0]['percentage'] if issuer_analysis else 0
        
        return {
            'top_issuers': issuer_analysis[:10],
            'total_issuers': len(issuer_analysis),
            'max_single_issuer_pct': max_single_issuer,
            'top_5_concentration_pct': top_5_concentration,
            'top_10_concentration_pct': top_10_concentration,
            'herfindahl_index': sum((item['percentage'] / 100) ** 2 for item in issuer_analysis)
        }
    
    def _analyze_sector_concentration(self, positions: List[Dict], total_value: float) -> Dict[str, Any]:
        """Analyze concentration by sector"""
        sector_exposure = {}
        
        for pos in positions:
            sector = pos.get('sector', 'Unknown')
            if sector not in sector_exposure:
                sector_exposure[sector] = {
                    'market_value': 0,
                    'positions': 0,
                    'issuers': set()
                }
            
            sector_exposure[sector]['market_value'] += pos['market_value']
            sector_exposure[sector]['positions'] += 1
            sector_exposure[sector]['issuers'].add(pos.get('issuer', 'Unknown'))
        
        # Calculate percentages
        sector_analysis = []
        for sector, data in sector_exposure.items():
            percentage = (data['market_value'] / total_value) * 100 if total_value > 0 else 0
            sector_analysis.append({
                'sector': sector,
                'market_value': data['market_value'],
                'percentage': percentage,
                'position_count': data['positions'],
                'unique_issuers': len(data['issuers'])
            })
        
        sector_analysis.sort(key=lambda x: x['market_value'], reverse=True)
        
        return {
            'sector_breakdown': sector_analysis,
            'total_sectors': len(sector_analysis),
            'max_sector_pct': sector_analysis[0]['percentage'] if sector_analysis else 0,
            'herfindahl_index': sum((item['percentage'] / 100) ** 2 for item in sector_analysis)
        }
    
    def _analyze_rating_concentration(self, positions: List[Dict], total_value: float) -> Dict[str, Any]:
        """Analyze concentration by credit rating"""
        rating_exposure = {}
        rating_mapping = {
            'AAA': 1, 'AA+': 2, 'AA': 3, 'AA-': 4,
            'A+': 5, 'A': 6, 'A-': 7,
            'BBB+': 8, 'BBB': 9, 'BBB-': 10,
            'BB+': 11, 'BB': 12, 'BB-': 13,
            'B+': 14, 'B': 15, 'B-': 16,
            'CCC+': 17, 'CCC': 18, 'CCC-': 19,
            'NR': 20
        }
        
        for pos in positions:
            rating = pos.get('rating', 'NR')
            if rating not in rating_exposure:
                rating_exposure[rating] = {
                    'market_value': 0,
                    'positions': 0
                }
            
            rating_exposure[rating]['market_value'] += pos['market_value']
            rating_exposure[rating]['positions'] += 1
        
        # Calculate percentages and categorize
        rating_analysis = []
        investment_grade_value = 0
        high_yield_value = 0
        
        for rating, data in rating_exposure.items():
            percentage = (data['market_value'] / total_value) * 100 if total_value > 0 else 0
            
            rating_analysis.append({
                'rating': rating,
                'market_value': data['market_value'],
                'percentage': percentage,
                'position_count': data['positions'],
                'rating_numeric': rating_mapping.get(rating, 20)
            })
            
            # Categorize investment grade vs high yield
            if rating_mapping.get(rating, 20) <= 10:  # BBB- and above
                investment_grade_value += data['market_value']
            else:
                high_yield_value += data['market_value']
        
        rating_analysis.sort(key=lambda x: x['rating_numeric'])
        
        # Calculate weighted average rating
        total_rating_weight = sum(
            data['market_value'] * rating_mapping.get(rating, 20)
            for rating, data in rating_exposure.items()
        )
        weighted_avg_rating = total_rating_weight / total_value if total_value > 0 else 20
        
        return {
            'rating_breakdown': rating_analysis,
            'investment_grade_pct': (investment_grade_value / total_value) * 100 if total_value > 0 else 0,
            'high_yield_pct': (high_yield_value / total_value) * 100 if total_value > 0 else 0,
            'weighted_avg_rating_numeric': weighted_avg_rating,
            'credit_quality_score': max(0, (20 - weighted_avg_rating) / 20 * 100)
        }
    
    def _analyze_maturity_concentration(self, positions: List[Dict], total_value: float) -> Dict[str, Any]:
        """Analyze concentration by maturity buckets"""
        maturity_buckets = {
            '0-1Y': {'market_value': 0, 'positions': 0},
            '1-3Y': {'market_value': 0, 'positions': 0},
            '3-5Y': {'market_value': 0, 'positions': 0},
            '5-10Y': {'market_value': 0, 'positions': 0},
            '10Y+': {'market_value': 0, 'positions': 0},
            'Perpetual': {'market_value': 0, 'positions': 0}
        }
        
        for pos in positions:
            maturity_date = pos.get('maturity_date')
            if not maturity_date:
                bucket = 'Perpetual'
            else:
                try:
                    if isinstance(maturity_date, str):
                        maturity_date = datetime.fromisoformat(maturity_date.replace('Z', '+00:00'))
                    
                    years_to_maturity = (maturity_date - datetime.utcnow()).days / 365.25
                    
                    if years_to_maturity <= 1:
                        bucket = '0-1Y'
                    elif years_to_maturity <= 3:
                        bucket = '1-3Y'
                    elif years_to_maturity <= 5:
                        bucket = '3-5Y'
                    elif years_to_maturity <= 10:
                        bucket = '5-10Y'
                    else:
                        bucket = '10Y+'
                except:
                    bucket = 'Perpetual'
            
            maturity_buckets[bucket]['market_value'] += pos['market_value']
            maturity_buckets[bucket]['positions'] += 1
        
        # Calculate percentages
        maturity_analysis = []
        for bucket, data in maturity_buckets.items():
            if data['market_value'] > 0:  # Only include non-empty buckets
                percentage = (data['market_value'] / total_value) * 100
                maturity_analysis.append({
                    'maturity_bucket': bucket,
                    'market_value': data['market_value'],
                    'percentage': percentage,
                    'position_count': data['positions']
                })
        
        maturity_analysis.sort(key=lambda x: x['market_value'], reverse=True)
        
        return {
            'maturity_breakdown': maturity_analysis,
            'max_bucket_pct': maturity_analysis[0]['percentage'] if maturity_analysis else 0,
            'effective_buckets': len(maturity_analysis)
        }
    
    def _analyze_currency_concentration(self, positions: List[Dict], total_value: float) -> Dict[str, Any]:
        """Analyze concentration by currency"""
        currency_exposure = {}
        
        for pos in positions:
            currency = pos.get('currency', 'INR')
            if currency not in currency_exposure:
                currency_exposure[currency] = {
                    'market_value': 0,
                    'positions': 0
                }
            
            currency_exposure[currency]['market_value'] += pos['market_value']
            currency_exposure[currency]['positions'] += 1
        
        # Calculate percentages
        currency_analysis = []
        for currency, data in currency_exposure.items():
            percentage = (data['market_value'] / total_value) * 100 if total_value > 0 else 0
            currency_analysis.append({
                'currency': currency,
                'market_value': data['market_value'],
                'percentage': percentage,
                'position_count': data['positions']
            })
        
        currency_analysis.sort(key=lambda x: x['market_value'], reverse=True)
        
        return {
            'currency_breakdown': currency_analysis,
            'base_currency_pct': currency_analysis[0]['percentage'] if currency_analysis else 0,
            'foreign_currency_pct': sum(item['percentage'] for item in currency_analysis[1:]),
            'currency_count': len(currency_analysis)
        }
    
    def _calculate_diversification_metrics(self, positions: List[Dict], total_value: float) -> Dict[str, Any]:
        """Calculate diversification metrics"""
        try:
            n_positions = len(positions)
            
            if n_positions == 0:
                return {}
            
            # Calculate position weights
            weights = [pos['market_value'] / total_value for pos in positions if total_value > 0]
            
            # Herfindahl-Hirschman Index
            hhi = sum(w**2 for w in weights)
            
            # Effective number of holdings
            effective_holdings = 1 / hhi if hhi > 0 else 1
            
            # Diversification ratio (1 = perfectly diversified, 0 = concentrated)
            diversification_ratio = (1 - hhi) / (1 - 1/n_positions) if n_positions > 1 else 0
            
            # Concentration ratio (top 5 positions)
            sorted_weights = sorted(weights, reverse=True)
            cr5 = sum(sorted_weights[:min(5, len(sorted_weights))])
            
            # Gini coefficient (inequality measure)
            gini = self._calculate_gini_coefficient(weights)
            
            return {
                'herfindahl_hirschman_index': hhi,
                'effective_number_holdings': effective_holdings,
                'diversification_ratio': diversification_ratio,
                'concentration_ratio_5': cr5,
                'gini_coefficient': gini,
                'total_positions': n_positions,
                'average_position_size_pct': (1 / n_positions) * 100 if n_positions > 0 else 0
            }
            
        except Exception as e:
            logger.error("Failed to calculate diversification metrics", error=str(e))
            return {}
    
    def _calculate_gini_coefficient(self, weights: List[float]) -> float:
        """Calculate Gini coefficient for position weights"""
        try:
            if not weights:
                return 0.0
            
            weights = sorted(weights)
            n = len(weights)
            cumsum = np.cumsum(weights)
            
            return (n + 1 - 2 * sum((n + 1 - i) * w for i, w in enumerate(weights, 1))) / (n * sum(weights))
            
        except Exception as e:
            logger.error("Gini coefficient calculation failed", error=str(e))
            return 0.0
    
    def _calculate_concentration_risk_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall concentration risk score (0-100, higher = more concentrated)"""
        try:
            score = 0.0
            
            # Issuer concentration (30% weight)
            max_issuer = analysis['concentration_by_issuer'].get('max_single_issuer_pct', 0)
            issuer_score = min(max_issuer * 2, 100)  # 50% issuer = 100 score
            score += issuer_score * 0.30
            
            # Sector concentration (25% weight)
            max_sector = analysis['concentration_by_sector'].get('max_sector_pct', 0)
            sector_score = min(max_sector * 1.5, 100)  # 67% sector = 100 score
            score += sector_score * 0.25
            
            # Rating concentration (20% weight)
            rating_hhi = analysis['concentration_by_rating'].get('rating_breakdown', [])
            if rating_hhi:
                rating_concentration = sum((item['percentage'] / 100) ** 2 for item in rating_hhi)
                rating_score = rating_concentration * 100
                score += rating_score * 0.20
            
            # Maturity concentration (15% weight)
            max_maturity = analysis['concentration_by_maturity'].get('max_bucket_pct', 0)
            maturity_score = min(max_maturity * 1.25, 100)  # 80% maturity bucket = 100 score
            score += maturity_score * 0.15
            
            # Diversification (10% weight)
            diversification = analysis['diversification_metrics']
            if diversification:
                div_ratio = diversification.get('diversification_ratio', 1.0)
                # Invert diversification ratio (1 = well diversified = low score)
                div_score = (1 - div_ratio) * 100
                score += div_score * 0.10
            
            return min(score, 100.0)
            
        except Exception as e:
            logger.error("Concentration risk score calculation failed", error=str(e))
            return 50.0  # Default medium risk
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate concentration risk recommendations"""
        recommendations = []
        
        try:
            # Issuer concentration recommendations
            max_issuer = analysis['concentration_by_issuer'].get('max_single_issuer_pct', 0)
            if max_issuer > 15:
                recommendations.append(f"Consider reducing single issuer exposure (currently {max_issuer:.1f}%, recommended <15%)")
            
            # Sector concentration recommendations
            max_sector = analysis['concentration_by_sector'].get('max_sector_pct', 0)
            if max_sector > 25:
                recommendations.append(f"Consider diversifying sector exposure (currently {max_sector:.1f}%, recommended <25%)")
            
            # Rating concentration recommendations
            ig_pct = analysis['concentration_by_rating'].get('investment_grade_pct', 0)
            if ig_pct < 70:
                recommendations.append(f"Consider increasing investment grade allocation (currently {ig_pct:.1f}%, recommended >70%)")
            
            # Maturity concentration recommendations
            max_maturity = analysis['concentration_by_maturity'].get('max_bucket_pct', 0)
            if max_maturity > 40:
                recommendations.append(f"Consider better maturity diversification (single bucket: {max_maturity:.1f}%, recommended <40%)")
            
            # Diversification recommendations
            diversification = analysis['diversification_metrics']
            if diversification:
                effective_holdings = diversification.get('effective_number_holdings', 0)
                if effective_holdings < 10:
                    recommendations.append(f"Portfolio may benefit from more diversification (effective holdings: {effective_holdings:.1f})")
            
            if not recommendations:
                recommendations.append("Portfolio concentration levels appear reasonable")
                
        except Exception as e:
            logger.error("Failed to generate recommendations", error=str(e))
            recommendations.append("Unable to generate recommendations due to calculation error")
        
        return recommendations
    
    async def _get_portfolio_positions(self, portfolio_id: str) -> List[Dict]:
        """Get portfolio positions (placeholder)"""
        # This would fetch from database
        return [
            {
                'symbol': 'GSEC10Y',
                'market_value': 25000000,
                'issuer': 'Government of India',
                'sector': 'Government',
                'rating': 'AAA',
                'currency': 'INR',
                'maturity_date': '2034-06-15'
            },
            {
                'symbol': 'GSEC5Y', 
                'market_value': 20000000,
                'issuer': 'Government of India',
                'sector': 'Government',
                'rating': 'AAA',
                'currency': 'INR',
                'maturity_date': '2029-06-15'
            },
            {
                'symbol': 'CORP_AA_2027',
                'market_value': 15000000,
                'issuer': 'ABC Corporation',
                'sector': 'Financial Services',
                'rating': 'AA',
                'currency': 'INR',
                'maturity_date': '2027-12-31'
            },
            {
                'symbol': 'CORP_A_2026',
                'market_value': 12000000,
                'issuer': 'XYZ Industries',
                'sector': 'Manufacturing',
                'rating': 'A',
                'currency': 'INR', 
                'maturity_date': '2026-03-15'
            },
            {
                'symbol': 'BANK_CD_2025',
                'market_value': 8000000,
                'issuer': 'DEF Bank',
                'sector': 'Banking',
                'rating': 'AA-',
                'currency': 'INR',
                'maturity_date': '2025-09-30'
            }
        ]
