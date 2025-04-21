import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, List

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from sqlalchemy.orm import Session
from ..core.database import SessionLocal
from ..models.dns_record import DNSRecord
from ..models.user import User
from ..models.log import LogLevel
from .cloudflare import CloudflareService
from .ip_service import IPService
from .log_service import LogService
from ..repositories.dns_record_repo import DnsRecordRepo


logger = logging.getLogger(__name__)


class DnsUpdateScheduler:
    """
    Singleton scheduler for performing automated DNS updates.
    
    This class manages scheduled tasks for checking and updating DNS records 
    with auto_update enabled. It runs as a background service to ensure 
    DNS records are kept in sync with the current public IP address.
    """
    
    _instance = None
    
    def __new__(cls):
        """
        Create a new instance of DnsUpdateScheduler or return the existing one.
        
        Returns:
            The singleton instance of DnsUpdateScheduler
        """
        if cls._instance is None:
            cls._instance = super(DnsUpdateScheduler, cls).__new__(cls)
            cls._instance.scheduler = AsyncIOScheduler()
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """
        Initialize the scheduler instance if it hasn't been initialized yet.
        
        This method is called after __new__ and sets up the scheduler instance 
        with proper configuration.
        """
        if not hasattr(self, 'scheduler'):
            self.scheduler = AsyncIOScheduler()
            self._initialized = False
    
    @classmethod
    def initialize(cls):
        """
        Initialize the scheduler singleton instance and start it.
        
        This is a convenience method for explicitly initializing the scheduler
        from external code. It creates the instance if needed and starts the
        scheduler.
        
        Returns:
            The initialized scheduler instance
        """
        instance = cls()
        instance.start()
        return instance
    
    def start(self):
        """
        Start the scheduler if it's not already running.
        
        This method initializes the scheduler and adds jobs for:
        - Updating DNS records every 10 minutes
        - Checking all DNS records daily
        """
        if self._initialized:
            logger.info("Scheduler already initialized")
            return
            
        if not self.scheduler.running:
            logger.info("Starting DNS update scheduler")
            
            # Add job to update DNS records every 10 minutes
            self.scheduler.add_job(
                self.update_dns_records,
                IntervalTrigger(minutes=10),
                id="update_dns_records_job",
                replace_existing=True
            )
            
            # Add job to check all DNS records daily at 3 AM
            self.scheduler.add_job(
                self.check_all_dns_records,
                CronTrigger(hour=3, minute=0),
                id="check_all_dns_records_job",
                replace_existing=True
            )
            
            self.scheduler.start()
            self._initialized = True
            logger.info("DNS update scheduler started successfully")
        else:
            logger.info("DNS update scheduler already running")
    
    def stop(self):
        """
        Stop the scheduler if it's running.
        """
        if self.scheduler.running:
            logger.info("Stopping DNS update scheduler")
            self.scheduler.shutdown()
            self._initialized = False
            logger.info("DNS update scheduler stopped")
    
    async def update_dns_records(self):
        """
        Update all DNS records with auto_update enabled.
        
        This method checks the current IP and updates records if the IP has changed.
        """
        logger.info("Running scheduled DNS record update for auto-updated records")
        
        db = SessionLocal()
        try:
            # Get current IP
            current_ip = await IPService.get_current_ip()
            if not current_ip:
                logger.error("Failed to retrieve current IP, aborting DNS update")
                return
                
            logger.info(f"Current IP for DNS updates: {current_ip}")
            
            # Get all DNS records with auto_update enabled
            records = db.query(DNSRecord).filter(
                DNSRecord.auto_update == True,
                DNSRecord.record_type.in_(["A", "AAAA"])
            ).all()
            
            if not records:
                logger.info("No DNS records with auto_update enabled found")
                return
                
            logger.info(f"Found {len(records)} records with auto_update enabled")
            
            # Update each record if needed
            updated_count = 0
            for record in records:
                if IPService.is_ip_changed(current_ip, record.content):
                    await self._update_record_ip(db, record, current_ip)
                    updated_count += 1
                else:
                    logger.debug(f"No IP change needed for {record.record_name}")
                    
            logger.info(f"Scheduled DNS update completed. Updated {updated_count} records.")
            
        except Exception as e:
            logger.error(f"Error in scheduled DNS update: {e}", exc_info=True)
        finally:
            db.close()
    
    async def check_all_dns_records(self):
        """
        Perform a daily check of all DNS records to ensure they have the correct IP.
        
        This serves as a fallback mechanism to ensure all records are properly maintained.
        """
        logger.info("Running daily check of all DNS records")
        
        db = SessionLocal()
        try:
            # Get current IP
            current_ip = await IPService.get_current_ip()
            if not current_ip:
                logger.error("Failed to retrieve current IP for daily check")
                return
                
            # Get all DNS records
            records = db.query(DNSRecord).filter(
                DNSRecord.record_type.in_(["A", "AAAA"])
            ).all()
            
            logger.info(f"Checking {len(records)} DNS records")
            
            # Check each auto-update record to ensure it has the correct IP
            updated_count = 0
            for record in records:
                if record.auto_update and IPService.is_ip_changed(current_ip, record.content):
                    logger.info(f"Record {record.record_name} has outdated IP, updating")
                    await self._update_record_ip(db, record, current_ip)
                    updated_count += 1
            
            logger.info(f"Daily DNS record check completed. Updated {updated_count} records.")
            
        except Exception as e:
            logger.error(f"Error in daily DNS check: {e}", exc_info=True)
        finally:
            db.close()
    
    async def _update_record_ip(self, db: Session, record: DNSRecord, new_ip: str):
        """
        Update a DNS record's IP address in database and Cloudflare.
        
        Args:
            db: Database session
            record: The DNS record to update
            new_ip: The new IP address to set
        """
        logger.info(f"Updating DNS record {record.record_name} IP from {record.content} to {new_ip}")
        
        try:
            # Get user for API credentials
            user = db.query(User).filter(User.id == record.user_id).first()
            if not user:
                logger.error(f"User not found for record ID {record.id}")
                return
            
            # Initialize Cloudflare service
            cf_service = CloudflareService(
                user.cloudflare_api_key, 
                user.cloudflare_email,
                is_token=user.is_token
            )
            
            # Update record in Cloudflare
            old_ip = record.content
            success = await cf_service.update_dns_record(
                zone_id=record.zone_id,
                record_id=record.record_id,
                type=record.record_type,
                name=record.record_name,
                content=new_ip,
                ttl=record.ttl,
                proxied=record.proxied
            )
            
            if not success:
                logger.error(f"Failed to update DNS record {record.record_name} in Cloudflare")
                
                # Log error
                LogService.create_log(
                    db=db,
                    level=LogLevel.ERROR,
                    message=f"Échec de mise à jour automatique d'IP pour {record.record_name}",
                    user_id=record.user_id,
                    record_id=record.id,
                    ip_address=new_ip
                )
                return
            
            # Update record in database
            record.content = new_ip
            record.last_updated = datetime.utcnow()
            db.commit()
            
            # Log success
            LogService.create_log(
                db=db,
                level=LogLevel.INFO,
                message=f"Mise à jour automatique d'IP pour {record.record_name} de {old_ip} à {new_ip}",
                user_id=record.user_id,
                record_id=record.id,
                ip_address=new_ip
            )
            
            logger.info(f"Successfully updated DNS record {record.record_name}")
            
        except Exception as e:
            logger.error(f"Error updating DNS record {record.record_name}: {e}", exc_info=True)
            
            # Log error
            LogService.create_log(
                db=db,
                level=LogLevel.ERROR,
                message=f"Erreur lors de la mise à jour d'IP pour {record.record_name}: {str(e)}",
                user_id=record.user_id,
                record_id=record.id,
                ip_address=new_ip
            )


# Singleton instance
dns_scheduler = DnsUpdateScheduler() 