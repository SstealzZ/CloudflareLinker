from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from .base import BaseModel


class DNSRecord(BaseModel):
    """
    Model for DNS record configurations managed via Cloudflare.
    
    Attributes:
        user_id: Foreign key to the user who owns this record
        zone_id: Cloudflare Zone ID
        zone_name: Human-readable domain name
        record_id: Cloudflare DNS record ID
        record_type: Type of DNS record (A, AAAA, CNAME, etc.)
        record_name: DNS record name (subdomain)
        content: Current IP address or target of the record
        ttl: Time to live in seconds
        proxied: Whether the record is proxied through Cloudflare
        auto_update: Whether the record should be auto-updated
        last_updated_ip: The IP that was last set
    """
    __tablename__ = "dns_records"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    zone_id = Column(String(32), index=True, nullable=False)
    zone_name = Column(String(255), nullable=False)
    record_id = Column(String(32), index=True, nullable=False)
    record_type = Column(String(10), nullable=False)
    record_name = Column(String(255), nullable=False)
    content = Column(String(255), nullable=False)
    ttl = Column(Integer, default=1)  # 1 = Auto
    proxied = Column(Boolean, default=True)
    auto_update = Column(Boolean, default=True)
    last_updated_ip = Column(String(45), nullable=True)
    
    # Relationship
    user = relationship("User", back_populates="dns_records") 