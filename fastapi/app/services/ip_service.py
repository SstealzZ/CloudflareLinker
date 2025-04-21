import httpx
import logging
import socket
from typing import Optional, List

logger = logging.getLogger(__name__)

class IPService:
    """
    Service for retrieving and managing IP addresses.
    """
    
    # IP services in order of preference
    IP_SERVICES = [
        "https://api.ipify.org",
        "https://ifconfig.me/ip",
        "https://icanhazip.com",
        "https://ip.42.pl/raw"
    ]
    
    @staticmethod
    async def get_current_ip() -> Optional[str]:
        """
        Get the current public IP address by querying multiple services.
        
        Returns:
            The current public IP address or None if retrieval fails
        """
        for service_url in IPService.IP_SERVICES:
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(service_url)
                    if response.status_code == 200:
                        ip = response.text.strip()
                        logger.info(f"Retrieved current IP: {ip} from {service_url}")
                        return ip
            except Exception as e:
                logger.warning(f"Failed to get IP from {service_url}: {e}")
        
        logger.error("Failed to retrieve current IP from all services")
        return None
    
    @staticmethod
    def is_valid_ip(ip: str) -> bool:
        """
        Check if a string is a valid IP address.
        
        Args:
            ip: String to check
            
        Returns:
            True if valid IP address, False otherwise
        """
        try:
            # Try parsing as IPv4
            socket.inet_pton(socket.AF_INET, ip)
            return True
        except socket.error:
            try:
                # Try parsing as IPv6
                socket.inet_pton(socket.AF_INET6, ip)
                return True
            except socket.error:
                return False
    
    @staticmethod
    def is_ip_changed(new_ip: str, old_ip: str) -> bool:
        """
        Check if IP address has changed.
        
        Args:
            new_ip: New IP address
            old_ip: Previous IP address
            
        Returns:
            True if IP has changed or old_ip is None, False otherwise
        """
        if not old_ip:
            return True
            
        return new_ip != old_ip 