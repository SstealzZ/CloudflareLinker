from datetime import datetime, timedelta
from typing import Any, Optional, Union
import os
import base64

from jose import jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet

from .config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Encryption for sensitive data like API keys
# Utilise une clé d'encryption fixe depuis les settings au lieu d'en générer une nouvelle à chaque démarrage
ENCRYPTION_KEY = settings.ENCRYPTION_KEY
if not ENCRYPTION_KEY:
    # Fallback si la clé n'est pas définie dans les settings
    ENCRYPTION_KEY = base64.urlsafe_b64encode(settings.SECRET_KEY.encode()[:32]).decode()

# S'assurer que la clé est au bon format
try:
    fernet = Fernet(ENCRYPTION_KEY.encode())
except Exception:
    # Si la clé n'est pas au bon format, créer une clé valide
    fernet = Fernet(Fernet.generate_key())


def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT access token.
    
    Args:
        subject: Subject to encode in the token (usually user ID)
        expires_delta: Optional expiration time delta
        
    Returns:
        Encoded JWT token as string
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a password against its hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password to verify against
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Creates a hash of the password.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def encrypt_api_key(api_key: str) -> str:
    """
    Encrypts sensitive data like API keys.
    
    Args:
        api_key: API key to encrypt
        
    Returns:
        Encrypted API key
    """
    return fernet.encrypt(api_key.encode()).decode()


def decrypt_api_key(encrypted_api_key: str) -> str:
    """
    Decrypts encrypted API keys.
    
    Args:
        encrypted_api_key: Encrypted API key
        
    Returns:
        Decrypted API key
    """
    try:
        return fernet.decrypt(encrypted_api_key.encode()).decode()
    except Exception:
        # Comme nous avons eu un problème de déchiffrement, c'est probablement parce que
        # la clé n'est pas chiffrée ou utilise une autre clé d'encryption
        # Retournons la clé telle quelle
        return encrypted_api_key 