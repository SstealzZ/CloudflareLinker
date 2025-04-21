from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from ....core.security import decrypt_api_key
from ....models.dns_record import DNSRecord
from ....models.user import User
from ....models.log import LogLevel
from ....schemas.dns_record import DNSRecord as DNSRecordSchema, DNSRecordCreate, DNSRecordUpdate
from ....services.cloudflare import CloudflareService
from ....services.log_service import LogService
from ....services.ip_service import IPService
from ...deps import get_db, get_current_active_user

router = APIRouter()


@router.get("/", response_model=List[DNSRecordSchema])
async def read_dns_records(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve DNS records for the current user.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of DNS records
    """
    records = db.query(DNSRecord).filter(
        DNSRecord.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return records


@router.get("/zones")
async def get_cloudflare_zones(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Retrieve Cloudflare zones (domains) for the current user.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of Cloudflare zones
    """
    # Initialize Cloudflare service
    cf_service = CloudflareService(
        api_key=current_user.cloudflare_api_key,
        email=current_user.cloudflare_email
    )
    
    # Get zones from Cloudflare
    zones = await cf_service.get_zones()
    
    if not zones:
        LogService.create_log(
            db=db,
            level=LogLevel.WARNING,
            message="No Cloudflare zones found",
            user_id=current_user.id
        )
        
        return {"zones": []}
    
    # Return formatted zones
    formatted_zones = [
        {
            "id": zone["id"],
            "name": zone["name"],
            "status": zone["status"],
            "paused": zone["paused"],
            "type": zone["type"]
        }
        for zone in zones
    ]
    
    return {"zones": formatted_zones}


@router.get("/current-ip")
async def get_current_ip(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get the current public IP address.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Current IP address
    """
    current_ip = await IPService.get_current_ip()
    
    if not current_ip:
        LogService.create_log(
            db=db,
            level=LogLevel.ERROR,
            message="Failed to get current IP address",
            user_id=current_user.id
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get current IP address"
        )
    
    return {"ip": current_ip}


@router.post("/", response_model=DNSRecordSchema)
async def create_dns_record(
    record_in: DNSRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create a new DNS record.
    
    Args:
        record_in: DNS record data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Created DNS record
        
    Raises:
        HTTPException: If Cloudflare API request fails
    """
    # Initialize Cloudflare service
    cf_service = CloudflareService(
        api_key=current_user.cloudflare_api_key,
        email=current_user.cloudflare_email
    )
    
    # Get current IP if it's an A/AAAA record and auto_update is True
    content = record_in.content
    if record_in.auto_update and record_in.record_type in ("A", "AAAA"):
        current_ip = await IPService.get_current_ip()
        if current_ip:
            content = current_ip
    
    # Create record in Cloudflare
    cf_record = await cf_service.create_dns_record(
        zone_id=record_in.zone_id,
        type=record_in.record_type,
        name=record_in.record_name,
        content=content,
        ttl=record_in.ttl,
        proxied=record_in.proxied
    )
    
    if not cf_record:
        # Log error
        LogService.create_log(
            db=db,
            level=LogLevel.ERROR,
            message="Failed to create DNS record in Cloudflare",
            user_id=current_user.id,
            details=f"Record: {record_in.record_name} ({record_in.record_type})",
            ip_address=content if record_in.record_type in ("A", "AAAA") else None
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create DNS record in Cloudflare"
        )
    
    # Create record in database
    current_ip = await IPService.get_current_ip() if record_in.auto_update else None
    
    db_record = DNSRecord(
        user_id=current_user.id,
        zone_id=record_in.zone_id,
        zone_name=record_in.zone_name,
        record_id=cf_record["id"],
        record_type=record_in.record_type,
        record_name=record_in.record_name,
        content=content,
        ttl=record_in.ttl,
        proxied=record_in.proxied,
        auto_update=record_in.auto_update,
        last_updated_ip=current_ip if record_in.auto_update else None
    )
    
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    
    # Log success
    LogService.create_log(
        db=db,
        level=LogLevel.SUCCESS,
        message=f"DNS record created: {record_in.record_name}",
        user_id=current_user.id,
        dns_record_id=db_record.id,
        ip_address=content if record_in.record_type in ("A", "AAAA") else None
    )
    
    return db_record


@router.get("/{record_id}", response_model=DNSRecordSchema)
async def read_dns_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific DNS record by ID.
    
    Args:
        record_id: DNS record ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        DNS record
        
    Raises:
        HTTPException: If record not found
    """
    record = db.query(DNSRecord).filter(
        DNSRecord.id == record_id, DNSRecord.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DNS record not found"
        )
    
    return record


@router.put("/{record_id}", response_model=DNSRecordSchema)
async def update_dns_record(
    record_id: int,
    record_in: DNSRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update a DNS record.
    
    Args:
        record_id: DNS record ID
        record_in: Updated DNS record data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Updated DNS record
        
    Raises:
        HTTPException: If record not found or update fails
    """
    db_record = db.query(DNSRecord).filter(
        DNSRecord.id == record_id, DNSRecord.user_id == current_user.id
    ).first()
    
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DNS record not found"
        )
    
    # Initialize Cloudflare service
    cf_service = CloudflareService(
        api_key=current_user.cloudflare_api_key,
        email=current_user.cloudflare_email
    )
    
    # Get updated values
    record_type = record_in.record_type or db_record.record_type
    record_name = record_in.record_name or db_record.record_name
    content = record_in.content or db_record.content
    ttl = record_in.ttl if record_in.ttl is not None else db_record.ttl
    proxied = record_in.proxied if record_in.proxied is not None else db_record.proxied
    
    # Update record in Cloudflare
    cf_record = await cf_service.update_dns_record(
        zone_id=db_record.zone_id,
        record_id=db_record.record_id,
        type=record_type,
        name=record_name,
        content=content,
        ttl=ttl,
        proxied=proxied
    )
    
    if not cf_record:
        # Log error
        LogService.create_log(
            db=db,
            level=LogLevel.ERROR,
            message=f"Failed to update DNS record: {db_record.record_name}",
            user_id=current_user.id,
            dns_record_id=db_record.id,
            ip_address=content if record_type in ("A", "AAAA") else None
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update DNS record in Cloudflare"
        )
    
    # Update record in database
    update_data = record_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_record, key, value)
    
    # If we're updating content and it's an IP record, update last_updated_ip
    if "content" in update_data and record_type in ("A", "AAAA"):
        db_record.last_updated_ip = content
    
    db.commit()
    db.refresh(db_record)
    
    # Log success
    LogService.create_log(
        db=db,
        level=LogLevel.SUCCESS,
        message=f"DNS record updated: {db_record.record_name}",
        user_id=current_user.id,
        dns_record_id=db_record.id,
        ip_address=content if record_type in ("A", "AAAA") else None
    )
    
    return db_record


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dns_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    """
    Delete a DNS record.
    
    Args:
        record_id: DNS record ID
        db: Database session
        current_user: Current authenticated user
        
    Raises:
        HTTPException: If record not found or deletion fails
    """
    db_record = db.query(DNSRecord).filter(
        DNSRecord.id == record_id, DNSRecord.user_id == current_user.id
    ).first()
    
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DNS record not found"
        )
    
    # Initialize Cloudflare service
    cf_service = CloudflareService(
        api_key=current_user.cloudflare_api_key,
        email=current_user.cloudflare_email
    )
    
    # Delete record from Cloudflare
    success = await cf_service.delete_dns_record(
        zone_id=db_record.zone_id,
        record_id=db_record.record_id
    )
    
    if not success:
        # Log error
        LogService.create_log(
            db=db,
            level=LogLevel.ERROR,
            message=f"Failed to delete DNS record: {db_record.record_name}",
            user_id=current_user.id,
            dns_record_id=db_record.id
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete DNS record from Cloudflare"
        )
    
    # Log record details before deletion
    record_name = db_record.record_name
    record_id_val = db_record.id
    
    # Delete record from database
    db.delete(db_record)
    db.commit()
    
    # Log success
    LogService.create_log(
        db=db,
        level=LogLevel.INFO,
        message=f"DNS record deleted: {record_name}",
        user_id=current_user.id
    )


