import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pickle
import joblib

# ML Libraries
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import xgboost as xgb
import lightgbm as lgb

# Deep Learning
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

import structlog

logger = structlog.get_logger()

class MLEngine:
    """Machine Learning Engine for VedhaVriddhi Analytics"""
    
    def __init__(self, settings):
        self.settings = settings
        self.models = {}
        self.scalers = {}
        self.model_metadata = {}
        self.models_loaded = False
        
        # Model types
        self.model_types = {
            'yield_forecast': 'regression',
            'credit_spread_prediction': 'regression', 
            'default_probability': 'classification',
            'price_movement': 'regression',
            'volatility_forecast': 'regression'
        }
        
    async def initialize(self):
        """Initialize ML engine"""
        logger.info("Initializing ML Engine")
        try:
            await self.load_models()
            await self.load_scalers()
            self.models_loaded = True
            logger.info("ML Engine initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize ML Engine", error=str(e))
            raise
    
    async def load_models(self):
        """Load pre-trained models"""
        try:
            model_configs = {
                'yield_forecast': {
                    'type': 'xgboost',
                    'features': ['current_yield', 'duration', 'sector_spread', 'macro_indicators'],
                    'target': 'yield_change_1d',
                    'lookback': 30
                },
                'credit_spread_prediction': {
                    'type': 'lightgbm',
                    'features': ['rating', 'sector', 'maturity', 'liquidity_score'],
                    'target': 'spread_change',
                    'lookback': 60
                },
                'default_probability': {
                    'type': 'neural_network',
                    'features': ['financial_ratios', 'market_indicators', 'macro_factors'],
                    'target': 'default_12m',
                    'lookback': 252
                }
            }
            
            for model_name, config in model_configs.items():
                try:
                    # Try to load existing model
                    model_path = f"/app/models/{model_name}.joblib"
                    model = joblib.load(model_path)
                    self.models[model_name] = model
                    self.model_metadata[model_name] = config
                    logger.info(f"Loaded existing model: {model_name}")
                except FileNotFoundError:
                    # Create new model if doesn't exist
                    model = self._create_model(config['type'])
                    self.models[model_name] = model
                    self.model_metadata[model_name] = config
                    logger.info(f"Created new model: {model_name}")
                    
        except Exception as e:
            logger.error("Failed to load models", error=str(e))
            # Create default models
            await self._create_default_models()
    
    def _create_model(self, model_type: str):
        """Create a new model based on type"""
        if model_type == 'xgboost':
            return xgb.XGBRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42
            )
        elif model_type == 'lightgbm':
            return lgb.LGBMRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42
            )
        elif model_type == 'neural_network':
            return self._create_neural_network()
        else:
            return GradientBoostingRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            )
    
    def _create_neural_network(self):
        """Create neural network model"""
        model = keras.Sequential([
            layers.Dense(128, activation='relu', input_shape=(10,)),
            layers.Dropout(0.2),
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(32, activation='relu'),
            layers.Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    async def _create_default_models(self):
        """Create default models when none exist"""
        logger.info("Creating default ML models")
        
        # Simple models for demonstration
        self.models['yield_forecast'] = GradientBoostingRegressor(random_state=42)
        self.models['credit_spread_prediction'] = RandomForestRegressor(random_state=42)
        self.models['default_probability'] = GradientBoostingRegressor(random_state=42)
        
        # Default metadata
        for model_name in self.models:
            self.model_metadata[model_name] = {
                'created': datetime.utcnow().isoformat(),
                'version': '1.0.0',
                'status': 'untrained'
            }
    
    async def load_scalers(self):
        """Load feature scalers"""
        try:
            for model_name in self.models:
                scaler_path = f"/app/scalers/{model_name}_scaler.joblib"
                try:
                    scaler = joblib.load(scaler_path)
                    self.scalers[model_name] = scaler
                except FileNotFoundError:
                    # Create new scaler
                    self.scalers[model_name] = StandardScaler()
                    
        except Exception as e:
            logger.error("Failed to load scalers", error=str(e))
    
    async def predict(self, model_type: str, features: List[float], horizon: int = 1) -> Dict[str, Any]:
        """Generate ML predictions"""
        try:
            if model_type not in self.models:
                raise ValueError(f"Model type {model_type} not found")
            
            model = self.models[model_type]
            scaler = self.scalers.get(model_type)
            
            # Prepare features
            features_array = np.array(features).reshape(1, -1)
            
            # Scale features if scaler exists
            if scaler and hasattr(scaler, 'transform'):
                try:
                    features_scaled = scaler.transform(features_array)
                except Exception as e:
                    logger.warning(f"Scaling failed for {model_type}, using raw features", error=str(e))
                    features_scaled = features_array
            else:
                features_scaled = features_array
            
            # Generate prediction
            if hasattr(model, 'predict'):
                if isinstance(model, keras.Model):
                    # Neural network prediction
                    prediction = model.predict(features_scaled, verbose=0)[0][0]
                else:
                    # Sklearn-style prediction
                    prediction = model.predict(features_scaled)[0]
            else:
                # Fallback to random prediction
                prediction = np.random.normal(0, 1)
            
            # Calculate confidence interval (simplified)
            confidence = self._calculate_prediction_confidence(model_type, features_scaled)
            
            return {
                'model_type': model_type,
                'prediction': float(prediction),
                'confidence': confidence,
                'horizon_days': horizon,
                'features_used': len(features),
                'timestamp': datetime.utcnow().isoformat(),
                'model_version': self.model_metadata.get(model_type, {}).get('version', '1.0.0')
            }
            
        except Exception as e:
            logger.error(f"Prediction failed for {model_type}", error=str(e))
            return {
                'model_type': model_type,
                'prediction': 0.0,
                'confidence': 0.0,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _calculate_prediction_confidence(self, model_type: str, features: np.ndarray) -> float:
        """Calculate prediction confidence score"""
        try:
            model = self.models[model_type]
            
            # For tree-based models, use prediction variance
            if hasattr(model, 'estimators_'):
                predictions = []
                for estimator in model.estimators_[:min(10, len(model.estimators_))]:
                    if hasattr(estimator, 'predict'):
                        pred = estimator.predict(features)[0]
                        predictions.append(pred)
                
                if predictions:
                    variance = np.var(predictions)
                    # Convert variance to confidence (0-1 scale)
                    confidence = max(0, min(1, 1 - (variance / (1 + variance))))
                    return float(confidence)
            
            # Default confidence
            return 0.75
            
        except Exception as e:
            logger.warning(f"Confidence calculation failed for {model_type}", error=str(e))
            return 0.5
    
    async def retrain_models(self):
        """Retrain all models with latest data"""
        logger.info("Starting model retraining")
        
        try:
            for model_name in self.models:
                await self._retrain_single_model(model_name)
            
            # Save models after retraining
            await self._save_models()
            
            logger.info("Model retraining completed successfully")
            
        except Exception as e:
            logger.error("Model retraining failed", error=str(e))
    
    async def _retrain_single_model(self, model_name: str):
        """Retrain a single model"""
        try:
            logger.info(f"Retraining model: {model_name}")
            
            # Get training data (placeholder - would fetch from database)
            training_data = await self._get_training_data(model_name)
            
            if not training_data or len(training_data) < 100:
                logger.warning(f"Insufficient training data for {model_name}")
                return
            
            # Prepare features and targets
            X, y = self._prepare_training_data(training_data, model_name)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Scale features
            scaler = self.scalers[model_name]
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train model
            model = self.models[model_name]
            
            if isinstance(model, keras.Model):
                # Neural network training
                model.fit(
                    X_train_scaled, y_train,
                    validation_data=(X_test_scaled, y_test),
                    epochs=50,
                    batch_size=32,
                    verbose=0
                )
            else:
                # Sklearn-style training
                model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = model.predict(X_test_scaled)
            if isinstance(model, keras.Model):
                y_pred = y_pred.flatten()
                
            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # Update metadata
            self.model_metadata[model_name].update({
                'last_trained': datetime.utcnow().isoformat(),
                'mse': float(mse),
                'mae': float(mae),
                'r2_score': float(r2),
                'training_samples': len(X_train),
                'test_samples': len(X_test)
            })
            
            logger.info(f"Model {model_name} retrained - R2: {r2:.3f}, MSE: {mse:.6f}")
            
        except Exception as e:
            logger.error(f"Failed to retrain {model_name}", error=str(e))
    
    async def _get_training_data(self, model_name: str) -> List[Dict]:
        """Get training data for a model (placeholder)"""
        # This would fetch real data from TimeSeries DB
        # For now, generate synthetic data
        np.random.seed(42)
        n_samples = 1000
        
        if model_name == 'yield_forecast':
            data = []
            for i in range(n_samples):
                data.append({
                    'current_yield': np.random.normal(6.5, 1.5),
                    'duration': np.random.uniform(1, 10),
                    'sector_spread': np.random.normal(1.2, 0.5),
                    'macro_indicator': np.random.normal(0, 1),
                    'target': np.random.normal(0.01, 0.05)  # Daily yield change
                })
            return data
        
        return []
    
    def _prepare_training_data(self, data: List[Dict], model_name: str) -> tuple:
        """Prepare training data for model"""
        df = pd.DataFrame(data)
        
        # Extract features and target based on model type
        if model_name == 'yield_forecast':
            feature_cols = ['current_yield', 'duration', 'sector_spread', 'macro_indicator']
            target_col = 'target'
        else:
            # Default: use all numeric columns except target
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            feature_cols = [col for col in numeric_cols if col != 'target']
            target_col = 'target'
        
        X = df[feature_cols].values
        y = df[target_col].values if target_col in df.columns else np.random.normal(0, 1, len(df))
        
        return X, y
    
    async def _save_models(self):
        """Save trained models and scalers"""
        try:
            import os
            os.makedirs("/app/models", exist_ok=True)
            os.makedirs("/app/scalers", exist_ok=True)
            
            for model_name, model in self.models.items():
                # Save model
                if isinstance(model, keras.Model):
                    model.save(f"/app/models/{model_name}.h5")
                else:
                    joblib.dump(model, f"/app/models/{model_name}.joblib")
                
                # Save scaler
                if model_name in self.scalers:
                    joblib.dump(self.scalers[model_name], f"/app/scalers/{model_name}_scaler.joblib")
            
            # Save metadata
            with open("/app/models/metadata.json", "w") as f:
                import json
                json.dump(self.model_metadata, f, indent=2)
            
            logger.info("Models and scalers saved successfully")
            
        except Exception as e:
            logger.error("Failed to save models", error=str(e))
    
    async def stop(self):
        """Stop ML engine"""
        logger.info("Stopping ML Engine")
        # Save models before stopping
        await self._save_models()
