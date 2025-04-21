import httpx
import logging
from typing import Dict, List, Optional, Any
import json
from ..core.security import decrypt_api_key

logger = logging.getLogger(__name__)

class CloudflareService:
    """
    Service for interacting with the Cloudflare API.
    """
    API_BASE_URL = "https://api.cloudflare.com/client/v4"
    
    def __init__(self, api_key: str, email: Optional[str] = None, is_encrypted: bool = True, is_token: bool = True):
        """
        Initialize the Cloudflare service with token authentication.
        
        Args:
            api_key: Cloudflare API token
            email: Optional Cloudflare account email
            is_encrypted: Whether the API token is encrypted
            is_token: Always True, only token authentication is supported
        """
        if not is_token:
            raise ValueError("Seule l'authentification par jeton API est supportée")
            
        try:
            # Essayer de déchiffrer le jeton
            self.api_key = decrypt_api_key(api_key) if is_encrypted else api_key
        except Exception as e:
            # En cas d'échec, utiliser le jeton tel quel et logger l'erreur
            logger.warning(f"Failed to decrypt API token, using as-is: {str(e)}")
            self.api_key = api_key
        
        # Utilisation de l'authentification par token
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def get_zones(self) -> List[Dict[str, Any]]:
        """
        Get all zones (domains) for the Cloudflare account.
        
        Returns:
            List of zone dictionaries
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.API_BASE_URL}/zones",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data["success"]:
                        return data["result"]
                    logger.error(f"Cloudflare API error: {data.get('errors', 'Unknown error')}")
                    return []
                else:
                    logger.error(f"Cloudflare API responded with status {response.status_code}: {response.text}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching Cloudflare zones: {str(e)}")
            return []
    
    async def get_dns_records(self, zone_id: str) -> List[Dict[str, Any]]:
        """
        Get all DNS records for a zone.
        
        Args:
            zone_id: Cloudflare zone ID
            
        Returns:
            List of DNS record dictionaries
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.API_BASE_URL}/zones/{zone_id}/dns_records",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data["success"]:
                        return data["result"]
                    logger.error(f"Cloudflare API error: {data.get('errors', 'Unknown error')}")
                    return []
                else:
                    logger.error(f"Cloudflare API responded with status {response.status_code}: {response.text}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching DNS records: {str(e)}")
            return []
    
    async def create_dns_record(
        self,
        zone_id: str,
        type: str,
        name: str,
        content: str,
        ttl: int = 1,
        proxied: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new DNS record.
        
        Args:
            zone_id: Cloudflare zone ID
            type: Record type (A, AAAA, CNAME, etc.)
            name: Record name (subdomain)
            content: Record content (IP address or domain)
            ttl: Time to live (1 = auto)
            proxied: Whether the record is proxied through Cloudflare
            
        Returns:
            Created DNS record or None if failed
        """
        payload = {
            "type": type,
            "name": name,
            "content": content,
            "ttl": ttl,
            "proxied": proxied
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.API_BASE_URL}/zones/{zone_id}/dns_records",
                    headers=self.headers,
                    json=payload
                )
                
                if response.status_code in (200, 201):
                    data = response.json()
                    if data["success"]:
                        return data["result"]
                    logger.error(f"Cloudflare API error: {data.get('errors', 'Unknown error')}")
                    return None
                else:
                    logger.error(f"Cloudflare API responded with status {response.status_code}: {response.text}")
                    return None
        except Exception as e:
            logger.error(f"Error creating DNS record: {str(e)}")
            return None
    
    async def update_dns_record(
        self,
        zone_id: str,
        record_id: str,
        type: str,
        name: str,
        content: str,
        ttl: int = 1,
        proxied: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Update an existing DNS record.
        
        Args:
            zone_id: Cloudflare zone ID
            record_id: DNS record ID
            type: Record type (A, AAAA, CNAME, etc.)
            name: Record name (subdomain)
            content: Record content (IP address or domain)
            ttl: Time to live (1 = auto)
            proxied: Whether the record is proxied through Cloudflare
            
        Returns:
            Updated DNS record or None if failed
        """
        payload = {
            "type": type,
            "name": name,
            "content": content,
            "ttl": ttl,
            "proxied": proxied
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"{self.API_BASE_URL}/zones/{zone_id}/dns_records/{record_id}",
                    headers=self.headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data["success"]:
                        return data["result"]
                    logger.error(f"Cloudflare API error: {data.get('errors', 'Unknown error')}")
                    return None
                else:
                    logger.error(f"Cloudflare API responded with status {response.status_code}: {response.text}")
                    return None
        except Exception as e:
            logger.error(f"Error updating DNS record: {str(e)}")
            return None
            
    async def delete_dns_record(
        self,
        zone_id: str,
        record_id: str
    ) -> bool:
        """
        Delete a DNS record.
        
        Args:
            zone_id: Cloudflare zone ID
            record_id: DNS record ID
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.API_BASE_URL}/zones/{zone_id}/dns_records/{record_id}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data["success"]
                else:
                    logger.error(f"Cloudflare API responded with status {response.status_code}: {response.text}")
                    return False
        except Exception as e:
            logger.error(f"Error deleting DNS record: {str(e)}")
            return False 