from sqlalchemy import Column, String, Integer, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
import enum
from .base import BaseModel


class LogLevel(str, enum.Enum):
    """
    Enumeration of possible log levels.
    """
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"


class Log(BaseModel):
    """
    Model for storing system logs and user activity.
    
    Attributes:
        user_id: Foreign key to the user associated with this log (optional)
        level: Log level (INFO, WARNING, ERROR, SUCCESS)
        message: Log message content
        details: Additional details or error information
        ip_address: IP address related to the log entry (optional)
        dns_record_id: Related DNS record ID (optional)
    """
    __tablename__ = "logs"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    level = Column(Enum(LogLevel), default=LogLevel.INFO, nullable=False)
    message = Column(String(255), nullable=False)
    details = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    dns_record_id = Column(Integer, ForeignKey("dns_records.id"), nullable=True)
    
    # Relationships
    user = relationship("User", backref="logs")
    dns_record = relationship("DNSRecord", backref="logs") 