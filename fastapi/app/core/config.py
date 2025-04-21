import os
import secrets
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator


class Settings(BaseSettings):
    """
    Application settings and configuration.
    
    Attributes:
        API_V1_STR: API version prefix
        SECRET_KEY: Secret key for token generation
        ACCESS_TOKEN_EXPIRE_MINUTES: JWT token expiration time
        ALGORITHM: Algorithm used for JWT token generation
        DATABASE_URL: SQLite database connection URL
        CORS_ORIGINS: List of allowed CORS origins
        FIRST_TIME_SETUP: Boolean flag indicating if this is the first time the application is launched
    """
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ALGORITHM: str = "HS256"
    
    # Clé d'encryption pour les données sensibles
    ENCRYPTION_KEY: str = ""
    
    # Database
    DATABASE_URL: str = f"sqlite:///{os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'cloudflare_linker.db')}"
    
    # First time setup
    FIRST_TIME_SETUP: bool = True
    
    # CORS
    CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[AnyHttpUrl]:
        """
        Validates and assembles CORS origins configuration.
        
        Args:
            v: String or list of CORS origins
            
        Returns:
            List of validated CORS origin URLs
        """
        if isinstance(v, str) and not v.startswith("["):
            return [origin.strip() for origin in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        """
        Pydantic configuration settings.
        """
        case_sensitive = True
        env_file = ".env"


settings = Settings() 