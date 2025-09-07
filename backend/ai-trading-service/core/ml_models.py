import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import joblib
import structlog

from models import MLModelConfig, TradeSignal, TradingSide, StrategyType

logger = structlog.get_logger()

class MLModelService:
    """Machine learning model management service"""
    
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.model_configs: Dict[str, MLModelConfig] = {}
        self.prediction_cache = {}
        
    async def initialize(self):
        """Initialize ML model service"""
        logger.info("Initializing ML Model Service")
        
        # Load model configurations
        await self._load_model_configs()
        
        # Load pre-trained models
        await self._load_models()
        
        # Start model update tasks
        asyncio.create_task(self._periodic_model_updates())
        
        logger.info(f"Initialized {len(self.models)} ML models")
    
    async def _load_model_configs(self):
        """Load ML model configurations"""
        self.model_configs = {
            'yield_predictor': MLModelConfig(
                model_id='yield_predictor',
                model_type='regression',
                input_features=[
                    'current_yield', 'duration', 'credit_spread', 
                    'volatility', 'volume', 'momentum_5d', 'momentum_20d'
                ],
                output_format='yield_change_1d',
                confidence_threshold=0.7,
                retrain_frequency_hours=6
            ),
            'price_direction': MLModelConfig(
                model_id='price_direction',
                model_type='classification',
                input_features=[
                    'price_momentum', 'volume_ratio', 'rsi', 'macd',
                    'bollinger_position', 'vix', 'term_structure_slope'
                ],
                output_format='direction_probability',
                confidence_threshold=0.75,
                retrain_frequency_hours=4
            ),
            'volatility_forecast': MLModelConfig(
                model_id='volatility_forecast',
                model_type='regression',
                input_features=[
                    'realized_vol_5d', 'realized_vol_20d', 'implied_vol',
                    'vix_level', 'vix_change', 'market_stress_indicator'
                ],
                output_format='volatility_1d',
                confidence_threshold=0.6,
                retrain_frequency_hours=12
            )
        }
    
    async def _load_models(self):
        """Load pre-trained models"""
        for model_id, config in self.model_configs.items():
            try:
                # In production, load actual models from storage
                # For now, create mock model objects
                self.models[model_id] = MockMLModel(model_id, config)
                logger.info(f"Loaded model: {model_id}")
                
            except Exception as e:
                logger.error(f"Failed to load model {model_id}", error=str(e))
    
    async def _periodic_model_updates(self):
        """Periodically update and retrain models"""
        while True:
            try:
                current_time = datetime.utcnow()
                
                for model_id, config in self.model_configs.items():
                    # Check if model needs retraining
                    if self._needs_retraining(model_id, config, current_time):
                        await self._retrain_model(model_id)
                
                # Wait 1 hour before next check
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error("Model update error", error=str(e))
                await asyncio.sleep(1800)  # Wait 30 minutes on error
    
    def _needs_retraining(self, model_id: str, config: MLModelConfig, current_time: datetime) -> bool:
        """Check if model needs retraining"""
        if not config.last_trained:
            return True
        
        hours_since_training = (current_time - config.last_trained).total_seconds() / 3600
        return hours_since_training >= config.retrain_frequency_hours
    
    async def _retrain_model(self, model_id: str):
        """Retrain specific model"""
        try:
            logger.info(f"Starting retraining for model: {model_id}")
            
            # Get training data
            training_data = await self._get_training_data(model_id)
            
            # Retrain model
            model = self.models.get(model_id)
            if model and training_data:
                await model.retrain(training_data)
                
                # Update config
                self.model_configs[model_id].last_trained = datetime.utcnow()
                
                logger.info(f"Successfully retrained model: {model_id}")
            
        except Exception as e:
            logger.error(f"Model retraining failed for {model_id}", error=str(e))
    
    async def _get_training_data(self, model_id: str) -> Optional[pd.DataFrame]:
        """Get training data for model"""
        # In production, this would fetch real market data
        # For now, return mock data
        
        np.random.seed(42)  # For reproducible results
        n_samples = 1000
        
        config = self.model_configs[model_id]
        n_features = len(config.input_features)
        
        # Generate mock training data
        X = np.random.randn(n_samples, n_features)
        
        if config.model_type == 'regression':
            y = np.random.randn(n_samples) * 0.01  # Small price changes
        else:  # classification
            y = np.random.choice([0, 1], size=n_samples, p=[0.6, 0.4])
        
        # Create DataFrame
        feature_names = config.input_features + ['target']
        data = np.column_stack([X, y])
        
        return pd.DataFrame(data, columns=feature_names)
    
    async def generate_predictions(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate predictions from all models"""
        predictions = {}
        
        for model_id, model in self.models.items():
            try:
                # Prepare features for model
                features = self._prepare_features(model_id, market_data)
                
                if features:
                    # Generate prediction
                    prediction = await model.predict(features)
                    predictions[model_id] = prediction
                    
            except Exception as e:
                logger.error(f"Prediction failed for model {model_id}", error=str(e))
        
        return predictions
    
    def _prepare_features(self, model_id: str, market_data: Dict[str, Any]) -> Optional[np.ndarray]:
        """Prepare features for specific model"""
        config = self.model_configs.get(model_id)
        if not config:
            return None
        
        # Extract required features from market data
        features = []
        for feature_name in config.input_features:
            if feature_name in market_data:
                features.append(market_data[feature_name])
            else:
                # Use default/mock value if feature not available
                features.append(0.0)
        
        return np.array(features).reshape(1, -1)
    
    async def get_model_performance(self, model_id: str) -> Dict[str, Any]:
        """Get performance metrics for specific model"""
        model = self.models.get(model_id)
        config = self.model_configs.get(model_id)
        
        if not model or not config:
            return {}
        
        return {
            'model_id': model_id,
            'model_type': config.model_type,
            'confidence_threshold': config.confidence_threshold,
            'last_trained': config.last_trained.isoformat() if config.last_trained else None,
            'performance_metrics': config.performance_metrics,
            'input_features': config.input_features
        }

class MockMLModel:
    """Mock ML model for demonstration"""
    
    def __init__(self, model_id: str, config: MLModelConfig):
        self.model_id = model_id
        self.config = config
        self.performance_metrics = {
            'accuracy': 0.75,
            'precision': 0.73,
            'recall': 0.71,
            'f1_score': 0.72
        }
    
    async def predict(self, features: np.ndarray) -> Dict[str, Any]:
        """Generate mock prediction"""
        # Simulate prediction time
        await asyncio.sleep(0.01)
        
        if self.config.model_type == 'regression':
            # Regression prediction
            prediction_value = np.random.normal(0.001, 0.005)  # Small yield/price change
            confidence = np.random.uniform(0.6, 0.95)
            
            return {
                'prediction': float(prediction_value),
                'confidence': float(confidence),
                'model_id': self.model_id,
                'timestamp': datetime.utcnow().isoformat()
            }
        else:
            # Classification prediction
            probability = np.random.uniform(0.5, 0.95)
            prediction_class = 1 if probability > 0.5 else 0
            
            return {
                'prediction_class': prediction_class,
                'probability': float(probability),
                'confidence': float(abs(probability - 0.5) * 2),  # Distance from 0.5
                'model_id': self.model_id,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def retrain(self, training_data: pd.DataFrame):
        """Mock model retraining"""
        logger.info(f"Retraining model {self.model_id} with {len(training_data)} samples")
        
        # Simulate training time
        await asyncio.sleep(1)
        
        # Update performance metrics (mock improvement)
        self.performance_metrics['accuracy'] = min(0.95, self.performance_metrics['accuracy'] * 1.01)
        
        logger.info(f"Model {self.model_id} retrained successfully")
