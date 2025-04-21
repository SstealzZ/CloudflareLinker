from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ...core import security
from ...core.config import settings
from ...db.session import get_db
from ...models.user import User
from ...schemas.token import Token
from ...schemas.user import UserCreate, UserResponse
from ...services.user import UserService
from ...services.cloudflare import CloudflareService

router = APIRouter()

@router.post("/setup", response_model=Token)
async def setup(*, db: Session = Depends(get_db), user_in: UserCreate) -> Any:
    """
    Initial system setup - creates the first admin user.
    
    Args:
        db: Database session
        user_in: User input schema
    
    Returns:
        JWT access token
        
    Raises:
        HTTPException: If the system is already set up
    """
    if not settings.FIRST_TIME_SETUP:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="System is already set up",
        )
        
    # Valider les informations Cloudflare
    try:
        # Initialiser le service avec jeton API Cloudflare obligatoire
        cf_service = CloudflareService(
            api_key=user_in.cloudflare_api_key, 
            email=user_in.cloudflare_email,
            is_encrypted=False,
            is_token=True
        )
        
        # Tester l'accès
        zones = await cf_service.get_zones()
        if not zones:
            raise ValueError("Impossible de récupérer les zones avec le jeton API Cloudflare fourni")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Jeton API Cloudflare invalide: {str(e)}",
        )

    # Créer l'utilisateur
    user = UserService.create_user(db, user_in)
    
    # Générer et retourner le token JWT
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/login", response_model=Token)
async def login(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    Login for users.
    
    Args:
        db: Database session
        form_data: Login credentials
    
    Returns:
        JWT access token
        
    Raises:
        HTTPException: If the credentials are invalid
    """
    user = UserService.authenticate(
        db, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants incorrects",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur inactif",
        )
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserResponse)
def get_current_user(
    db: Session = Depends(get_db), user: User = Depends(UserService.get_current_user)
) -> Any:
    """
    Get current user information.
    
    Args:
        db: Database session
        user: Current authenticated user
    
    Returns:
        Current user information
    """
    return user 