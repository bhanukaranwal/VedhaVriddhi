import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
from scipy import optimize, interpolate
from sklearn.decomposition import PCA
import structlog

from models import YieldCurvePoint, YieldCurveModel
from database.timeseries_db import TimeSeriesDB

logger = structlog.get_logger()

class YieldCurveEngine:
    """Advanced yield curve modeling and analysis"""
    
    def __init__(self, settings):
        self.settings = settings
        self.db = TimeSeriesDB(settings)
        self.curves = {}
        self.models = {}
        
        # Standard tenors (in years)
        self.tenors = [0.25, 0.5, 1, 2, 3, 5, 7, 10, 15, 20, 30]
        self.tenor_labels = ['3M', '6M', '1Y', '2Y', '3Y', '5Y', '7Y', '10Y', '15Y', '20Y', '30Y']
        
    async def initialize(self):
        """Initialize yield curve engine"""
        logger.info("Initializing Yield Curve Engine")
        await self.load_historical_curves()
        await self.calibrate_models()
        
    async def update_curves(self):
        """Update all yield curves"""
        try:
            # Government yield curve
            await self._update_government_curve()
            
            # Corporate yield curves by rating
            for rating in ['AAA', 'AA', 'A', 'BBB']:
                await self._update_corporate_curve(rating)
                
            # State government curve
            await self._update_state_government_curve()
            
            logger.info("Updated all yield curves")
            
        except Exception as e:
            logger.error("Failed to update curves", error=str(e))
            raise
    
    async def _update_government_curve(self):
        """Update government securities yield curve"""
        try:
            # Fetch latest government bond yields
            yields_data = await self.db.get_latest_yields('government')
            
            if not yields_data:
                logger.warning("No government yield data available")
                return
            
            # Convert to DataFrame for processing
            df = pd.DataFrame(yields_data)
            
            # Clean and interpolate
            curve_points = self._interpolate_curve(df, 'government')
            
            # Calculate curve statistics
            curve_stats = self._calculate_curve_statistics(curve_points)
            
            # Store curve
            self.curves['government'] = {
                'points': curve_points,
                'statistics': curve_stats,
                'timestamp': datetime.utcnow(),
                'type': 'government'
            }
            
            # Save to database
            await self.db.store_yield_curve('government', curve_points, curve_stats)
            
            logger.info("Updated government yield curve")
            
        except Exception as e:
            logger.error("Failed to update government curve", error=str(e))
            
    async def _update_corporate_curve(self, rating: str):
        """Update corporate yield curve for specific rating"""
        try:
            # Fetch corporate bond yields for rating
            yields_data = await self.db.get_latest_yields('corporate', rating=rating)
            
            if not yields_data:
                logger.warning(f"No {rating} corporate yield data available")
                return
            
            # Get government curve for spread calculation
            govt_curve = self.curves.get('government')
            if not govt_curve:
                logger.warning("Government curve not available for spread calculation")
                return
            
            # Convert to DataFrame
            df = pd.DataFrame(yields_data)
            
            # Interpolate curve
            curve_points = self._interpolate_curve(df, f'corporate_{rating}')
            
            # Calculate spreads over government
            spreads = self._calculate_spreads(curve_points, govt_curve['points'])
            
            # Calculate curve statistics
            curve_stats = self._calculate_curve_statistics(curve_points)
            curve_stats['spreads'] = spreads
            
            # Store curve
            self.curves[f'corporate_{rating}'] = {
                'points': curve_points,
                'statistics': curve_stats,
                'timestamp': datetime.utcnow(),
                'type': 'corporate',
                'rating': rating
            }
            
            # Save to database
            await self.db.store_yield_curve(f'corporate_{rating}', curve_points, curve_stats)
            
            logger.info(f"Updated {rating} corporate yield curve")
            
        except Exception as e:
            logger.error(f"Failed to update {rating} corporate curve", error=str(e))
    
    def _interpolate_curve(self, df: pd.DataFrame, curve_type: str) -> List[YieldCurvePoint]:
        """Interpolate yield curve using various methods"""
        try:
            # Sort by maturity
            df_sorted = df.sort_values('maturity_years')
            
            # Remove duplicates and outliers
            df_clean = self._clean_yield_data(df_sorted)
            
            if len(df_clean) < 3:
                raise ValueError("Insufficient data points for interpolation")
            
            # Cubic spline interpolation
            cs = interpolate.CubicSpline(
                df_clean['maturity_years'].values,
                df_clean['yield'].values,
                bc_type='natural'
            )
            
            # Generate points for standard tenors
            curve_points = []
            for tenor in self.tenors:
                try:
                    yield_value = float(cs(tenor))
                    
                    # Sanity checks
                    if yield_value < 0 or yield_value > 50:  # 50% max yield
                        logger.warning(f"Unusual yield value {yield_value} for tenor {tenor}")
                        continue
                        
                    curve_points.append(YieldCurvePoint(
                        tenor=tenor,
                        yield_value=yield_value,
                        maturity_date=datetime.utcnow() + timedelta(days=int(tenor * 365)),
                        curve_type=curve_type,
                        timestamp=datetime.utcnow()
                    ))
                    
                except Exception as e:
                    logger.warning(f"Failed to interpolate for tenor {tenor}", error=str(e))
                    continue
            
            return curve_points
            
        except Exception as e:
            logger.error("Curve interpolation failed", error=str(e))
            return []
    
    def _clean_yield_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean yield data removing outliers and duplicates"""
        # Remove null yields
        df_clean = df.dropna(subset=['yield'])
        
        # Remove negative yields (unless government in special circumstances)
        df_clean = df_clean[df_clean['yield'] >= -1.0]  # Allow slightly negative
        
        # Remove extreme outliers using IQR method
        Q1 = df_clean['yield'].quantile(0.25)
        Q3 = df_clean['yield'].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 3.0 * IQR  # More conservative than 1.5
        upper_bound = Q3 + 3.0 * IQR
        
        df_clean = df_clean[
            (df_clean['yield'] >= lower_bound) & 
            (df_clean['yield'] <= upper_bound)
        ]
        
        # Remove duplicate maturities, keeping latest
        df_clean = df_clean.drop_duplicates(subset=['maturity_years'], keep='last')
        
        return df_clean
    
    def _calculate_spreads(self, corporate_points: List[YieldCurvePoint], 
                          govt_points: List[YieldCurvePoint]) -> Dict[float, float]:
        """Calculate credit spreads over government curve"""
        spreads = {}
        
        # Create lookup for government yields
        govt_yields = {point.tenor: point.yield_value for point in govt_points}
        
        for corp_point in corporate_points:
            if corp_point.tenor in govt_yields:
                spread = corp_point.yield_value - govt_yields[corp_point.tenor]
                spreads[corp_point.tenor] = spread
        
        return spreads
    
    def _calculate_curve_statistics(self, curve_points: List[YieldCurvePoint]) -> Dict[str, float]:
        """Calculate curve shape and risk statistics"""
        if len(curve_points) < 3:
            return {}
        
        yields = [point.yield_value for point in curve_points]
        tenors = [point.tenor for point in curve_points]
        
        # Level (10Y yield)
        level = next((y for t, y in zip(tenors, yields) if t == 10), yields[len(yields)//2])
        
        # Slope (10Y - 2Y)
        yield_10y = next((y for t, y in zip(tenors, yields) if t == 10), level)
        yield_2y = next((y for t, y in zip(tenors, yields) if t == 2), yields[0])
        slope = yield_10y - yield_2y
        
        # Curvature (2*5Y - 2Y - 10Y)
        yield_5y = next((y for t, y in zip(tenors, yields) if t == 5), level)
        curvature = 2 * yield_5y - yield_2y - yield_10y
        
        # Volatility (if historical data available)
        volatility = self._calculate_yield_volatility(curve_points[0].curve_type)
        
        return {
            'level': level,
            'slope': slope, 
            'curvature': curvature,
            'volatility': volatility,
            'min_yield': min(yields),
            'max_yield': max(yields),
            'avg_yield': np.mean(yields)
        }
    
    async def _calculate_yield_volatility(self, curve_type: str) -> float:
        """Calculate historical yield volatility"""
        try:
            # Get
    async def _calculate_yield_volatility(self, curve_type: str) -> float:
        """Calculate historical yield volatility"""
        try:
            # Get 30 days of historical data
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)
            
            historical_data = await self.db.get_yield_history(
                curve_type, start_date, end_date
            )
            
            if len(historical_data) < 10:
                return 0.0  # Insufficient data
                
            # Calculate daily changes
            df = pd.DataFrame(historical_data)
            df['yield_change'] = df['yield'].diff()
            
            # Annualized volatility
            volatility = df['yield_change'].std() * np.sqrt(252)
            return float(volatility) if not np.isnan(volatility) else 0.0
            
        except Exception as e:
            logger.error("Failed to calculate volatility", error=str(e))
            return 0.0

    async def get_curve(self, curve_type: str, date: Optional[str] = None) -> List[Dict]:
        """Get yield curve data"""
        try:
            if date:
                # Historical curve
                curve_data = await self.db.get_historical_curve(curve_type, date)
            else:
                # Latest curve
                curve_data = self.curves.get(curve_type)
                
            if not curve_data:
                return []
                
            # Format for API response
            if 'points' in curve_data:
                return [
                    {
                        'tenor': point.tenor,
                        'tenor_label': self.tenor_labels[self.tenors.index(point.tenor)] 
                                     if point.tenor in self.tenors else f"{point.tenor}Y",
                        'yield': point.yield_value,
                        'maturity_date': point.maturity_date.isoformat(),
                        'timestamp': point.timestamp.isoformat()
                    }
                    for point in curve_data['points']
                ]
            else:
                return curve_data
                
        except Exception as e:
            logger.error(f"Failed to get curve {curve_type}", error=str(e))
            return []

    async def nelson_siegel_fit(self, yields: np.ndarray, tenors: np.ndarray) -> Dict[str, float]:
        """Fit Nelson-Siegel model to yield curve"""
        try:
            def nelson_siegel(tau, beta0, beta1, beta2, lambda_param):
                """Nelson-Siegel functional form"""
                term1 = beta1 * ((1 - np.exp(-lambda_param * tau)) / (lambda_param * tau))
                term2 = beta2 * (((1 - np.exp(-lambda_param * tau)) / (lambda_param * tau)) - np.exp(-lambda_param * tau))
                return beta0 + term1 + term2
            
            def objective(params):
                beta0, beta1, beta2, lambda_param = params
                fitted = nelson_siegel(tenors, beta0, beta1, beta2, lambda_param)
                return np.sum((yields - fitted) ** 2)
            
            # Initial parameter guess
            initial_guess = [yields.mean(), -1.0, 0.0, 0.5]
            
            # Bounds for parameters
            bounds = [(-10, 20), (-10, 10), (-10, 10), (0.01, 5.0)]
            
            # Optimization
            result = optimize.minimize(
                objective, 
                initial_guess, 
                bounds=bounds, 
                method='L-BFGS-B'
            )
            
            if result.success:
                beta0, beta1, beta2, lambda_param = result.x
                
                # Calculate R-squared
                fitted_yields = nelson_siegel(tenors, beta0, beta1, beta2, lambda_param)
                ss_res = np.sum((yields - fitted_yields) ** 2)
                ss_tot = np.sum((yields - np.mean(yields)) ** 2)
                r_squared = 1 - (ss_res / ss_tot)
                
                return {
                    'beta0': beta0,
                    'beta1': beta1, 
                    'beta2': beta2,
                    'lambda': lambda_param,
                    'r_squared': r_squared,
                    'rmse': np.sqrt(ss_res / len(yields))
                }
            else:
                logger.warning("Nelson-Siegel optimization failed")
                return {}
                
        except Exception as e:
            logger.error("Nelson-Siegel fitting failed", error=str(e))
            return {}
