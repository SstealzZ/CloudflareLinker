from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...db.session import get_db
from ...models.user import User
from ...models.dns_record import DNSRecord
from ...models.log import Log, LogLevel
from ...schemas.dns import DNSRecordCreate, DNSRecordResponse, DNSRecordUpdate
from ...services.user import UserService
from ...services.cloudflare import CloudflareService
from ...services.log import LogService

router = APIRouter()

@router.get("/zones", response_model=dict)
async def get_zones(
    db: Session = Depends(get_db), 
    current_user: User = Depends(UserService.get_current_user)
) -> Any:
    """
    Get Cloudflare zones for the current user.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of Cloudflare zones
    """
    try:
        cf_service = CloudflareService(
            current_user.cloudflare_api_key, 
            current_user.cloudflare_email,
            is_token=current_user.is_token
        )
        zones = await cf_service.get_zones()
        return {"zones": zones}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get Cloudflare zones: {str(e)}",
        )

@router.get("/records/{zone_id}", response_model=dict)
async def get_dns_records(
    zone_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(UserService.get_current_user),
) -> Any:
    """
    Get DNS records for a zone.
    
    Args:
        zone_id: Cloudflare zone ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of DNS records
    """
    try:
        # Fetch from Cloudflare
        cf_service = CloudflareService(
            current_user.cloudflare_api_key, 
            current_user.cloudflare_email,
            is_token=current_user.is_token
        )
        cloudflare_records = await cf_service.get_dns_records(zone_id)
        
        # Fetch managed records from database
        managed_records = db.query(DNSRecord).filter(
            DNSRecord.user_id == current_user.id,
            DNSRecord.zone_id == zone_id
        ).all()
        
        # Build a dict of managed records for quick lookup
        managed_dict = {record.record_id: record for record in managed_records}
        
        # Merge Cloudflare data with DB data
        for record in cloudflare_records:
            if record["id"] in managed_dict:
                record["managed"] = True
                record["auto_update"] = managed_dict[record["id"]].auto_update
            else:
                record["managed"] = False
                record["auto_update"] = False
        
        return {
            "records": cloudflare_records,
            "zone_id": zone_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get DNS records: {str(e)}",
        )

@router.post("/records", response_model=DNSRecordResponse)
async def create_dns_record(
    record_in: DNSRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(UserService.get_current_user),
) -> Any:
    """
    Create a new DNS record.
    
    Args:
        record_in: DNS record to create
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Created DNS record
    """
    try:
        # Create record in Cloudflare
        cf_service = CloudflareService(
            current_user.cloudflare_api_key, 
            current_user.cloudflare_email,
            is_token=current_user.is_token
        )
        
        cf_record = await cf_service.create_dns_record(
            zone_id=record_in.zone_id,
            type=record_in.record_type,
            name=record_in.record_name,
            content=record_in.content,
            ttl=record_in.ttl,
            proxied=record_in.proxied
        )
        
        if not cf_record:
            raise Exception("Cloudflare API returned no data")
        
        # Create record in database
        db_record = DNSRecord(
            user_id=current_user.id,
            zone_id=record_in.zone_id,
            zone_name=record_in.zone_name,
            record_id=cf_record["id"],
            record_type=record_in.record_type,
            record_name=record_in.record_name,
            content=record_in.content,
            ttl=record_in.ttl,
            proxied=record_in.proxied,
            auto_update=record_in.auto_update
        )
        
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        
        # Log the action
        LogService.create_log(
            db=db,
            level=LogLevel.INFO,
            message=f"DNS record {record_in.record_name} created",
            user_id=current_user.id,
            record_id=db_record.id
        )
        
        return db_record
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create DNS record: {str(e)}",
        )

@router.put("/records/{record_id}", response_model=DNSRecordResponse)
async def update_dns_record(
    record_id: int,
    record_in: DNSRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(UserService.get_current_user),
) -> Any:
    """
    Update a DNS record.
    
    Args:
        record_id: ID of the DNS record to update
        record_in: Updated DNS record data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Updated DNS record
    """
    # Get record from database
    db_record = db.query(DNSRecord).filter(
        DNSRecord.id == record_id,
        DNSRecord.user_id == current_user.id
    ).first()
    
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DNS record not found",
        )
    
    try:
        # Update record in Cloudflare
        cf_service = CloudflareService(
            current_user.cloudflare_api_key, 
            current_user.cloudflare_email,
            is_token=current_user.is_token
        )
        
        old_content = db_record.content
        
        cf_record = await cf_service.update_dns_record(
            zone_id=db_record.zone_id,
            record_id=db_record.record_id,
            type=record_in.record_type or db_record.record_type,
            name=record_in.record_name or db_record.record_name,
            content=record_in.content or db_record.content,
            ttl=record_in.ttl or db_record.ttl,
            proxied=record_in.proxied if record_in.proxied is not None else db_record.proxied
        )
        
        if not cf_record:
            raise Exception("Cloudflare API returned no data")
        
        # Update record in database
        if record_in.record_type is not None:
            db_record.record_type = record_in.record_type
        if record_in.record_name is not None:
            db_record.record_name = record_in.record_name
        if record_in.content is not None:
            db_record.content = record_in.content
        if record_in.ttl is not None:
            db_record.ttl = record_in.ttl
        if record_in.proxied is not None:
            db_record.proxied = record_in.proxied
        if record_in.auto_update is not None:
            db_record.auto_update = record_in.auto_update
        
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        
        # Log the action
        LogService.create_log(
            db=db,
            level=LogLevel.INFO,
            message=f"DNS record {db_record.record_name} updated",
            user_id=current_user.id,
            record_id=db_record.id,
            ip_address=db_record.content if old_content != db_record.content else None
        )
        
        return db_record
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update DNS record: {str(e)}",
        )

@router.delete("/records/{record_id}", response_model=dict)
async def delete_dns_record(
    record_id: int,
    delete_from_cloudflare: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(UserService.get_current_user),
) -> Any:
    """
    Delete a DNS record.
    
    Args:
        record_id: ID of the DNS record to delete
        delete_from_cloudflare: Whether to also delete the record from Cloudflare
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Confirmation message
    """
    # Get record from database
    db_record = db.query(DNSRecord).filter(
        DNSRecord.id == record_id,
        DNSRecord.user_id == current_user.id
    ).first()
    
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DNS record not found",
        )
    
    try:
        record_name = db_record.record_name
        
        # Delete from Cloudflare if requested
        if delete_from_cloudflare:
            cf_service = CloudflareService(
                current_user.cloudflare_api_key, 
                current_user.cloudflare_email,
                is_token=current_user.is_token
            )
            
            success = await cf_service.delete_dns_record(
                zone_id=db_record.zone_id,
                record_id=db_record.record_id
            )
            
            if not success:
                raise Exception("Failed to delete record from Cloudflare")
        
        # Delete record from database
        db.delete(db_record)
        db.commit()
        
        # Log the action
        LogService.create_log(
            db=db,
            level=LogLevel.INFO,
            message=f"DNS record {record_name} deleted",
            user_id=current_user.id
        )
        
        return {"message": "DNS record deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete DNS record: {str(e)}",
        ) 