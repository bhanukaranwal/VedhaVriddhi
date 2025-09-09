"""Common utilities for VedhaVriddhi services"""
import hashlib
import json
import time
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import structlog

logger = structlog.get_logger()

def generate_unique_id(prefix: str = "") -> str:
    """Generate unique ID with optional prefix"""
    timestamp = str(int(time.time() * 1000))  # milliseconds
    random_str = hashlib.md5(f"{timestamp}{time.time_ns()}".encode()).hexdigest()[:8]
    return f"{prefix}_{timestamp}_{random_str}" if prefix else f"{timestamp}_{random_str}"

def validate_json_data(data: Any) -> bool:
    """Validate if data is JSON serializable"""
    try:
        json.dumps(data)
        return True
    except (TypeError, ValueError):
        return False

def sanitize_financial_data(data: Dict) -> Dict:
    """Sanitize financial data for security"""
    sensitive_fields = ['ssn', 'tax_id', 'account_number', 'routing_number']
    sanitized = data.copy()
    
    for field in sensitive_fields:
        if field in sanitized:
            sanitized[field] = "*" * len(str(sanitized[field]))
    
    return sanitized

def calculate_portfolio_metrics(weights: List[float], returns: List[float], 
                              covariance_matrix: List[List[float]]) -> Dict:
    """Calculate basic portfolio metrics"""
    import numpy as np
    
    weights_array = np.array(weights)
    returns_array = np.array(returns)
    cov_matrix = np.array(covariance_matrix)
    
    portfolio_return = np.dot(weights_array, returns_array)
    portfolio_variance = np.dot(weights_array, np.dot(cov_matrix, weights_array))
    portfolio_volatility = np.sqrt(portfolio_variance)
    
    sharpe_ratio = portfolio_return / portfolio_volatility if portfolio_volatility > 0 else 0
    
    return {
        'expected_return': float(portfolio_return),
        'volatility': float(portfolio_volatility),
        'variance': float(portfolio_variance),
        'sharpe_ratio': float(sharpe_ratio)
    }

def format_currency(amount: float, currency: str = "USD") -> str:
    """Format currency with proper symbols and formatting"""
    currency_symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'JPY': '¥',
        'INR': '₹'
    }
    
    symbol = currency_symbols.get(currency, currency)
    return f"{symbol}{amount:,.2f}"

def get_utc_timestamp() -> datetime:
    """Get current UTC timestamp"""
    return datetime.now(timezone.utc)

def hash_sensitive_data(data: str, salt: str = "") -> str:
    """Hash sensitive data with optional salt"""
    return hashlib.sha256(f"{data}{salt}".encode()).hexdigest()

class PerformanceTimer:
    """Context manager for performance timing"""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        execution_time = time.time() - self.start_time
        logger.info(f"{self.operation_name} completed in {execution_time:.4f} seconds")

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator for retrying failed operations"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    logger.warning(f"Attempt {attempt + 1} failed: {e}, retrying in {delay}s")
                    time.sleep(delay)
                    
        def sync_wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    logger.warning(f"Attempt {attempt + 1} failed: {e}, retrying in {delay}s")
                    time.sleep(delay)
        
        import asyncio
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator
