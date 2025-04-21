from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class TimestampMixin:
    """
    A mixin that adds created_at and updated_at timestamp fields to models.
    
    Attributes:
        created_at: Timestamp when the record was created
        updated_at: Timestamp when the record was last updated
    """
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=False)


class BaseModel(Base, TimestampMixin):
    """
    Base model for all database models providing ID and timestamp fields.
    
    Attributes:
        id: Primary key ID for the model
    """
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True) 