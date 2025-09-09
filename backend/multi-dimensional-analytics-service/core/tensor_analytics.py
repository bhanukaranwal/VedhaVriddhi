import asyncio
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass
import structlog

logger = structlog.get_logger()

@dataclass
class TensorDecomposition:
    """Tensor decomposition result"""
    decomposition_id: str
    decomposition_type: str
    original_shape: Tuple[int, ...]
    rank: int
    factors: List[np.ndarray]
    reconstruction_error: float
    explained_variance: float

class AdvancedTensorAnalytics:
    """Multi-dimensional tensor analytics for financial data"""
    
    def __init__(self):
        self.tensor_cache: Dict[str, np.ndarray] = {}
        self.decompositions: Dict[str, TensorDecomposition] = {}
        self.analysis_history: List[Dict] = []
        
    async def initialize(self):
        """Initialize tensor analytics system"""
        logger.info("Initializing Advanced Tensor Analytics")
        logger.info("Advanced Tensor Analytics initialized successfully")
    
    async def create_financial_tensor(self, 
                                    data_sources: Dict[str, np.ndarray],
                                    dimensions: List[str]) -> str:
        """Create multi-dimensional financial tensor"""
        try:
            tensor_id = f"tensor_{datetime.utcnow().timestamp()}"
            
            # Validate dimension alignment
            shapes = [data.shape for data in data_sources.values()]
            if not all(len(shape) == len(shapes[0]) for shape in shapes):
                raise ValueError("All data sources must have same number of dimensions")
            
            # Stack data sources into tensor
            data_arrays = list(data_sources.values())
            financial_tensor = np.stack(data_arrays, axis=0)
            
            self.tensor_cache[tensor_id] = financial_tensor
            
            logger.info(f"Created financial tensor {tensor_id} with shape {financial_tensor.shape}")
            return tensor_id
            
        except Exception as e:
            logger.error("Financial tensor creation failed", error=str(e))
            raise
    
    async def decompose_tensor(self, tensor_id: str, 
                             method: str = "cp", 
                             rank: int = 3) -> TensorDecomposition:
        """Perform tensor decomposition"""
        try:
            tensor = self.tensor_cache.get(tensor_id)
            if tensor is None:
                raise ValueError(f"Tensor {tensor_id} not found")
            
            decomposition_id = f"decomp_{tensor_id}_{method}_{rank}"
            
            if method.lower() == "cp":
                factors, reconstruction_error = await self._cp_decomposition(tensor, rank)
            elif method.lower() == "tucker":
                factors, reconstruction_error = await self._tucker_decomposition(tensor, rank)
            else:
                raise ValueError(f"Unsupported decomposition method: {method}")
            
            # Calculate explained variance
            original_norm = np.linalg.norm(tensor)
            explained_variance = 1.0 - (reconstruction_error / original_norm) if original_norm > 0 else 0.0
            
            # Create decomposition record
            decomposition = TensorDecomposition(
                decomposition_id=decomposition_id,
                decomposition_type=method.upper(),
                original_shape=tensor.shape,
                rank=rank,
                factors=factors,
                reconstruction_error=reconstruction_error,
                explained_variance=explained_variance
            )
            
            self.decompositions[decomposition_id] = decomposition
            
            logger.info(f"Completed {method.upper()} decomposition with {explained_variance:.2%} explained variance")
            return decomposition
            
        except Exception as e:
            logger.error("Tensor decomposition failed", error=str(e))
            raise
    
    async def _cp_decomposition(self, tensor: np.ndarray, rank: int) -> Tuple[List[np.ndarray], float]:
        """Canonical Polyadic (CP) decomposition"""
        # Mock CP decomposition implementation
        factors = []
        for mode_size in tensor.shape:
            factor = np.random.randn(mode_size, rank)
            factors.append(factor)
        
        # Reconstruct tensor for error calculation
        reconstructed = await self._reconstruct_cp(factors)
        reconstruction_error = np.linalg.norm(tensor - reconstructed)
        
        return factors, reconstruction_error
    
    async def _tucker_decomposition(self, tensor: np.ndarray, rank: int) -> Tuple[List[np.ndarray], float]:
        """Tucker decomposition"""
        # Mock Tucker decomposition
        factors = []
        core_shape = tuple(min(dim, rank) for dim in tensor.shape)
        
        # Factor matrices
        for i, mode_size in enumerate(tensor.shape):
            factor = np.random.randn(mode_size, core_shape[i])
            factors.append(factor)
        
        # Core tensor
        core = np.random.randn(*core_shape)
        factors.append(core)  # Add core as last "factor"
        
        # Mock reconstruction error
        reconstruction_error = np.linalg.norm(tensor) * 0.1  # 10% error
        
        return factors, reconstruction_error
    
    async def _reconstruct_cp(self, factors: List[np.ndarray]) -> np.ndarray:
        """Reconstruct tensor from CP factors"""
        # Simplified CP reconstruction
        rank = factors[0].shape[1]
        shape = tuple(factor.shape[0] for factor in factors)
        
        reconstructed = np.zeros(shape)
        for r in range(rank):
            component = factors[0][:, r]
            for factor in factors[1:]:
                component = np.outer(component, factor[:, r])
            
            # Reshape to original tensor shape
            component = component.reshape(shape)
            reconstructed += component
        
        return reconstructed
    
    async def analyze_tensor_patterns(self, tensor_id: str) -> Dict:
        """Analyze patterns in financial tensor"""
        try:
            tensor = self.tensor_cache.get(tensor_id)
            if tensor is None:
                raise ValueError(f"Tensor {tensor_id} not found")
            
            # Temporal patterns
            temporal_patterns = await self._analyze_temporal_patterns(tensor)
            
            # Cross-sectional patterns
            cross_sectional_patterns = await self._analyze_cross_sectional_patterns(tensor)
            
            # Multi-dimensional correlations
            correlations = await self._analyze_multidimensional_correlations(tensor)
            
            # Anomaly detection
            anomalies = await self._detect_tensor_anomalies(tensor)
            
            analysis_result = {
                'tensor_id': tensor_id,
                'tensor_shape': tensor.shape,
                'temporal_patterns': temporal_patterns,
                'cross_sectional_patterns': cross_sectional_patterns,
                'multidimensional_correlations': correlations,
                'anomalies_detected': anomalies,
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
            self.analysis_history.append(analysis_result)
            return analysis_result
            
        except Exception as e:
            logger.error("Tensor pattern analysis failed", error=str(e))
            raise
    
    async def _analyze_temporal_patterns(self, tensor: np.ndarray) -> Dict:
        """Analyze temporal patterns in tensor"""
        # Assume last dimension is time
        time_axis = -1
        
        # Temporal statistics
        temporal_mean = np.mean(tensor, axis=time_axis)
        temporal_std = np.std(tensor, axis=time_axis)
        temporal_trend = np.polyfit(range(tensor.shape[time_axis]), 
                                  np.mean(tensor, axis=tuple(range(len(tensor.shape)-1))), 1)[0]
        
        return {
            'temporal_mean': float(np.mean(temporal_mean)),
            'temporal_volatility': float(np.mean(temporal_std)),
            'trend_coefficient': float(temporal_trend),
            'seasonality_detected': abs(temporal_trend) > 0.01,
            'temporal_complexity': float(np.std(temporal_std))
        }
    
    async def _analyze_cross_sectional_patterns(self, tensor: np.ndarray) -> Dict:
        """Analyze cross-sectional patterns"""
        # Analyze patterns across first dimension (e.g., assets)
        cross_sectional_corr = np.corrcoef(tensor.reshape(tensor.shape[0], -1))
        
        return {
            'average_correlation': float(np.mean(cross_sectional_corr[np.triu_indices_from(cross_sectional_corr, k=1)])),
            'max_correlation': float(np.max(cross_sectional_corr[np.triu_indices_from(cross_sectional_corr, k=1)])),
            'clustering_detected': np.max(cross_sectional_corr) > 0.7,
            'diversification_score': 1.0 - abs(np.mean(cross_sectional_corr))
        }
    
    async def _analyze_multidimensional_correlations(self, tensor: np.ndarray) -> Dict:
        """Analyze correlations across multiple dimensions"""
        correlations = {}
        
        # Pairwise dimension correlations
        for i in range(len(tensor.shape)):
            for j in range(i+1, len(tensor.shape)):
                # Flatten tensor along other dimensions
                dims_to_keep = [i, j]
                dims_to_flatten = [k for k in range(len(tensor.shape)) if k not in dims_to_keep]
                
                if dims_to_flatten:
                    flattened = np.mean(tensor, axis=tuple(dims_to_flatten))
                    corr_matrix = np.corrcoef(flattened)
                    avg_corr = np.mean(corr_matrix[np.triu_indices_from(corr_matrix, k=1)])
                    correlations[f'dims_{i}_{j}'] = float(avg_corr)
        
        return correlations
    
    async def _detect_tensor_anomalies(self, tensor: np.ndarray) -> Dict:
        """Detect anomalies in tensor data"""
        # Statistical anomaly detection
        tensor_flat = tensor.flatten()
        mean_val = np.mean(tensor_flat)
        std_val = np.std(tensor_flat)
        
        # Z-score based anomalies
        z_scores = np.abs(tensor_flat - mean_val) / std_val
        anomaly_threshold = 3.0
        anomaly_count = np.sum(z_scores > anomaly_threshold)
        
        return {
            'anomaly_count': int(anomaly_count),
            'anomaly_percentage': float(anomaly_count / len(tensor_flat) * 100),
            'max_z_score': float(np.max(z_scores)),
            'anomaly_threshold': anomaly_threshold,
            'anomalies_detected': anomaly_count > 0
        }
    
    async def get_tensor_analytics_summary(self) -> Dict:
        """Get comprehensive tensor analytics summary"""
        try:
            return {
                'total_tensors': len(self.tensor_cache),
                'total_decompositions': len(self.decompositions),
                'total_analyses': len(self.analysis_history),
                'tensor_shapes': [tensor.shape for tensor in self.tensor_cache.values()],
                'decomposition_methods_used': list(set(d.decomposition_type for d in self.decompositions.values())),
                'average_explained_variance': np.mean([d.explained_variance for d in self.decompositions.values()]) if self.decompositions else 0.0,
                'analytics_available': True
            }
            
        except Exception as e:
            logger.error("Tensor analytics summary generation failed", error=str(e))
            return {'analytics_available': False, 'error': str(e)}
