from typing import Optional
from pydantic import BaseModel, Field


class DNSRecordBase(BaseModel):
    """
    Base DNS record schema with common fields.
    
    Attributes:
        zone_id: Cloudflare Zone ID
        zone_name: Human-readable domain name
        record_type: Type of DNS record (A, AAAA, CNAME, etc.)
        record_name: DNS record name (subdomain)
        content: IP address or target of the record
        ttl: Time to live in seconds
        proxied: Whether the record is proxied through Cloudflare
        auto_update: Whether the record should be auto-updated
    """
    zone_id: str
    zone_name: str
    record_type: str
    record_name: str
    content: str
    ttl: int = 1
    proxied: bool = True
    auto_update: bool = True


class DNSRecordCreate(DNSRecordBase):
    """
    Schema for DNS record creation.
    """
    pass


class DNSRecordUpdate(BaseModel):
    """
    Schema for updating DNS record details.
    
    Attributes:
        record_type: New record type
        record_name: New record name
        content: New content
        ttl: New TTL
        proxied: New proxied status
        auto_update: New auto-update status
    """
    record_type: Optional[str] = None
    record_name: Optional[str] = None
    content: Optional[str] = None
    ttl: Optional[int] = None
    proxied: Optional[bool] = None
    auto_update: Optional[bool] = None


class DNSRecordInDB(DNSRecordBase):
    """
    Schema for DNS record as stored in the database.
    
    Attributes:
        id: Database record ID
        user_id: ID of user who owns this record
        record_id: Cloudflare DNS record ID
        last_updated_ip: The last IP address that was set
    """
    id: int
    user_id: int
    record_id: str
    last_updated_ip: Optional[str] = None
    
    class Config:
        """
        Pydantic configuration for ORM mode.
        """
        orm_mode = True


class DNSRecord(DNSRecordInDB):
    """
    Public DNS record schema for API responses.
    """
    pass 