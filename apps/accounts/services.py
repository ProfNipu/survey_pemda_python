"""
ESIMPEG API Service for authentication and data fetching
"""
import requests
import logging
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class EsimpegAPIService:
    """
    Service class untuk consume ESIMPEG API v5.0
    Handles authentication, token management, and data fetching
    """
    
    def __init__(self):
        self.base_url = getattr(settings, 'ESIMPEG_API_URL', 'http://localhost:8000')
        self.timeout = getattr(settings, 'ESIMPEG_API_TIMEOUT', 10)
        # Host header untuk fix Django URL reverse issue saat call via Docker network
        self.host_header = getattr(settings, 'ESIMPEG_API_HOST_HEADER', None)
    
    def login(self, username, password):
        """
        Login to ESIMPEG API v5.0
        
        Args:
            username (str): Username (email/NIP)
            password (str): Password
        
        Returns:
            dict: Response data with access_token, refresh_token, user info
            None: If login failed
        
        Example response:
        {
            "status": "success",
            "message": "Login successful",
            "data": {
                "access_token": "eyJhbGc...",
                "refresh_token": "eyJhbGc...",
                "token_type": "Bearer",
                "expires_in": 86400,
                "user": {
                    "user_id": 1,
                    "username": "prakom@admin.com",
                    "name": "Prakom Admin",
                    "email": "prakom@admin.com",
                    "id_pegawai": 123,
                    "user_id_opd": 456,
                    "is_active": true
                }
            },
            "version": "5.0"
        }
        """
        url = f"{self.base_url}/apisimpeg/5.0/auth/login"
        
        headers = {'Content-Type': 'application/json'}
        if self.host_header:
            headers['Host'] = self.host_header
        
        try:
            response = requests.post(
                url,
                json={
                    'username': username,
                    'password': password
                },
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'success':
                    logger.info(f"ESIMPEG API login successful for user: {username}")
                    return data.get('data')
                else:
                    logger.warning(f"ESIMPEG API login failed: {data.get('message')}")
                    return None
            else:
                logger.error(f"ESIMPEG API login failed with status {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error(f"ESIMPEG API login timeout for user: {username}")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"ESIMPEG API connection error (API might be down)")
            return None
        except Exception as e:
            logger.error(f"ESIMPEG API login error: {str(e)}")
            return None
    
    def verify_token(self, token):
        """
        Verify JWT token validity
        
        Args:
            token (str): JWT access token
        
        Returns:
            bool: True if valid, False otherwise
        """
        url = f"{self.base_url}/apisimpeg/5.0/auth/verify"
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        if self.host_header:
            headers['Host'] = self.host_header
        
        try:
            response = requests.post(
                url,
                headers=headers,
                timeout=self.timeout
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"ESIMPEG API verify token error: {str(e)}")
            return False
    
    def refresh_token(self, refresh_token):
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token (str): JWT refresh token
        
        Returns:
            dict: New access_token and refresh_token
            None: If refresh failed
        """
        url = f"{self.base_url}/apisimpeg/5.0/auth/refresh"
        
        try:
            response = requests.post(
                url,
                json={'refresh_token': refresh_token},
                headers={'Content-Type': 'application/json'},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    return data.get('data')
            
            return None
            
        except Exception as e:
            logger.error(f"ESIMPEG API refresh token error: {str(e)}")
            return None
    
    def get_pegawai_list(self, token, page=1, per_page=50, search=None, id_opd=None):
        """
        Get pegawai list from ESIMPEG API v5.0
        
        Args:
            token (str): JWT access token
            page (int): Page number
            per_page (int): Items per page (10/25/50/100/200)
            search (str): Search query (nama or NIP)
            id_opd (int): Filter by OPD
        
        Returns:
            dict: Response data with items and pagination
            None: If request failed
        """
        url = f"{self.base_url}/apisimpeg/5.0/pegawai/data/list"
        
        params = {
            'page': page,
            'per_page': per_page
        }
        
        if search:
            params['search'] = search
        if id_opd:
            params['id_opd'] = id_opd
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        if self.host_header:
            headers['Host'] = self.host_header
        
        try:
            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                # Support both new format (status: success) and old Laravel format (data with items)
                if data.get('status') == 'success':
                    return data.get('data')
                elif 'data' in data and isinstance(data.get('data'), dict) and 'items' in data['data']:
                    # Old Laravel format: {data: {items: [...], pagination: {...}}}
                    return data['data']
            
            return None
            
        except Exception as e:
            logger.error(f"ESIMPEG API get pegawai list error: {str(e)}")
            return None
    
    def get_pegawai_by_nip(self, token, nip):
        """
        Get pegawai detail by NIP from ESIMPEG API v5.0
        
        Args:
            token (str): JWT access token
            nip (str): NIP pegawai (18 digit)
        
        Returns:
            dict: Pegawai data with riwayat and SIASN
            None: If request failed
        """
        url = f"{self.base_url}/apisimpeg/5.0/pegawai/data/nip/{nip}"
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        if self.host_header:
            headers['Host'] = self.host_header
        
        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    return data.get('data')
            
            return None
            
        except Exception as e:
            logger.error(f"ESIMPEG API get pegawai by NIP error: {str(e)}")
            return None
    
    def change_password(self, token, old_password, new_password):
        """
        Change password via ESIMPEG API v5.0
        
        Args:
            token (str): JWT access token
            old_password (str): Old password
            new_password (str): New password
        
        Returns:
            dict: Response data
            None: If request failed
        """
        url = f"{self.base_url}/apisimpeg/5.0/auth/change-password"
        
        try:
            response = requests.post(
                url,
                json={
                    'old_password': old_password,
                    'new_password': new_password,
                    'confirm_password': new_password
                },
                headers={
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    logger.info("ESIMPEG API change password successful")
                    return data
            
            return None
            
        except Exception as e:
            logger.error(f"ESIMPEG API change password error: {str(e)}")
            return None
    
    def is_api_available(self):
        """
        Check if ESIMPEG API is available
        
        Returns:
            bool: True if available, False otherwise
        """
        # Check cache first (avoid repeated requests)
        cache_key = 'esimpeg_api_available'
        cached = cache.get(cache_key)
        
        if cached is not None:
            return cached
        
        url = f"{self.base_url}/health"
        
        try:
            response = requests.get(url, timeout=3)
            available = response.status_code == 200
            
            # Cache result for 1 minute
            cache.set(cache_key, available, 60)
            
            return available
            
        except Exception:
            # Cache unavailable for 1 minute
            cache.set(cache_key, False, 60)
            return False
