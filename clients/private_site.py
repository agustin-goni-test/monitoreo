import requests
from typing import Optional
import json
from dotenv import load_dotenv
import os

load_dotenv()

class PrivateSiteClient:
    def __init__(self, base_url: str):
        """
        Initialize with just the base URL
        Token will be set separately via set_token()
        """
        self.base_url = base_url.rstrip('/')
        self._token: Optional[str] = None
        self._session = requests.Session()

    def set_token(self, token: str):
        """Set/update the authentication token"""
        self._token = token
        self._session.headers.update({
            'Authorization': f'Bearer {token}'
        })

    def get_last_transaction(self, commerce_rut: str) -> dict:
        """
        Calls the private endpoint to get last transaction timestamp
        Requires token to be set first via set_token()
        
        Args:
            commerce_rut: The commerce RUT identifier
            
        Returns:
            Dictionary containing the API response
            
        Raises:
            RuntimeError: If no token set or API call fails
        """
        if not self._token:
            raise RuntimeError("Authentication token not set - call set_token() first")
        
        last_trx = os.getenv("LAST_TRX_ENDPOINT")
        endpoint = f"{self.base_url}{last_trx}"  # Adjust endpoint as needed
        payload = {
            "commerce_rut": commerce_rut,
            "rol_user": "rol_super_usuario",
            "atc_filter": "TODOS"
        }
        
        try:
            response = self._session.post(
                endpoint,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Validate response structure
            if data.get('code') != 1:
                raise RuntimeError(f"API error: {data.get('message', 'Unknown error')}")
                
            return data
            
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"API request failed: {str(e)}")
        except json.JSONDecodeError:
            raise RuntimeError("Invalid JSON response from server")

# Singleton implementation
_private_site_instance: Optional[PrivateSiteClient] = None

def get_private_site_client() -> PrivateSiteClient:
    global _private_site_instance
    
    if _private_site_instance is None:
        
        load_dotenv()
        base_url = os.getenv("PRIVATE_SITE_URL")
        if not base_url:
            raise RuntimeError("PRIVATE_SITE_URL environment variable not set")
            
        _private_site_instance = PrivateSiteClient(base_url)
    
    return _private_site_instance