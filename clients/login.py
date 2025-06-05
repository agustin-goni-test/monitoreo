from dotenv import load_dotenv
import os
from typing import Optional
import json
import requests

# Initialize environment variables ONCE when module loads
load_dotenv()  # <-- Critical initialization at module level

class LoginClient:
    def __init__(self, base_url: str, user: str, password: str):
        if not all([base_url, user, password]):
            raise ValueError("All credentials must be provided")
        self.base_url = base_url
        self.user = user
        self.password = password
        self._token = None
        self._token_expiry = None

    def authenticate(self) -> str:
        """
        Authenticates with the login service and returns the token.
        Caches the token for subsequent calls until expiry.
        
        Returns:
            str: The authentication token
            
        Raises:
            RuntimeError: If authentication fails
        """
        if self._token and not self._is_token_expired():
            return self._token
            
        auth_url = f"{self.base_url}/login"  # Adjust endpoint as needed
        payload = {
            "user": self.user,
            "pass": self.password
        }
        
        try:
            response = requests.post(
                auth_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            if data.get('code') != 1:  # Assuming 1 means success
                raise RuntimeError(f"Authentication failed: {data.get('message', 'Unknown error')}")
            
            self._token = data['data']['token']
            print (self._token)
            return self._token
            
        except requests.exceptions.RequestException as e:
            # Specific error handling
            if "500" in str(e):
                raise RuntimeError("Authentication server is currently unavailable (500 error)")
            elif "404" in str(e):
                raise RuntimeError("Authentication endpoint not found (404)")
            else:
                raise RuntimeError(f"Authentication failed: {str(e)}")
        except json.JSONDecodeError:
            raise RuntimeError("Invalid JSON response from server")
        except KeyError:
            raise RuntimeError("Malformed authentication response")
        

    def _is_token_expired(self) -> bool:
        """Simple token expiry check (would need proper JWT decoding in production)"""
        if self._token is not None:
            auth_url = f"{self.base_url}/check"

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self._token}'
            }

            try:
                response = requests.post(
                    auth_url,
                    json={},
                    headers=headers,
                    timeout=10
                )

                response.raise_for_status()

                data = response.json()
                code = data.get('code')
                message = data.get('message')

                if code == 1 and message == "Esta autorizado":
                    return False  # Token is valid
                else:
                    return True

            except requests.exceptions.RequestException as e:
                # Specific error handling
                if "500" in str(e):
                    raise RuntimeError("Authentication server is currently unavailable (500 error)")
                elif "404" in str(e):
                    raise RuntimeError("Authentication endpoint not found (404)")
                else:
                    raise RuntimeError(f"Authentication failed: {str(e)}")
            except json.JSONDecodeError:
                raise RuntimeError("Invalid JSON response from server")
            except KeyError:
                raise RuntimeError("Malformed authentication response")

        else:
            return True
        
        


_login_client_instance: Optional[LoginClient] = None

def get_login_client() -> LoginClient:
    global _login_client_instance
    
    if _login_client_instance is None:
        # Environment variables are already loaded at module level
        url = os.getenv("LOGIN_URL")
        user = os.getenv("LOGIN_USER")
        password = os.getenv("LOGIN_PASSWORD")
        
        if None in (url, user, password):
            missing = []
            if url is None: missing.append("LOGIN_URL")
            if user is None: missing.append("LOGIN_USER")
            if password is None: missing.append("LOGIN_PASSWORD")
            raise RuntimeError(
                f"Missing environment variables: {', '.join(missing)}\n"
                "Please check your .env file or environment configuration."
            )
        
        _login_client_instance = LoginClient(
            base_url=url,
            user=user,
            password=password
        )
    
    return _login_client_instance