@router.post("/{record_id}/update-ip", response_model=DNSRecordSchema)
async def update_dns_record_ip(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Manually update the IP address for a DNS record.
    
    Args:
        record_id: DNS record ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Updated DNS record
        
    Raises:
        HTTPException: If record not found or update fails
    """
    db_record = db.query(DNSRecord).filter(
        DNSRecord.id == record_id, DNSRecord.user_id == current_user.id
    ).first()
    
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DNS record not found"
        )
    
    # Only allow updating IP for A or AAAA records
    if db_record.record_type not in ("A", "AAAA"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="IP updating is only available for A or AAAA records"
        )
    
    # Get current IP
    current_ip = await IPService.get_current_ip()
    if not current_ip:
        # Log error
        LogService.create_log(
            db=db,
            level=LogLevel.ERROR,
            message="Failed to get current IP address",
            user_id=current_user.id,
            dns_record_id=db_record.id
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get current IP address"
        )
    
    # Check if IP has changed
    if not IPService.is_ip_changed(current_ip, db_record.last_updated_ip):
        # Even if IP hasn't changed, log the verification and update timestamp
        old_ip = db_record.content
        
        # Update timestamp even if IP hasn't changed
        db_record.updated_at = func.now()
        db_record.last_updated_ip = current_ip
        
        db.commit()
        db.refresh(db_record)
        
        # Log the verification attempt
        LogService.create_log(
            db=db,
            level=LogLevel.INFO,
            message=f"IP verification for {db_record.record_name} (unchanged: {current_ip})",
            user_id=current_user.id,
            dns_record_id=db_record.id,
            ip_address=current_ip
        )
        
        return db_record
    
    # Initialize Cloudflare service
    cf_service = CloudflareService(
        api_key=current_user.cloudflare_api_key,
        email=current_user.cloudflare_email
    )
    
    # Update record in Cloudflare
    cf_record = await cf_service.update_dns_record(
        zone_id=db_record.zone_id,
        record_id=db_record.record_id,
        type=db_record.record_type,
        name=db_record.record_name,
        content=current_ip,
        ttl=db_record.ttl,
        proxied=db_record.proxied
    )
    
    if not cf_record:
        # Log error
        LogService.create_log(
            db=db,
            level=LogLevel.ERROR,
            message=f"Failed to update IP for DNS record: {db_record.record_name}",
            user_id=current_user.id,
            dns_record_id=db_record.id,
            ip_address=current_ip
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update DNS record in Cloudflare"
        )
    
    # Update record in database
    old_ip = db_record.content
    db_record.content = current_ip
    db_record.last_updated_ip = current_ip
    
    db.commit()
    db.refresh(db_record)
    
    # Log success
    LogService.create_log(
        db=db,
        level=LogLevel.SUCCESS,
        message=f"IP updated for {db_record.record_name} ({old_ip} -> {current_ip})",
        user_id=current_user.id,
        dns_record_id=db_record.id,
        ip_address=current_ip
    )
    
    return db_record


@router.get("/records/{zone_id}", response_model=List[dict])
async def get_cloudflare_dns_records(
    zone_id: str,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get all DNS records for a Cloudflare zone.
    
    Args:
        zone_id: Cloudflare zone ID
        current_user: Current authenticated user
        
    Returns:
        List of Cloudflare DNS records
        
    Raises:
        HTTPException: If Cloudflare API request fails
    """
    # Initialize Cloudflare service
    cf_service = CloudflareService(
        api_key=current_user.cloudflare_api_key,
        email=current_user.cloudflare_email
    )
    
    # Get DNS records from Cloudflare
    records = await cf_service.get_dns_records(zone_id=zone_id)
    
    if records is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get DNS records from Cloudflare"
        )
    
    return records


