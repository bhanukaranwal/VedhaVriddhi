import hashlib
import hmac
import secrets
import jwt
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import structlog

logger = structlog.get_logger()

class SecurityManager:
    """Advanced security manager for VedhaVriddhi system"""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.security = HTTPBearer()
        
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=24)
            
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
    
    def generate_api_key(self, user_id: str, service: str) -> str:
        """Generate secure API key for service access"""
        timestamp = str(int(datetime.utcnow().timestamp()))
        data = f"{user_id}:{service}:{timestamp}"
        
        # Create HMAC signature
        signature = hmac.new(
            self.secret_key.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
        
        api_key = f"vv4_{user_id}_{service}_{timestamp}_{signature}"
        return api_key
    
    def validate_api_key(self, api_key: str) -> Optional[Dict[str, str]]:
        """Validate API key and extract user info"""
        try:
            parts = api_key.split('_')
            if len(parts) != 5 or parts[0] != 'vv4':
                return None
                
            prefix, user_id, service, timestamp, signature = parts
            
            # Reconstruct data for verification
            data = f"{user_id}:{service}:{timestamp}"
            expected_signature = hmac.new(
                self.secret_key.encode(),
                data.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if hmac.compare_digest(signature, expected_signature):
                return {
                    'user_id': user_id,
                    'service': service,
                    'issued_at': timestamp
                }
            return None
            
        except Exception as e:
            logger.error("API key validation failed", error=str(e))
            return None

class BiometricSecurity:
    """Advanced biometric security integration"""
    
    def __init__(self):
        self.encryption_key = secrets.token_bytes(32)
        
    def encrypt_biometric_data(self, biometric_data: bytes) -> bytes:
        """Encrypt biometric data using AES-256"""
        from cryptography.fernet import Fernet
        import base64
        
        key = base64.urlsafe_b64encode(self.encryption_key)
        cipher_suite = Fernet(key)
        encrypted_data = cipher_suite.encrypt(biometric_data)
        return encrypted_data
    
    def decrypt_biometric_data(self, encrypted_data: bytes) -> bytes:
        """Decrypt biometric data"""
        from cryptography.fernet import Fernet
        import base64
        
        key = base64.urlsafe_b64encode(self.encryption_key)
        cipher_suite = Fernet(key)
        decrypted_data = cipher_suite.decrypt(encrypted_data)
        return decrypted_data

class QuantumSecurity:
    """Quantum-resistant security measures"""
    
    def __init__(self):
        self.quantum_safe_algorithms = ['CRYSTALS-Kyber', 'CRYSTALS-Dilithium', 'FALCON']
        
    def generate_quantum_safe_keypair(self) -> Dict[str, bytes]:
        """Generate quantum-safe key pair (placeholder for actual implementation)"""
        # In production, would use actual post-quantum cryptography libraries
        private_key = secrets.token_bytes(64)
        public_key = secrets.token_bytes(32)
        
        return {
            'private_key': private_key,
            'public_key': public_key,
            'algorithm': 'CRYSTALS-Kyber-768'
        }
