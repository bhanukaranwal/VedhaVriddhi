import asyncio
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass
from sklearn.decomposition import PCA, TruncatedSVD
from sklearn.manifold import TSNE, UMAP
from sklearn.preprocessing import StandardScaler
import structlog

logger = structlog.get_logger()

@dataclass
class DimensionalModel:
    """Dimensional model representation"""
    model_id: str
    model_type: str
    original_dimensions: int
    reduced_dimensions: int
    explained_variance_ratio: Optional[List[float]]
    model_parameters: Dict[str, Any]
    trained_at: datetime

class AdvancedDimensionalModeling:
    """Advanced dimensional modeling for high-dimensional financial data"""
    
    def __init__(self):
        self.models: Dict[str, DimensionalModel] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        self.model_implementations: Dict[str, Any] = {}
        
    async def initialize(self):
        """Initialize dimensional modeling system"""
        logger.info("Initializing Advanced Dimensional Modeling")
        logger.info("Advanced Dimensional Modeling initialized successfully")
    
    async def create_dimensional_model(self,
                                     model_type: str,
                                     training_data: np.ndarray,
                                     target_dimensions: int,
                                     model_parameters: Dict = None) -> str:
        """Create and train dimensional reduction model"""
        try:
            model_id = f"dim_model_{model_type}_{datetime.utcnow().timestamp()}"
            original_dimensions = training_data.shape[1]
            
            # Standardize data
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(training_data)
            self.scalers[model_id] = scaler
            
            # Create and train model
            if model_type.lower() == 'pca':
                model, explained_variance = await self._train_pca_model(
                    scaled_data, target_dimensions, model_parameters or {}
                )
            elif model_type.lower() == 'tsne':
                model, explained_variance = await self._train_tsne_model(
                    scaled_data, target_dimensions, model_parameters or {}
                )
            elif model_type.lower() == 'umap':
                model, explained_variance = await self._train_umap_model(
                    scaled_data, target_dimensions, model_parameters or {}
                )
            elif model_type.lower() == 'svd':
                model, explained_variance = await self._train_svd_model(
                    scaled_data, target_dimensions, model_parameters or {}
                )
            else:
                raise ValueError(f"Unsupported model type: {model_type}")
            
            # Store model
            self.model_implementations[model_id] = model
            
            # Create model record
            dim_model = DimensionalModel(
                model_id=model_id,
                model_type=model_type.upper(),
                original_dimensions=original_dimensions,
                reduced_dimensions=target_dimensions,
                explained_variance_ratio=explained_variance,
                model_parameters=model_parameters or {},
                trained_at=datetime.utcnow()
            )
            
            self.models[model_id] = dim_model
            
            logger.info(f"Created {model_type.upper()} model reducing from {original_dimensions} to {target_dimensions} dimensions")
            return model_id
            
        except Exception as e:
            logger.error("Dimensional model creation failed", error=str(e))
            raise
    
    async def _train_pca_model(self, data: np.ndarray, n_components: int, parameters: Dict) -> Tuple[PCA, List[float]]:
        """Train PCA model"""
        pca = PCA(
            n_components=n_components,
            random_state=parameters.get('random_state', 42)
        )
        
        pca.fit(data)
        explained_variance = pca.explained_variance_ratio_.tolist()
        
        return pca, explained_variance
    
    async def _train_tsne_model(self, data: np.ndarray, n_components: int, parameters: Dict) -> Tuple[Any, None]:
        """Train t-SNE model"""
        tsne = TSNE(
            n_components=n_components,
            perplexity=parameters.get('perplexity', 30),
            n_iter=parameters.get('n_iter', 300),
            random_state=parameters.get('random_state', 42),
            learning_rate=parameters.get('learning_rate', 200.0)
        )
        
        # t-SNE doesn't support transform, so we store the fitted data
        embedded_data = tsne.fit_transform(data)
        
        # Create a wrapper that stores the embedding
        class TSNEWrapper:
            def __init__(self, embedding):
                self.embedding = embedding
                self.n_components = n_components
            
            def transform(self, X):
                # For new data, would need to use approximation methods
                # For now, return the original embedding for training data
                return self.embedding[:len(X)]
        
        return TSNEWrapper(embedded_data), None
    
    async def _train_umap_model(self, data: np.ndarray, n_components: int, parameters: Dict) -> Tuple[Any, None]:
        """Train UMAP model"""
        try:
            import umap
            reducer = umap.UMAP(
                n_components=n_components,
                n_neighbors=parameters.get('n_neighbors', 15),
                min_dist=parameters.get('min_dist', 0.1),
                random_state=parameters.get('random_state', 42)
            )
            
            reducer.fit(data)
            return reducer, None
            
        except ImportError:
            logger.warning("UMAP not installed, falling back to PCA")
            return await self._train_pca_model(data, n_components, parameters)
    
    async def _train_svd_model(self, data: np.ndarray, n_components: int, parameters: Dict) -> Tuple[TruncatedSVD, List[float]]:
        """Train Truncated SVD model"""
        svd = TruncatedSVD(
            n_components=n_components,
            random_state=parameters.get('random_state', 42),
            n_iter=parameters.get('n_iter', 5)
        )
        
        svd.fit(data)
        explained_variance = svd.explained_variance_ratio_.tolist()
        
        return svd, explained_variance
    
    async def transform_data(self, model_id: str, data: np.ndarray) -> np.ndarray:
        """Transform data using trained dimensional model"""
        try:
            if model_id not in self.models:
                raise ValueError(f"Model {model_id} not found")
            
            model = self.model_implementations[model_id]
            scaler = self.scalers[model_id]
            
            # Scale data using same scaler as training
            scaled_data = scaler.transform(data)
            
            # Transform data
            transformed_data = model.transform(scaled_data)
            
            return transformed_data
            
        except Exception as e:
            logger.error("Data transformation failed", error=str(e))
            raise
    
    async def analyze_dimensional_structure(self, model_id: str) -> Dict:
        """Analyze the dimensional structure of the model"""
        try:
            if model_id not in self.models:
                raise ValueError(f"Model {model_id} not found")
            
            dim_model = self.models[model_id]
            model = self.model_implementations[model_id]
            
            analysis = {
                'model_id': model_id,
                'model_type': dim_model.model_type,
                'dimensionality_reduction_ratio': dim_model.reduced_dimensions / dim_model.original_dimensions,
                'information_preservation': await self._calculate_information_preservation(dim_model, model)
            }
            
            # Model-specific analysis
            if dim_model.model_type == 'PCA':
                analysis.update(await self._analyze_pca_structure(model, dim_model))
            elif dim_model.model_type == 'SVD':
                analysis.update(await self._analyze_svd_structure(model, dim_model))
            
            return analysis
            
        except Exception as e:
            logger.error("Dimensional structure analysis failed", error=str(e))
            raise
    
    async def _calculate_information_preservation(self, dim_model: DimensionalModel, model: Any) -> Dict:
        """Calculate information preservation metrics"""
        if dim_model.explained_variance_ratio is not None:
            total_variance_explained = sum(dim_model.explained_variance_ratio)
            
            return {
                'total_variance_explained': float(total_variance_explained),
                'cumulative_variance_by_component': np.cumsum(dim_model.explained_variance_ratio).tolist(),
                'information_loss': float(1.0 - total_variance_explained)
            }
        else:
            # For methods without explained variance
            return {
                'total_variance_explained': None,
                'information_preservation_estimate': 0.8,  # Rough estimate
                'information_loss': 0.2
            }
    
    async def _analyze_pca_structure(self, pca_model: PCA, dim_model: DimensionalModel) -> Dict:
        """Analyze PCA-specific structure"""
        components = pca_model.components_
        
        # Component analysis
        component_norms = np.linalg.norm(components, axis=1)
        component_sparsity = np.count_nonzero(np.abs(components) > 0.1, axis=1) / components.shape[1]
        
        return {
            'pca_analysis': {
                'component_norms': component_norms.tolist(),
                'component_sparsity': component_sparsity.tolist(),
                'most_important_features': await self._identify_important_features(components),
                'component_interpretability': await self._assess_component_interpretability(components)
            }
        }
    
    async def _analyze_svd_structure(self, svd_model: TruncatedSVD, dim_model: DimensionalModel) -> Dict:
        """Analyze SVD-specific structure"""
        components = svd_model.components_
        singular_values = svd_model.singular_values_
        
        return {
            'svd_analysis': {
                'singular_values': singular_values.tolist(),
                'singular_value_decay': (singular_values[:-1] / singular_values[1:]).tolist(),
                'rank_approximation_quality': float(np.sum(singular_values**2) / np.sum(svd_model.explained_variance_ratio_)),
                'component_analysis': await self._analyze_svd_components(components)
            }
        }
    
    async def _identify_important_features(self, components: np.ndarray) -> List[Dict]:
        """Identify most important features in each component"""
        important_features = []
        
        for i, component in enumerate(components):
            # Get top features by absolute weight
            feature_importance = np.abs(component)
            top_indices = np.argsort(feature_importance)[-5:][::-1]  # Top 5
            
            important_features.append({
                'component': i,
                'top_features': [
                    {'feature_index': int(idx), 'weight': float(component[idx]), 'importance': float(feature_importance[idx])}
                    for idx in top_indices
                ]
            })
        
        return important_features
    
    async def _assess_component_interpretability(self, components: np.ndarray) -> List[float]:
        """Assess interpretability of each component"""
        interpretability_scores = []
        
        for component in components:
            # Interpretability based on sparsity and concentration
            abs_weights = np.abs(component)
            
            # Gini coefficient for concentration
            sorted_weights = np.sort(abs_weights)
            n = len(sorted_weights)
            gini = (2 * np.sum((np.arange(1, n+1)) * sorted_weights)) / (n * np.sum(sorted_weights)) - (n + 1) / n
            
            # Sparsity measure
            sparsity = np.count_nonzero(abs_weights > 0.1) / len(abs_weights)
            
            # Combined interpretability (higher Gini and moderate sparsity = more interpretable)
            interpretability = gini * (1 - abs(sparsity - 0.3))  # Optimal sparsity around 30%
            interpretability_scores.append(float(interpretability))
        
        return interpretability_scores
    
    async def _analyze_svd_components(self, components: np.ndarray) -> Dict:
        """Analyze SVD components"""
        return {
            'component_orthogonality': float(np.mean(np.abs(np.dot(components, components.T) - np.eye(len(components))))),
            'component_concentration': [float(np.max(np.abs(comp)) / np.mean(np.abs(comp))) for comp in components],
            'component_stability': await self._assess_component_stability(components)
        }
    
    async def _assess_component_stability(self, components: np.ndarray) -> float:
        """Assess stability of components"""
        # Mock stability assessment
        # In practice, would use bootstrap sampling or cross-validation
        component_vars = np.var(components, axis=1)
        stability_score = 1.0 / (1.0 + np.mean(component_vars))
        
        return float(stability_score)
    
    async def compare_dimensional_models(self, model_ids: List[str]) -> Dict:
        """Compare multiple dimensional models"""
        try:
            if len(model_ids) < 2:
                raise ValueError("Need at least 2 models to compare")
            
            models_info = []
            for model_id in model_ids:
                if model_id not in self.models:
                    raise ValueError(f"Model {model_id} not found")
                
                dim_model = self.models[model_id]
                analysis = await self.analyze_dimensional_structure(model_id)
                
                models_info.append({
                    'model_id': model_id,
                    'model_type': dim_model.model_type,
                    'dimensions': dim_model.reduced_dimensions,
                    'variance_explained': analysis.get('information_preservation', {}).get('total_variance_explained'),
                    'information_loss': analysis.get('information_preservation', {}).get('information_loss')
                })
            
            # Comparison metrics
            comparison = {
                'models_compared': models_info,
                'best_variance_explained': max(
                    (m for m in models_info if m['variance_explained'] is not None),
                    key=lambda x: x['variance_explained'],
                    default=None
                ),
                'most_efficient': min(
                    models_info,
                    key=lambda x: x['dimensions'] / (x['variance_explained'] or 0.1)
                ),
                'comparison_timestamp': datetime.utcnow().isoformat()
            }
            
            return comparison
            
        except Exception as e:
            logger.error("Model comparison failed", error=str(e))
            raise
    
    async def get_dimensional_modeling_summary(self) -> Dict:
        """Get comprehensive dimensional modeling summary"""
        try:
            total_models = len(self.models)
            
            if total_models == 0:
                return {'models_available': False}
            
            # Model type distribution
            model_types = {}
            for model in self.models.values():
                model_types[model.model_type] = model_types.get(model.model_type, 0) + 1
            
            # Dimension reduction statistics
            reduction_ratios = [
                model.reduced_dimensions / model.original_dimensions
                for model in self.models.values()
            ]
            
            # Variance explained statistics
            variance_explained = [
                sum(model.explained_variance_ratio) if model.explained_variance_ratio else None
                for model in self.models.values()
            ]
            variance_explained = [v for v in variance_explained if v is not None]
            
            return {
                'models_available': True,
                'total_models': total_models,
                'model_type_distribution': model_types,
                'dimensionality_reduction_stats': {
                    'average_reduction_ratio': float(np.mean(reduction_ratios)),
                    'min_reduction_ratio': float(np.min(reduction_ratios)),
                    'max_reduction_ratio': float(np.max(reduction_ratios))
                },
                'information_preservation_stats': {
                    'average_variance_explained': float(np.mean(variance_explained)) if variance_explained else None,
                    'models_with_variance_data': len(variance_explained)
                },
                'summary_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Dimensional modeling summary generation failed", error=str(e))
            return {'models_available': False, 'error': str(e)}