@router.post("/update-all-ips", response_model=dict)
async def update_all_dns_record_ips(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update IP for all A and AAAA DNS records.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Dictionary with count of updated records
        
    Raises:
        HTTPException: If update fails
    """
    # Get all A and AAAA records for the user
    records = db.query(DNSRecord).filter(
        DNSRecord.user_id == current_user.id,
        DNSRecord.record_type.in_(["A", "AAAA"])
    ).all()
    
    if not records:
        # Log even if no records found
        LogService.create_log(
            db=db,
            level=LogLevel.INFO,
            message="Update all IPs attempted but no A/AAAA records found",
            user_id=current_user.id
        )
        return {"updated": 0, "message": "No DNS records found to update"}
    
    # Get current IP
    current_ip = await IPService.get_current_ip()
    if not current_ip:
        LogService.create_log(
            db=db,
            level=LogLevel.ERROR,
            message="Failed to get current IP address for bulk update",
            user_id=current_user.id
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get current IP address"
        )
    
    # Initialize Cloudflare service
    cf_service = CloudflareService(
        api_key=current_user.cloudflare_api_key,
        email=current_user.cloudflare_email
    )
    
    updated_count = 0
    checked_count = 0
    
    for record in records:
        checked_count += 1
        ip_changed = IPService.is_ip_changed(current_ip, record.content)
        
        try:
            # Always update the record in Cloudflare, regardless of whether IP has changed
            cf_record = await cf_service.update_dns_record(
                zone_id=record.zone_id,
                record_id=record.record_id,
                type=record.record_type,
                name=record.record_name,
                content=current_ip,
                ttl=record.ttl,
                proxied=record.proxied
            )
            
            if not cf_record:
                # Log error but continue with other records
                LogService.create_log(
                    db=db,
                    level=LogLevel.ERROR,
                    message=f"Failed to update IP for DNS record: {record.record_name}",
                    user_id=current_user.id,
                    dns_record_id=record.id,
                    ip_address=current_ip
                )
                continue
                
            # Update record in database
            old_ip = record.content
            if ip_changed:
                record.content = current_ip
                updated_count += 1
            
            # Always update the timestamp and last_updated_ip, even if IP didn't change
            record.last_updated_ip = current_ip
            record.updated_at = func.now()
            
            # Log success based on whether IP changed
            if ip_changed:
                LogService.create_log(
                    db=db,
                    level=LogLevel.SUCCESS,
                    message=f"IP updated for {record.record_name} ({old_ip} -> {current_ip})",
                    user_id=current_user.id,
                    dns_record_id=record.id,
                    ip_address=current_ip
                )
            else:
                LogService.create_log(
                    db=db,
                    level=LogLevel.INFO,
                    message=f"IP verification for {record.record_name} (unchanged: {current_ip})",
                    user_id=current_user.id,
                    dns_record_id=record.id,
                    ip_address=current_ip
                )
                
        except Exception as e:
            # Log error but continue with other records
            LogService.create_log(
                db=db,
                level=LogLevel.ERROR,
                message=f"Error updating {record.record_name}: {str(e)}",
                user_id=current_user.id,
                dns_record_id=record.id
            )
    
    # Commit all changes at once
    db.commit()
    
    # Log summary
    LogService.create_log(
        db=db,
        level=LogLevel.INFO,
        message=f"Bulk IP update completed: {updated_count} updated, {checked_count} checked",
        user_id=current_user.id,
        ip_address=current_ip
    )
    
    return {
        "checked": checked_count,
        "updated": updated_count,
        "current_ip": current_ip,
        "message": f"Checked {checked_count} DNS records, updated {updated_count}"
    } 