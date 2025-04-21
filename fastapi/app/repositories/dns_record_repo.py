from typing import List, Optional
from sqlalchemy.orm import Session
from ..models.dns_record import DNSRecord


class DnsRecordRepo:
    """
    Repository for DNS record database operations.
    
    This class provides methods for CRUD operations on DNS records,
    abstracting the database operations from the business logic.
    """

    @staticmethod
    def create(
        db: Session,
        user_id: int,
        zone_id: str,
        zone_name: str,
        record_id: str,
        record_name: str,
        record_type: str,
        content: str,
        ttl: int = 1,
        proxied: bool = True,
        auto_update: bool = False
    ) -> DNSRecord:
        """
        Create a new DNS record.
        
        Args:
            db: Database session
            user_id: ID of the user who owns this record
            zone_id: Cloudflare zone ID
            zone_name: Cloudflare zone name (domain)
            record_id: Cloudflare record ID
            record_name: DNS record name
            record_type: DNS record type (A, AAAA, CNAME, etc.)
            content: Record content (IP address or domain)
            ttl: Time to live (1 = auto)
            proxied: Whether the record is proxied through Cloudflare
            auto_update: Whether the record should be auto-updated
            
        Returns:
            Created DNS record
        """
        dns_record = DNSRecord(
            user_id=user_id,
            zone_id=zone_id,
            zone_name=zone_name,
            record_id=record_id,
            record_name=record_name,
            record_type=record_type,
            content=content,
            ttl=ttl,
            proxied=proxied,
            auto_update=auto_update
        )
        
        db.add(dns_record)
        db.commit()
        db.refresh(dns_record)
        return dns_record
    
    @staticmethod
    def get_by_id(db: Session, record_id: int) -> Optional[DNSRecord]:
        """
        Get a DNS record by ID.
        
        Args:
            db: Database session
            record_id: ID of the record to fetch
            
        Returns:
            DNS record if found, None otherwise
        """
        return db.query(DNSRecord).filter(DNSRecord.id == record_id).first()
    
    @staticmethod
    def get_by_user_id(db: Session, user_id: int) -> List[DNSRecord]:
        """
        Get all DNS records for a user.
        
        Args:
            db: Database session
            user_id: ID of the user
            
        Returns:
            List of DNS records
        """
        return db.query(DNSRecord).filter(DNSRecord.user_id == user_id).all()
    
    @staticmethod
    def get_all_auto_update(db: Session) -> List[DNSRecord]:
        """
        Get all DNS records with auto_update enabled.
        
        Args:
            db: Database session
            
        Returns:
            List of DNS records with auto_update enabled
        """
        return db.query(DNSRecord).filter(DNSRecord.auto_update == True).all()
    
    @staticmethod
    def update(db: Session, record_id: int, **kwargs) -> Optional[DNSRecord]:
        """
        Update a DNS record.
        
        Args:
            db: Database session
            record_id: ID of the record to update
            **kwargs: Fields to update
            
        Returns:
            Updated DNS record if found, None otherwise
        """
        record = db.query(DNSRecord).filter(DNSRecord.id == record_id).first()
        if not record:
            return None
            
        for key, value in kwargs.items():
            if hasattr(record, key):
                setattr(record, key, value)
                
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def delete(db: Session, record_id: int) -> bool:
        """
        Delete a DNS record.
        
        Args:
            db: Database session
            record_id: ID of the record to delete
            
        Returns:
            True if record was deleted, False otherwise
        """
        record = db.query(DNSRecord).filter(DNSRecord.id == record_id).first()
        if not record:
            return False
            
        db.delete(record)
        db.commit()
        return True 