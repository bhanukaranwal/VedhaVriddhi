import asyncio
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import structlog

logger = structlog.get_logger()

class PatternType(Enum):
    TEMPORAL = "temporal"
    CYCLICAL = "cyclical"
    TREND = "trend"
    ANOMALY = "anomaly"
    CORRELATION = "correlation"
    REGIME_CHANGE = "regime_change"
    VOLATILITY_CLUSTER = "volatility_cluster"
    MEAN_REVERSION = "mean_reversion"

@dataclass
class DetectedPattern:
    """Detected pattern in data"""
    pattern_id: str
    pattern_type: PatternType
    confidence: float
    strength: float
    time_range: Tuple[datetime, datetime]
    parameters: Dict[str, Any]
    description: str
    impact_score: float

@dataclass
class SynthesizedPattern:
    """Synthesized multi-dimensional pattern"""
    synthesis_id: str
    component_patterns: List[str]
    synthesis_method: str
    emergent_properties: Dict[str, Any]
    predictive_power: float
    robustness_score: float

class AdvancedPatternSynthesis:
    """Advanced pattern detection and synthesis for financial data"""
    
    def __init__(self):
        self.detected_patterns: Dict[str, DetectedPattern] = {}
        self.synthesized_patterns: Dict[str, SynthesizedPattern] = {}
        self.pattern_detectors = {}
        self.synthesis_engines = {}
        
    async def initialize(self):
        """Initialize pattern synthesis system"""
        logger.info("Initializing Advanced Pattern Synthesis")
        
        # Initialize pattern detectors
        self.pattern_detectors = {
            PatternType.TEMPORAL: self._detect_temporal_patterns,
            PatternType.CYCLICAL: self._detect_cyclical_patterns,
            PatternType.TREND: self._detect_trend_patterns,
            PatternType.ANOMALY: self._detect_anomaly_patterns,
            PatternType.CORRELATION: self._detect_correlation_patterns,
            PatternType.REGIME_CHANGE: self._detect_regime_changes,
            PatternType.VOLATILITY_CLUSTER: self._detect_volatility_clusters,
            PatternType.MEAN_REVERSION: self._detect_mean_reversion
        }
        
        # Initialize synthesis engines
        self.synthesis_engines = {
            'hierarchical': self._hierarchical_synthesis,
            'emergent': self._emergent_synthesis,
            'temporal_fusion': self._temporal_fusion_synthesis,
            'cross_dimensional': self._cross_dimensional_synthesis
        }
        
        logger.info("Advanced Pattern Synthesis initialized successfully")
    
    async def detect_multidimensional_patterns(self, 
                                             data_cube: np.ndarray,
                                             timestamps: List[datetime],
                                             pattern_types: List[PatternType] = None) -> List[DetectedPattern]:
        """Detect patterns across multiple dimensions"""
        try:
            if pattern_types is None:
                pattern_types = list(PatternType)
            
            detected_patterns = []
            
            for pattern_type in pattern_types:
                detector = self.pattern_detectors.get(pattern_type)
                if detector:
                    patterns = await detector(data_cube, timestamps)
                    detected_patterns.extend(patterns)
            
            # Store detected patterns
            for pattern in detected_patterns:
                self.detected_patterns[pattern.pattern_id] = pattern
            
            logger.info(f"Detected {len(detected_patterns)} patterns across {len(pattern_types)} pattern types")
            return detected_patterns
            
        except Exception as e:
            logger.error("Multi-dimensional pattern detection failed", error=str(e))
            raise
    
    async def _detect_temporal_patterns(self, data_cube: np.ndarray, timestamps: List[datetime]) -> List[DetectedPattern]:
        """Detect temporal patterns"""
        patterns = []
        
        # Analyze temporal correlations across different lags
        for lag in [1, 5, 22, 66]:  # Daily, weekly, monthly, quarterly
            if lag >= data_cube.shape[-1]:  # Time dimension
                continue
                
            # Calculate temporal autocorrelation
            time_series = np.mean(data_cube, axis=tuple(range(len(data_cube.shape)-1)))  # Average across all but time
            autocorr = await self._calculate_autocorrelation(time_series, lag)
            
            if abs(autocorr) > 0.3:  # Significant temporal correlation
                pattern_id = f"temporal_{lag}_{datetime.utcnow().timestamp()}"
                
                pattern = DetectedPattern(
                    pattern_id=pattern_id,
                    pattern_type=PatternType.TEMPORAL,
                    confidence=min(abs(autocorr) * 1.5, 1.0),
                    strength=abs(autocorr),
                    time_range=(timestamps[0], timestamps[-1]),
                    parameters={'lag': lag, 'autocorrelation': autocorr},
                    description=f"Temporal pattern with {lag}-period lag (autocorr: {autocorr:.3f})",
                    impact_score=abs(autocorr) * 0.8
                )
                patterns.append(pattern)
        
        return patterns
    
    async def _detect_cyclical_patterns(self, data_cube: np.ndarray, timestamps: List[datetime]) -> List[DetectedPattern]:
        """Detect cyclical patterns using FFT"""
        patterns = []
        
        # Apply FFT to detect cyclical components
        time_series = np.mean(data_cube, axis=tuple(range(len(data_cube.shape)-1)))
        
        # Remove trend
        detrended = time_series - np.polyval(np.polyfit(range(len(time_series)), time_series, 1), range(len(time_series)))
        
        # FFT
        fft = np.fft.fft(detrended)
        freqs = np.fft.fftfreq(len(detrended))
        power = np.abs(fft) ** 2
        
        # Find dominant frequencies
        dominant_indices = np.argsort(power)[-5:][::-1]  # Top 5
        
        for i, idx in enumerate(dominant_indices):
            if freqs[idx] > 0 and power[idx] > np.mean(power) * 3:  # Significant frequency
                period = 1.0 / freqs[idx]
                
                pattern_id = f"cyclical_{i}_{datetime.utcnow().timestamp()}"
                
                pattern = DetectedPattern(
                    pattern_id=pattern_id,
                    pattern_type=PatternType.CYCLICAL,
                    confidence=min(power[idx] / np.max(power), 1.0),
                    strength=float(power[idx] / np.mean(power)),
                    time_range=(timestamps[0], timestamps[-1]),
                    parameters={'period': period, 'frequency': freqs[idx], 'power': power[idx]},
                    description=f"Cyclical pattern with period {period:.1f} units",
                    impact_score=min(power[idx] / np.max(power) * 0.9, 1.0)
                )
                patterns.append(pattern)
        
        return patterns
    
    async def _detect_trend_patterns(self, data_cube: np.ndarray, timestamps: List[datetime]) -> List[DetectedPattern]:
        """Detect trend patterns"""
        patterns = []
        
        # Analyze trends across different dimensions
        for dim in range(len(data_cube.shape) - 1):  # Exclude time dimension
            # Average across other dimensions
            other_dims = [i for i in range(len(data_cube.shape)) if i not in [dim, -1]]
            
            if other_dims:
                dim_data = np.mean(data_cube, axis=tuple(other_dims))
            else:
                dim_data = data_cube
            
            # Detect trends in each series along this dimension
            for series_idx in range(dim_data.shape[0] if len(dim_data.shape) > 1 else 1):
                if len(dim_data.shape) > 1:
                    time_series = dim_data[series_idx]
                else:
                    time_series = dim_data
                
                # Linear trend
                trend_coeff = np.polyfit(range(len(time_series)), time_series, 1)[0]
                r_squared = await self._calculate_r_squared(time_series, trend_coeff)
                
                if abs(trend_coeff) > 0.01 and r_squared > 0.3:  # Significant trend
                    pattern_id = f"trend_{dim}_{series_idx}_{datetime.utcnow().timestamp()}"
                    
                    pattern = DetectedPattern(
                        pattern_id=pattern_id,
                        pattern_type=PatternType.TREND,
                        confidence=r_squared,
                        strength=abs(trend_coeff),
                        time_range=(timestamps[0], timestamps[-1]),
                        parameters={'slope': trend_coeff, 'r_squared': r_squared, 'dimension': dim},
                        description=f"{'Upward' if trend_coeff > 0 else 'Downward'} trend (slope: {trend_coeff:.4f})",
                        impact_score=r_squared * min(abs(trend_coeff) * 10, 1.0)
                    )
                    patterns.append(pattern)
        
        return patterns
    
    async def _detect_anomaly_patterns(self, data_cube: np.ndarray, timestamps: List[datetime]) -> List[DetectedPattern]:
        """Detect anomaly patterns"""
        patterns = []
        
        # Flatten data for anomaly detection
        flattened_data = data_cube.reshape(-1, data_cube.shape[-1])  # Keep time dimension
        
        for series_idx in range(min(flattened_data.shape[0], 50)):  # Limit to first 50 series
            time_series = flattened_data[series_idx]
            
            # Z-score based anomaly detection
            mean_val = np.mean(time_series)
            std_val = np.std(time_series)
            
            if std_val > 0:
                z_scores = np.abs(time_series - mean_val) / std_val
                anomaly_indices = np.where(z_scores > 3.0)[0]  # 3-sigma rule
                
                if len(anomaly_indices) > 0:
                    # Group consecutive anomalies
                    anomaly_groups = await self._group_consecutive_indices(anomaly_indices)
                    
                    for group in anomaly_groups:
                        start_idx, end_idx = group[0], group[-1]
                        anomaly_strength = np.mean(z_scores[group])
                        
                        pattern_id = f"anomaly_{series_idx}_{start_idx}_{datetime.utcnow().timestamp()}"
                        
                        pattern = DetectedPattern(
                            pattern_id=pattern_id,
                            pattern_type=PatternType.ANOMALY,
                            confidence=min(anomaly_strength / 5.0, 1.0),
                            strength=float(anomaly_strength),
                            time_range=(timestamps[start_idx], timestamps[min(end_idx, len(timestamps)-1)]),
                            parameters={
                                'z_score': anomaly_strength,
                                'start_index': start_idx,
                                'end_index': end_idx,
                                'series_index': series_idx
                            },
                            description=f"Anomaly detected (z-score: {anomaly_strength:.2f})",
                            impact_score=min(anomaly_strength / 3.0, 1.0)
                        )
                        patterns.append(pattern)
        
        return patterns[:10]  # Limit to top 10 anomalies
    
    async def _detect_correlation_patterns(self, data_cube: np.ndarray, timestamps: List[datetime]) -> List[DetectedPattern]:
        """Detect correlation patterns between different series"""
        patterns = []
        
        # Flatten to get individual time series
        flattened_data = data_cube.reshape(-1, data_cube.shape[-1])
        
        # Sample pairs for correlation analysis
        n_series = min(flattened_data.shape[0], 20)  # Limit to 20 series
        
        for i in range(n_series):
            for j in range(i+1, n_series):
                series_i = flattened_data[i]
                series_j = flattened_data[j]
                
                # Calculate correlation
                correlation = np.corrcoef(series_i, series_j)[0, 1]
                
                if abs(correlation) > 0.7:  # High correlation
                    pattern_id = f"correlation_{i}_{j}_{datetime.utcnow().timestamp()}"
                    
                    pattern = DetectedPattern(
                        pattern_id=pattern_id,
                        pattern_type=PatternType.CORRELATION,
                        confidence=abs(correlation),
                        strength=abs(correlation),
                        time_range=(timestamps[0], timestamps[-1]),
                        parameters={
                            'series_pair': (i, j),
                            'correlation': correlation,
                            'correlation_type': 'positive' if correlation > 0 else 'negative'
                        },
                        description=f"{'Strong positive' if correlation > 0 else 'Strong negative'} correlation ({correlation:.3f})",
                        impact_score=abs(correlation) * 0.8
                    )
                    patterns.append(pattern)
        
        return patterns[:15]  # Limit to top 15 correlations
    
    async def synthesize_patterns(self, 
                                pattern_ids: List[str], 
                                synthesis_method: str = 'hierarchical') -> SynthesizedPattern:
        """Synthesize multiple patterns into higher-order pattern"""
        try:
            if not pattern_ids:
                raise ValueError("No patterns provided for synthesis")
            
            # Get patterns
            patterns = [self.detected_patterns[pid] for pid in pattern_ids if pid in self.detected_patterns]
            
            if not patterns:
                raise ValueError("No valid patterns found")
            
            # Apply synthesis method
            synthesis_engine = self.synthesis_engines.get(synthesis_method)
            if not synthesis_engine:
                raise ValueError(f"Unknown synthesis method: {synthesis_method}")
            
            synthesis_result = await synthesis_engine(patterns)
            
            # Create synthesized pattern
            synthesis_id = f"synthesis_{synthesis_method}_{datetime.utcnow().timestamp()}"
            
            synthesized = SynthesizedPattern(
                synthesis_id=synthesis_id,
                component_patterns=pattern_ids,
                synthesis_method=synthesis_method,
                emergent_properties=synthesis_result['emergent_properties'],
                predictive_power=synthesis_result['predictive_power'],
                robustness_score=synthesis_result['robustness_score']
            )
            
            self.synthesized_patterns[synthesis_id] = synthesized
            
            logger.info(f"Synthesized {len(patterns)} patterns using {synthesis_method} method")
            return synthesized
            
        except Exception as e:
            logger.error("Pattern synthesis failed", error=str(e))
            raise
    
    async def _hierarchical_synthesis(self, patterns: List[DetectedPattern]) -> Dict:
        """Hierarchical pattern synthesis"""
        # Group patterns by type and time overlap
        pattern_groups = {}
        for pattern in patterns:
            pattern_groups.setdefault(pattern.pattern_type, []).append(pattern)
        
        # Analyze hierarchical relationships
        emergent_properties = {
            'pattern_hierarchy': {},
            'interaction_strength': 0.0,
            'temporal_alignment': 0.0
        }
        
        # Calculate interaction between pattern types
        for ptype1, ptype1_patterns in pattern_groups.items():
            for ptype2, ptype2_patterns in pattern_groups.items():
                if ptype1 != ptype2:
                    interaction = await self._calculate_pattern_interaction(ptype1_patterns, ptype2_patterns)
                    emergent_properties['pattern_hierarchy'][f'{ptype1.value}_{ptype2.value}'] = interaction
        
        # Overall interaction strength
        emergent_properties['interaction_strength'] = np.mean(list(emergent_properties['pattern_hierarchy'].values())) if emergent_properties['pattern_hierarchy'] else 0.0
        
        # Predictive power based on pattern diversity and strength
        pattern_strengths = [p.strength for p in patterns]
        pattern_diversity = len(pattern_groups) / len(PatternType)
        predictive_power = np.mean(pattern_strengths) * pattern_diversity
        
        # Robustness based on confidence and temporal coverage
        confidences = [p.confidence for p in patterns]
        robustness_score = np.mean(confidences) * min(len(patterns) / 5.0, 1.0)
        
        return {
            'emergent_properties': emergent_properties,
            'predictive_power': float(predictive_power),
            'robustness_score': float(robustness_score)
        }
    
    async def _emergent_synthesis(self, patterns: List[DetectedPattern]) -> Dict:
        """Emergent pattern synthesis"""
        # Look for emergent behaviors that arise from pattern interactions
        emergent_properties = {
            'emergence_indicators': [],
            'phase_transitions': [],
            'non_linear_interactions': 0.0
        }
        
        # Detect emergence indicators
        pattern_strengths = np.array([p.strength for p in patterns])
        pattern_confidences = np.array([p.confidence for p in patterns])
        
        # Non-linearity in pattern interactions
        if len(patterns) > 2:
            interaction_matrix = np.outer(pattern_strengths, pattern_confidences)
            non_linearity = np.std(interaction_matrix) / np.mean(interaction_matrix) if np.mean(interaction_matrix) > 0 else 0
            emergent_properties['non_linear_interactions'] = float(non_linearity)
        
        # Predictive power enhanced by emergence
        base_predictive_power = np.mean(pattern_strengths) * np.mean(pattern_confidences)
        emergence_bonus = emergent_properties['non_linear_interactions'] * 0.3
        predictive_power = base_predictive_power + emergence_bonus
        
        # Robustness considering emergent stability
        robustness_score = np.mean(pattern_confidences) * (1.0 + min(emergence_bonus, 0.5))
        
        return {
            'emergent_properties': emergent_properties,
            'predictive_power': float(predictive_power),
            'robustness_score': float(robustness_score)
        }
    
    async def _calculate_pattern_interaction(self, patterns1: List[DetectedPattern], patterns2: List[DetectedPattern]) -> float:
        """Calculate interaction strength between two pattern groups"""
        if not patterns1 or not patterns2:
            return 0.0
        
        # Time overlap analysis
        total_overlap = 0.0
        total_comparisons = 0
        
        for p1 in patterns1:
            for p2 in patterns2:
                overlap = await self._calculate_temporal_overlap(p1.time_range, p2.time_range)
                strength_product = p1.strength * p2.strength
                
                total_overlap += overlap * strength_product
                total_comparisons += 1
        
        return total_overlap / total_comparisons if total_comparisons > 0 else 0.0
    
    async def _calculate_temporal_overlap(self, range1: Tuple[datetime, datetime], range2: Tuple[datetime, datetime]) -> float:
        """Calculate temporal overlap between two time ranges"""
        start1, end1 = range1
        start2, end2 = range2
        
        # Calculate overlap
        overlap_start = max(start1, start2)
        overlap_end = min(end1, end2)
        
        if overlap_end <= overlap_start:
            return 0.0
        
        overlap_duration = (overlap_end - overlap_start).total_seconds()
        total_duration = max((end1 - start1).total_seconds(), (end2 - start2).total_seconds())
        
        return overlap_duration / total_duration if total_duration > 0 else 0.0
    
    # Helper methods
    async def _calculate_autocorrelation(self, time_series: np.ndarray, lag: int) -> float:
        """Calculate autocorrelation at specific lag"""
        if lag >= len(time_series) or lag <= 0:
            return 0.0
        
        n = len(time_series) - lag
        if n <= 1:
            return 0.0
        
        series1 = time_series[:-lag]
        series2 = time_series[lag:]
        
        correlation = np.corrcoef(series1, series2)[0, 1]
        return correlation if not np.isnan(correlation) else 0.0
    
    async def _calculate_r_squared(self, time_series: np.ndarray, slope: float) -> float:
        """Calculate R-squared for linear trend"""
        x = np.arange(len(time_series))
        y_pred = slope * x + np.mean(time_series)
        
        ss_res = np.sum((time_series - y_pred) ** 2)
        ss_tot = np.sum((time_series - np.mean(time_series)) ** 2)
        
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
        return max(0.0, r_squared)
    
    async def _group_consecutive_indices(self, indices: np.ndarray) -> List[List[int]]:
        """Group consecutive indices"""
        groups = []
        current_group = [indices[0]]
        
        for i in range(1, len(indices)):
            if indices[i] == indices[i-1] + 1:
                current_group.append(indices[i])
            else:
                groups.append(current_group)
                current_group = [indices[i]]
        
        groups.append(current_group)
        return groups
    
    async def get_pattern_synthesis_summary(self) -> Dict:
        """Get comprehensive pattern synthesis summary"""
        try:
            return {
                'detected_patterns': len(self.detected_patterns),
                'synthesized_patterns': len(self.synthesized_patterns),
                'pattern_type_distribution': {
                    ptype.value: len([p for p in self.detected_patterns.values() if p.pattern_type == ptype])
                    for ptype in PatternType
                },
                'synthesis_method_usage': {
                    method: len([s for s in self.synthesized_patterns.values() if s.synthesis_method == method])
                    for method in self.synthesis_engines.keys()
                },
                'average_pattern_confidence': float(np.mean([p.confidence for p in self.detected_patterns.values()])) if self.detected_patterns else 0.0,
                'average_synthesis_predictive_power': float(np.mean([s.predictive_power for s in self.synthesized_patterns.values()])) if self.synthesized_patterns else 0.0
            }
            
        except Exception as e:
            logger.error("Pattern synthesis summary generation failed", error=str(e))
            return {'summary_available': False, 'error': str(e)}
