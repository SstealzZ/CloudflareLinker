from typing import Optional
from pydantic import BaseModel, EmailStr, validator, Field


class UserBase(BaseModel):
    """
    Base user schema with common fields.
    
    Attributes:
        username: User's username
        email: User's email address
        is_active: Whether the user account is active
    """
    username: str
    email: EmailStr
    is_active: bool = True


class UserCreate(UserBase):
    """
    Schema for user creation.
    
    Attributes:
        password: Plain text password (will be hashed)
        cloudflare_api_key: Cloudflare API key (token)
        cloudflare_email: Email associated with Cloudflare account (optional with token)
        is_token: Always True, only token authentication is supported
    """
    password: str
    cloudflare_api_key: str
    cloudflare_email: Optional[EmailStr] = None
    is_token: bool = True
    
    @validator("password")
    def password_must_be_strong(cls, v):
        """
        Validates that the password meets security requirements.
        
        Args:
            v: Password to validate
            
        Returns:
            Validated password
            
        Raises:
            ValueError: If password is too short
        """
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v
    
    @validator("is_token")
    def must_use_token(cls, v):
        """
        Validates that only token authentication is used.
        
        Args:
            v: is_token value
            
        Returns:
            Validated value (must be True)
            
        Raises:
            ValueError: If is_token is False
        """
        if not v:
            raise ValueError("Seule l'authentification par jeton API est supportée")
        return v


class FirstTimeSetup(BaseModel):
    """
    Schema for first-time setup with admin user creation.
    
    Attributes:
        username: Admin username
        password: Admin password (will be hashed)
        email: Admin email address
        cloudflare_api_key: Cloudflare API token
        cloudflare_email: Email associated with Cloudflare account (optional with token)
        is_token: Always True, only token authentication is supported
    """
    username: str
    password: str
    email: EmailStr
    cloudflare_api_key: str
    cloudflare_email: Optional[EmailStr] = None
    is_token: bool = True
    
    @validator("password")
    def password_must_be_strong(cls, v):
        """
        Validates that the password meets security requirements.
        
        Args:
            v: Password to validate
            
        Returns:
            Validated password
            
        Raises:
            ValueError: If password is too short
        """
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v
    
    @validator("is_token")
    def must_use_token(cls, v):
        """
        Validates that only token authentication is used.
        
        Args:
            v: is_token value
            
        Returns:
            Validated value (must be True)
            
        Raises:
            ValueError: If is_token is False
        """
        if not v:
            raise ValueError("Seule l'authentification par jeton API est supportée")
        return v


class UserUpdate(BaseModel):
    """
    Schema for updating user details.
    
    Attributes:
        email: New email address
        cloudflare_api_key: New Cloudflare API key
        cloudflare_email: New Cloudflare account email
        is_token: Whether the Cloudflare API key is a token
    """
    email: Optional[EmailStr] = None
    cloudflare_api_key: Optional[str] = None
    cloudflare_email: Optional[EmailStr] = None
    is_token: Optional[bool] = None


class UserPasswordUpdate(BaseModel):
    """
    Schema for updating user password.
    
    Attributes:
        current_password: Current password for verification
        new_password: New password to set
    """
    current_password: str
    new_password: str
    
    @validator("new_password")
    def password_must_be_strong(cls, v):
        """
        Validates that the new password meets security requirements.
        
        Args:
            v: Password to validate
            
        Returns:
            Validated password
            
        Raises:
            ValueError: If password is too short
        """
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class UserInDB(UserBase):
    """
    Schema for user as stored in the database.
    
    Attributes:
        id: User ID
        is_active: Whether the user account is active
        cloudflare_email: Email associated with Cloudflare account
        is_token: Whether the Cloudflare API key is a token
    """
    id: int
    is_active: bool
    cloudflare_email: Optional[EmailStr] = None
    is_token: bool = False
    
    class Config:
        """
        Pydantic configuration for ORM mode.
        """
        orm_mode = True


class User(UserInDB):
    """
    Public user schema for API responses.
    """
    pass


class Token(BaseModel):
    """
    Schema for authentication token.
    
    Attributes:
        access_token: JWT access token
        token_type: Token type (always "bearer")
    """
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """
    Schema for data contained in a token.
    
    Attributes:
        username: Username from the token
    """
    username: Optional[str] = None 