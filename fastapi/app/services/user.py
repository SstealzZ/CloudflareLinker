from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from ..db.session import get_db
from ..core.config import settings
from ..core.security import verify_password, get_password_hash, encrypt_api_key
from ..schemas.user import UserCreate, UserUpdate
from ..models.user import User
from ..schemas.token import TokenPayload

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


class UserService:
    """
    Service for user operations.
    """
    
    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            db: Database session
            username: Username to look up
            
        Returns:
            User object if found, None otherwise
        """
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            db: Database session
            email: Email to look up
            
        Returns:
            User object if found, None otherwise
        """
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            db: Database session
            user_id: User ID to look up
            
        Returns:
            User object if found, None otherwise
        """
        return db.query(User).filter(User.id == user_id).first()
    
    @classmethod
    def create_user(cls, db: Session, user_in: UserCreate) -> User:
        """
        Create a new user.
        
        Args:
            db: Database session
            user_in: User creation data
            
        Returns:
            Created user object
        """
        # Check if username or email already exists
        if cls.get_by_username(db, user_in.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )
        if cls.get_by_email(db, user_in.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        
        # Create user
        encrypted_api_key = encrypt_api_key(user_in.cloudflare_api_key)
        
        user = User(
            username=user_in.username,
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            cloudflare_api_key=encrypted_api_key,
            cloudflare_email=user_in.cloudflare_email,
            is_token=user_in.is_token
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # If this is the first user, mark setup as complete
        if db.query(User).count() == 1:
            settings.FIRST_TIME_SETUP = False
            
        return user
    
    @classmethod
    def update_user(cls, db: Session, user_id: int, user_in: UserUpdate) -> User:
        """
        Update a user.
        
        Args:
            db: Database session
            user_id: ID of user to update
            user_in: User update data
            
        Returns:
            Updated user object
            
        Raises:
            HTTPException: If user is not found
        """
        user = cls.get_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        
        # Update simple fields
        if user_in.email is not None:
            user.email = user_in.email
        
        # Update password if provided
        if user_in.password is not None:
            user.hashed_password = get_password_hash(user_in.password)
            
        # Update Cloudflare credentials if provided
        if user_in.cloudflare_api_key is not None:
            user.cloudflare_api_key = encrypt_api_key(user_in.cloudflare_api_key)
        
        if user_in.cloudflare_email is not None:
            user.cloudflare_email = user_in.cloudflare_email
            
        if user_in.is_token is not None:
            user.is_token = user_in.is_token
        
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
        
    @staticmethod
    def authenticate(db: Session, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user.
        
        Args:
            db: Database session
            username: Username for authentication
            password: Password for authentication
            
        Returns:
            User object if authentication successful, None otherwise
        """
        user = UserService.get_by_username(db, username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    @staticmethod
    def get_current_user(
        db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
    ) -> User:
        """
        Get current user from JWT token.
        
        Args:
            db: Database session
            token: JWT token
            
        Returns:
            Current user object
            
        Raises:
            HTTPException: If authentication fails
        """
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            token_data = TokenPayload(**payload)
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
            
        user = UserService.get_by_id(db, token_data.sub)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user",
            )
        return user 