import asyncio
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import structlog

logger = structlog.get_logger()

class HealthIndicator(Enum):
    ATMOSPHERIC_CO2 = "atmospheric_co2"
    GLOBAL_TEMPERATURE = "global_temperature"
    BIODIVERSITY_INDEX = "biodiversity_index"
    OCEAN_PH = "ocean_ph"
    FOREST_COVER = "forest_cover"
    RENEWABLE_ENERGY = "renewable_energy"
    SOIL_HEALTH = "soil_health"
    WATER_QUALITY = "water_quality"

@dataclass
class PlanetaryHealthMetric:
    """Planetary health measurement"""
    metric_id: str
    indicator: HealthIndicator
    current_value: float
    optimal_range: Tuple[float, float]
    critical_threshold: float
    measurement_timestamp: datetime
    data_source: str
    confidence_level: float

class PlanetaryHealthMonitor:
    """Advanced planetary health monitoring and tipping point detection"""
    
    def __init__(self):
        self.health_metrics: Dict[str, PlanetaryHealthMetric] = {}
        self.health_history: Dict[HealthIndicator, List[float]] = {}
        self.tipping_point_detector = TippingPointDetector()
        self.regeneration_tracker = RegenerationTracker()
        
    async def initialize(self):
        """Initialize planetary health monitor"""
        logger.info("Initializing Planetary Health Monitor")
        
        await self.tipping_point_detector.initialize()
        await self.regeneration_tracker.initialize()
        
        # Initialize baseline indicators
        await self._initialize_health_indicators()
        
        # Start monitoring loops
        asyncio.create_task(self._continuous_health_monitoring())
        asyncio.create_task(self._tipping_point_surveillance())
        asyncio.create_task(self._regeneration_monitoring())
        
        logger.info("Planetary Health Monitor initialized successfully")
    
    async def _initialize_health_indicators(self):
        """Initialize baseline planetary health indicators"""
        # Current planetary health baselines (approximate values)
        baseline_indicators = {
            HealthIndicator.ATMOSPHERIC_CO2: {
                'current_value': 421.0,  # ppm
                'optimal_range': (280.0, 350.0),
                'critical_threshold': 450.0,
                'data_source': 'NOAA_Mauna_Loa'
            },
            HealthIndicator.GLOBAL_TEMPERATURE: {
                'current_value': 1.1,  # degrees C above pre-industrial
                'optimal_range': (0.0, 0.5),
                'critical_threshold': 2.0,
                'data_source': 'NASA_GISS'
            },
            HealthIndicator.BIODIVERSITY_INDEX: {
                'current_value': 0.69,  # Living Planet Index
                'optimal_range': (0.95, 1.0),
                'critical_threshold': 0.5,
                'data_source': 'WWF_Living_Planet_Report'
            },
            HealthIndicator.OCEAN_PH: {
                'current_value': 8.0,  # pH units
                'optimal_range': (8.1, 8.3),
                'critical_threshold': 7.8,
                'data_source': 'NOAA_Ocean_Chemistry'
            },
            HealthIndicator.FOREST_COVER: {
                'current_value': 31.0,  # percent of land area
                'optimal_range': (35.0, 40.0),
                'critical_threshold': 25.0,
                'data_source': 'FAO_Global_Forest_Assessment'
            },
            HealthIndicator.RENEWABLE_ENERGY: {
                'current_value': 12.6,  # percent of global energy
                'optimal_range': (80.0, 100.0),
                'critical_threshold': 50.0,
                'data_source': 'IEA_Renewable_Statistics'
            }
        }
        
        for indicator, data in baseline_indicators.items():
            metric_id = f"baseline_{indicator.value}_{datetime.utcnow().timestamp()}"
            
            metric = PlanetaryHealthMetric(
                metric_id=metric_id,
                indicator=indicator,
                current_value=data['current_value'],
                optimal_range=data['optimal_range'],
                critical_threshold=data['critical_threshold'],
                measurement_timestamp=datetime.utcnow(),
                data_source=data['data_source'],
                confidence_level=0.85
            )
            
            self.health_metrics[metric_id] = metric
            
            # Initialize history
            self.health_history[indicator] = [data['current_value']]
    
    async def update_health_metric(self,
                                 indicator: HealthIndicator,
                                 new_value: float,
                                 data_source: str,
                                 confidence_level: float = 0.8) -> str:
        """Update planetary health metric"""
        try:
            metric_id = f"metric_{indicator.value}_{datetime.utcnow().timestamp()}"
            
            # Get reference metric for ranges
            reference_metrics = [m for m in self.health_metrics.values() if m.indicator == indicator]
            if reference_metrics:
                reference = reference_metrics[-1]  # Most recent
                optimal_range = reference.optimal_range
                critical_threshold = reference.critical_threshold
            else:
                # Default ranges
                optimal_range = (0.0, 1.0)
                critical_threshold = 0.0
            
            # Create new metric
            metric = PlanetaryHealthMetric(
                metric_id=metric_id,
                indicator=indicator,
                current_value=new_value,
                optimal_range=optimal_range,
                critical_threshold=critical_threshold,
                measurement_timestamp=datetime.utcnow(),
                data_source=data_source,
                confidence_level=confidence_level
            )
            
            self.health_metrics[metric_id] = metric
            
            # Update history
            if indicator not in self.health_history:
                self.health_history[indicator] = []
            self.health_history[indicator].append(new_value)
            
            # Keep only recent history
            if len(self.health_history[indicator]) > 1000:
                self.health_history[indicator] = self.health_history[indicator][-1000:]
            
            # Check for critical changes
            await self._check_critical_changes(indicator, new_value)
            
            logger.info(f"Updated {indicator.value} metric: {new_value}")
            return metric_id
            
        except Exception as e:
            logger.error("Health metric update failed", error=str(e))
            raise
    
    async def _check_critical_changes(self, indicator: HealthIndicator, new_value: float):
        """Check for critical changes in health indicators"""
        history = self.health_history.get(indicator, [])
        
        if len(history) < 2:
            return
        
        # Check for rapid deterioration
        recent_trend = np.polyfit(range(len(history[-10:])), history[-10:], 1)[0]
        
        # Get current metric for thresholds
        current_metrics = [m for m in self.health_metrics.values() if m.indicator == indicator]
        if not current_metrics:
            return
        
        current_metric = max(current_metrics, key=lambda m: m.measurement_timestamp)
        
        # Critical threshold breach
        if indicator in [HealthIndicator.ATMOSPHERIC_CO2, HealthIndicator.GLOBAL_TEMPERATURE]:
            if new_value > current_metric.critical_threshold:
                logger.critical(f"CRITICAL: {indicator.value} exceeded threshold: {new_value}")
        else:
            if new_value < current_metric.critical_threshold:
                logger.critical(f"CRITICAL: {indicator.value} below threshold: {new_value}")
        
        # Rapid deterioration
        deterioration_threshold = 0.01  # 1% change per measurement
        if abs(recent_trend) > deterioration_threshold:
            logger.warning(f"Rapid change in {indicator.value}: trend = {recent_trend}")
    
    async def assess_planetary_health(self) -> Dict:
        """Assess overall planetary health status"""
        try:
            if not self.health_metrics:
                return {'planetary_health_assessment_available': False}
            
            # Get latest metrics for each indicator
            latest_metrics = {}
            for indicator in HealthIndicator:
                indicator_metrics = [m for m in self.health_metrics.values() if m.indicator == indicator]
                if indicator_metrics:
                    latest_metrics[indicator] = max(indicator_metrics, key=lambda m: m.measurement_timestamp)
            
            # Calculate health scores
            health_scores = {}
            critical_indicators = []
            
            for indicator, metric in latest_metrics.items():
                if indicator in [HealthIndicator.ATMOSPHERIC_CO2, HealthIndicator.GLOBAL_TEMPERATURE]:
                    # Lower is better for these indicators
                    optimal_mid = sum(metric.optimal_range) / 2
                    if metric.current_value <= optimal_mid:
                        score = 1.0
                    elif metric.current_value >= metric.critical_threshold:
                        score = 0.0
                        critical_indicators.append(indicator.value)
                    else:
                        score = 1.0 - (metric.current_value - optimal_mid) / (metric.critical_threshold - optimal_mid)
                else:
                    # Higher is better for these indicators
                    optimal_mid = sum(metric.optimal_range) / 2
                    if metric.current_value >= optimal_mid:
                        score = 1.0
                    elif metric.current_value <= metric.critical_threshold:
                        score = 0.0
                        critical_indicators.append(indicator.value)
                    else:
                        score = (metric.current_value - metric.critical_threshold) / (optimal_mid - metric.critical_threshold)
                
                health_scores[indicator.value] = max(0.0, min(1.0, score))
            
            # Overall planetary health score
            overall_health = np.mean(list(health_scores.values())) if health_scores else 0.0
            
            # Tipping point analysis
            tipping_points = await self.tipping_point_detector.assess_tipping_points(latest_metrics)
            
            # Regeneration potential
            regeneration_potential = await self.regeneration_tracker.assess_regeneration_potential()
            
            # Health status classification
            if overall_health > 0.8:
                health_status = "healthy"
            elif overall_health > 0.6:
                health_status = "stressed"
            elif overall_health > 0.4:
                health_status = "degraded"
            else:
                health_status = "critical"
            
            return {
                'planetary_health_assessment_available': True,
                'overall_health_score': float(overall_health),
                'health_status': health_status,
                'indicator_scores': health_scores,
                'critical_indicators': critical_indicators,
                'tipping_points_analysis': tipping_points,
                'regeneration_potential': regeneration_potential,
                'total_indicators_monitored': len(latest_metrics),
                'assessment_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Planetary health assessment failed", error=str(e))
            return {'planetary_health_assessment_available': False, 'error': str(e)}
    
    async def _continuous_health_monitoring(self):
        """Continuous health monitoring loop"""
        while True:
            try:
                # Simulate receiving real-time data updates
                for indicator in [HealthIndicator.ATMOSPHERIC_CO2, HealthIndicator.GLOBAL_TEMPERATURE, 
                                HealthIndicator.BIODIVERSITY_INDEX]:
                    
                    # Mock data update (in practice would receive from actual data sources)
                    if indicator in self.health_history:
                        current_value = self.health_history[indicator][-1]
                        # Add small random variation
                        variation = np.random.normal(0, 0.01) * current_value
                        new_value = current_value + variation
                        
                        await self.update_health_metric(
                            indicator, new_value, f"continuous_monitoring_{indicator.value}", 0.7
                        )
                
                await asyncio.sleep(300)  # Update every 5 minutes
                
            except Exception as e:
                logger.error("Continuous health monitoring error", error=str(e))
                await asyncio.sleep(600)
    
    async def _tipping_point_surveillance(self):
        """Monitor for approaching tipping points"""
        while True:
            try:
                assessment = await self.assess_planetary_health()
                
                if assessment.get('tipping_points_analysis', {}).get('imminent_tipping_points'):
                    logger.critical("IMMINENT TIPPING POINTS DETECTED")
                    # Would trigger emergency protocols
                
                await asyncio.sleep(1800)  # Check every 30 minutes
                
            except Exception as e:
                logger.error("Tipping point surveillance error", error=str(e))
                await asyncio.sleep(3600)
    
    async def _regeneration_monitoring(self):
        """Monitor regeneration opportunities and progress"""
        while True:
            try:
                regeneration_status = await self.regeneration_tracker.monitor_regeneration_progress()
                
                if regeneration_status['breakthrough_opportunities']:
                    logger.info("Breakthrough regeneration opportunities identified")
                
                await asyncio.sleep(3600)  # Monitor hourly
                
            except Exception as e:
                logger.error("Regeneration monitoring error", error=str(e))
                await asyncio.sleep(1800)

# Support classes
class TippingPointDetector:
    """Detect approaching planetary tipping points"""
    
    async def initialize(self):
        self.tipping_point_thresholds = {
            HealthIndicator.ATMOSPHERIC_CO2: 450.0,  # ppm - dangerous climate change
            HealthIndicator.GLOBAL_TEMPERATURE: 1.5,  # degrees C - Paris Agreement target
            HealthIndicator.BIODIVERSITY_INDEX: 0.5,  # Living Planet Index - ecosystem collapse
            HealthIndicator.OCEAN_PH: 7.8,  # pH - ocean acidification tipping point
            HealthIndicator.FOREST_COVER: 25.0  # percent - forest ecosystem stability
        }
    
    async def assess_tipping_points(self, latest_metrics: Dict) -> Dict:
        """Assess proximity to tipping points"""
        tipping_analysis = {
            'imminent_tipping_points': [],
            'approaching_tipping_points': [],
            'tipping_point_distances': {}
        }
        
        for indicator, metric in latest_metrics.items():
            if indicator in self.tipping_point_thresholds:
                threshold = self.tipping_point_thresholds[indicator]
                current_value = metric.current_value
                
                # Calculate distance to tipping point
                if indicator in [HealthIndicator.ATMOSPHERIC_CO2, HealthIndicator.GLOBAL_TEMPERATURE]:
                    distance = (threshold - current_value) / threshold
                else:
                    distance = (current_value - threshold) / current_value if current_value > 0 else -1.0
                
                tipping_analysis['tipping_point_distances'][indicator.value] = float(distance)
                
                # Classify proximity
                if distance < 0.05:  # Within 5%
                    tipping_analysis['imminent_tipping_points'].append(indicator.value)
                elif distance < 0.2:  # Within 20%
                    tipping_analysis['approaching_tipping_points'].append(indicator.value)
        
        return tipping_analysis

class RegenerationTracker:
    """Track planetary regeneration opportunities and progress"""
    
    async def initialize(self):
        self.regeneration_projects = {}
        self.regeneration_metrics = {}
    
    async def assess_regeneration_potential(self) -> Dict:
        """Assess potential for planetary regeneration"""
        return {
            'reforestation_potential': 0.8,  # High potential
            'ocean_restoration_potential': 0.6,  # Medium potential
            'soil_regeneration_potential': 0.7,  # High potential
            'renewable_transition_potential': 0.9,  # Very high potential
            'overall_regeneration_score': 0.75
        }
    
    async def monitor_regeneration_progress(self) -> Dict:
        """Monitor progress of regeneration efforts"""
        return {
            'active_projects': len(self.regeneration_projects),
            'breakthrough_opportunities': ['soil_carbon_sequestration', 'ocean_kelp_forests'],
            'regeneration_rate': 0.02,  # 2% improvement per year
            'acceleration_needed': True
        }
