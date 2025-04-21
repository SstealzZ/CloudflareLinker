from sqlalchemy import Column, String, Boolean
from .base import BaseModel


class User(BaseModel):
    """
    User model for authentication and storing Cloudflare API credentials.
    
    Attributes:
        username: Unique username for the user
        hashed_password: Securely hashed password
        email: User's email address
        cloudflare_api_key: Encrypted Cloudflare API key
        cloudflare_email: Email associated with Cloudflare account
        is_active: Whether the user account is active
        is_token: Whether the Cloudflare API key is a token
    """
    __tablename__ = "users"
    
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    cloudflare_api_key = Column(String(255), nullable=True)
    cloudflare_email = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    is_token = Column(Boolean, default=True) 