from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from ..models.log import LogLevel


class LogBase(BaseModel):
    """
    Base log schema with common fields.
    
    Attributes:
        level: Log level (INFO, WARNING, ERROR, SUCCESS)
        message: Log message
        details: Additional details (optional)
        ip_address: IP address related to this log (optional)
    """
    level: LogLevel
    message: str
    details: Optional[str] = None
    ip_address: Optional[str] = None


class LogCreate(LogBase):
    """
    Schema for log creation.
    
    Attributes:
        user_id: ID of user associated with this log (optional)
        dns_record_id: ID of DNS record associated with this log (optional)
    """
    user_id: Optional[int] = None
    dns_record_id: Optional[int] = None


class LogInDB(LogBase):
    """
    Schema for log as stored in the database.
    
    Attributes:
        id: Log ID
        created_at: Timestamp when log was created
        user_id: ID of user associated with this log (optional)
        dns_record_id: ID of DNS record associated with this log (optional)
    """
    id: int
    created_at: datetime
    user_id: Optional[int] = None
    dns_record_id: Optional[int] = None
    
    class Config:
        """
        Pydantic configuration for ORM mode.
        """
        orm_mode = True


class Log(LogInDB):
    """
    Public log schema for API responses.
    """
    pass 