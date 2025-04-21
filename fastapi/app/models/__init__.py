from .base import Base, BaseModel
from .user import User
from .dns_record import DNSRecord
from .log import Log, LogLevel

# Update the User model to include the back reference
from sqlalchemy.orm import relationship
User.dns_records = relationship("DNSRecord", back_populates="user") 