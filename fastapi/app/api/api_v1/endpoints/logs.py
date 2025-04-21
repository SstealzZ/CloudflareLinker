from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ....models.log import Log
from ....models.user import User
from ....schemas.log import Log as LogSchema
from ....services.log_service import LogService
from ...deps import get_db, get_current_active_user

router = APIRouter()


@router.get("/", response_model=List[LogSchema])
async def read_logs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve logs for the current user.
    
    Args:
        skip: Number of logs to skip
        limit: Maximum number of logs to return
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of logs
    """
    logs = LogService.get_logs(
        db=db,
        skip=skip,
        limit=limit,
        user_id=current_user.id
    )
    
    return logs


@router.get("/system", response_model=List[LogSchema])
async def read_system_logs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve system logs (logs not associated with a specific user).
    
    Args:
        skip: Number of logs to skip
        limit: Maximum number of logs to return
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of system logs
    """
    logs = db.query(Log).filter(
        Log.user_id.is_(None)
    ).order_by(Log.created_at.desc()).offset(skip).limit(limit).all()
    
    return logs 