from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ....core.config import settings
from ....core.security import create_access_token, verify_password, get_password_hash, encrypt_api_key
from ....models.user import User
from ....schemas.user import User as UserSchema, UserCreate, Token, FirstTimeSetup
from ....services.log_service import LogService
from ....models.log import LogLevel
from ...deps import get_db, get_current_active_user

router = APIRouter()


@router.post("/register", response_model=UserSchema)
def register_user(
    user_in: UserCreate, db: Session = Depends(get_db)
) -> Any:
    """
    Register a new user.
    
    Args:
        user_in: User data for registration
        db: Database session
        
    Returns:
        Created user
        
    Raises:
        HTTPException: If username or email is already registered
    """
    user = db.query(User).filter(User.username == user_in.username).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Check if there are any users in the system
    first_user = db.query(User).first() is None
    
    # Create the user
    encrypted_api_key = encrypt_api_key(user_in.cloudflare_api_key)
    db_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        cloudflare_api_key=encrypted_api_key,
        cloudflare_email=user_in.cloudflare_email,
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Log the registration
    LogService.create_log(
        db=db,
        level=LogLevel.INFO,
        message=f"User {db_user.username} registered successfully",
        user_id=db_user.id
    )
    
    return db_user


@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login.
    
    Args:
        db: Database session
        form_data: OAuth2 form with username and password
        
    Returns:
        JWT access token
        
    Raises:
        HTTPException: If login fails
    """
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Log the login
    LogService.create_log(
        db=db,
        level=LogLevel.INFO,
        message=f"User {user.username} logged in",
        user_id=user.id
    )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            subject=user.username, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserSchema)
def read_users_me(current_user: User = Depends(get_current_active_user)) -> Any:
    """
    Get current user information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user data
    """
    return current_user


@router.get("/setup-status")
def get_setup_status(db: Session = Depends(get_db)) -> dict:
    """
    Check if the application requires first-time setup.
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with setup status information
    """
    existing_user = db.query(User).first()
    needs_setup = settings.FIRST_TIME_SETUP and existing_user is None
    
    return {
        "needs_setup": needs_setup
    }


@router.post("/setup", response_model=Token)
def first_time_setup(
    setup_data: FirstTimeSetup, db: Session = Depends(get_db)
) -> Any:
    """
    First-time setup endpoint for creating the initial admin user.
    
    Args:
        setup_data: Admin user data and setup configuration
        db: Database session
        
    Returns:
        JWT access token for the created admin user
        
    Raises:
        HTTPException: If setup is not allowed or validation fails
    """
    validate_setup_is_allowed(db)
    
    admin_user = create_admin_user(db, setup_data)
    log_setup_completion(db, admin_user)
    
    settings.FIRST_TIME_SETUP = False
    
    return generate_access_token(admin_user.username)


def validate_setup_is_allowed(db: Session) -> None:
    """
    Validates that first-time setup is allowed to proceed.
    
    Args:
        db: Database session
        
    Raises:
        HTTPException: If setup is not allowed
    """
    if not settings.FIRST_TIME_SETUP:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="First-time setup is not allowed. System is already configured."
        )
    
    existing_user = db.query(User).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Setup is not allowed. Users already exist in the system."
        )


def create_admin_user(db: Session, setup_data: FirstTimeSetup) -> User:
    """
    Creates an admin user from the setup data.
    
    Args:
        db: Database session
        setup_data: Admin user data and setup configuration
        
    Returns:
        Created admin user
    """
    encrypted_api_key = encrypt_api_key(setup_data.cloudflare_api_key)
    admin_user = User(
        username=setup_data.username,
        email=setup_data.email,
        hashed_password=get_password_hash(setup_data.password),
        cloudflare_api_key=encrypted_api_key,
        cloudflare_email=setup_data.cloudflare_email,
        is_active=True,
    )
    
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    return admin_user


def log_setup_completion(db: Session, admin_user: User) -> None:
    """
    Logs the successful completion of the setup process.
    
    Args:
        db: Database session
        admin_user: The created admin user
    """
    LogService.create_log(
        db=db,
        level=LogLevel.INFO,
        message=f"Initial setup completed. Admin user {admin_user.username} created.",
        user_id=admin_user.id
    )


def generate_access_token(username: str) -> dict:
    """
    Generates a JWT access token for the given username.
    
    Args:
        username: Username to create token for
        
    Returns:
        Dictionary with access token and token type
    """
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            subject=username, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    } 