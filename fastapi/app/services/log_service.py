from typing import Optional
from sqlalchemy.orm import Session
from ..models.log import Log, LogLevel


class LogService:
    """
    Service for creating and managing system logs.
    """
    
    @staticmethod
    def create_log(
        db: Session,
        level: LogLevel,
        message: str,
        user_id: Optional[int] = None,
        details: Optional[str] = None,
        ip_address: Optional[str] = None,
        dns_record_id: Optional[int] = None
    ) -> Log:
        """
        Create a new log entry.
        
        Args:
            db: Database session
            level: Log level (INFO, WARNING, ERROR, SUCCESS)
            message: Log message
            user_id: Optional user ID related to this log
            details: Optional additional details
            ip_address: Optional IP address
            dns_record_id: Optional DNS record ID
            
        Returns:
            Created log object
        """
        log = Log(
            level=level,
            message=message,
            user_id=user_id,
            details=details,
            ip_address=ip_address,
            dns_record_id=dns_record_id
        )
        
        db.add(log)
        db.commit()
        db.refresh(log)
        
        return log
    
    @staticmethod
    def get_logs(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[int] = None
    ) -> list[Log]:
        """
        Get paginated logs, optionally filtered by user.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            user_id: Optional user ID to filter logs
            
        Returns:
            List of log objects
        """
        query = db.query(Log)
        
        if user_id is not None:
            query = query.filter(Log.user_id == user_id)
        
        return query.order_by(Log.created_at.desc()).offset(skip).limit(limit).all() 