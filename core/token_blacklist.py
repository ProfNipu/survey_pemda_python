"""
JWT Token Blacklist using Redis
Fast, scalable, auto-expiring
"""
from django.core.cache import cache
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TokenBlacklist:
    """
    Manage JWT token blacklist using Redis
    Tokens are stored with their expiration time
    Redis automatically removes expired entries
    """
    
    BLACKLIST_PREFIX = "jwt_blacklist:"
    
    @classmethod
    def add(cls, token_string, expires_at=None):
        """
        Add token to blacklist
        
        Args:
            token_string: JWT token string
            expires_at: Token expiration timestamp (optional)
        
        Returns:
            bool: True if added successfully
        """
        try:
            from rest_framework_simplejwt.tokens import AccessToken
            
            # Decode token to get expiration and JTI
            token = AccessToken(token_string)
            jti = token.get('jti')  # JWT ID (unique identifier)
            exp = token.get('exp')  # Expiration timestamp
            
            if not jti:
                logger.error("Token doesn't have JTI claim")
                return False
            
            # Calculate TTL (time to live in seconds)
            now = datetime.now().timestamp()
            ttl = int(exp - now) if exp > now else 3600  # Default 1 hour if already expired
            
            # Store in Redis with auto-expiration
            cache_key = f"{cls.BLACKLIST_PREFIX}{jti}"
            cache.set(cache_key, {
                'blacklisted_at': datetime.now().isoformat(),
                'user_id': token.get('user_id'),
                'reason': 'revoked'
            }, ttl)
            
            logger.info(f"Token {jti[:10]}... added to blacklist (TTL: {ttl}s)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add token to blacklist: {str(e)}")
            return False
    
    @classmethod
    def is_blacklisted(cls, token_string):
        """
        Check if token is in blacklist
        
        Args:
            token_string: JWT token string
        
        Returns:
            bool: True if blacklisted, False otherwise
        """
        try:
            from rest_framework_simplejwt.tokens import AccessToken
            
            token = AccessToken(token_string)
            jti = token.get('jti')
            
            if not jti:
                return False
            
            cache_key = f"{cls.BLACKLIST_PREFIX}{jti}"
            return cache.get(cache_key) is not None
            
        except Exception as e:
            logger.error(f"Failed to check blacklist: {str(e)}")
            return False
    
    @classmethod
    def remove(cls, token_string):
        """
        Remove token from blacklist (un-revoke)
        
        Args:
            token_string: JWT token string
        
        Returns:
            bool: True if removed successfully
        """
        try:
            from rest_framework_simplejwt.tokens import AccessToken
            
            token = AccessToken(token_string)
            jti = token.get('jti')
            
            if not jti:
                return False
            
            cache_key = f"{cls.BLACKLIST_PREFIX}{jti}"
            cache.delete(cache_key)
            
            logger.info(f"Token {jti[:10]}... removed from blacklist")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove token from blacklist: {str(e)}")
            return False
    
    @classmethod
    def blacklist_all_user_tokens(cls, user_id, reason="user_action"):
        """
        Blacklist all tokens for a specific user
        Useful for: password change, account suspension
        
        Args:
            user_id: User ID
            reason: Reason for blacklisting (default: "user_action")
        
        Note: This requires storing active tokens somewhere
              For now, we'll use a simpler approach with user-level blacklist
        """
        try:
            # Store user-level blacklist with timestamp
            cache_key = f"user_blacklist:{user_id}"
            cache.set(cache_key, {
                'blacklisted_at': datetime.now().timestamp(),
                'reason': reason
            }, 86400 * 365)  # 1 year (covers max token lifetime)
            
            logger.info(f"All tokens for user {user_id} blacklisted. Reason: {reason}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to blacklist user tokens: {str(e)}")
            return False
    
    @classmethod
    def is_user_blacklisted(cls, user_id, token_issued_at):
        """
        Check if user is blacklisted (for all tokens)
        
        Args:
            user_id: User ID
            token_issued_at: Token issued timestamp
        
        Returns:
            bool: True if user blacklisted and token issued before blacklist
        """
        try:
            cache_key = f"user_blacklist:{user_id}"
            blacklist_data = cache.get(cache_key)
            
            if not blacklist_data:
                return False
            
            # Token is invalid if issued before user blacklist
            blacklisted_at = blacklist_data.get('blacklisted_at')
            return token_issued_at < blacklisted_at
            
        except Exception as e:
            logger.error(f"Failed to check user blacklist: {str(e)}")
            return False
    
    @classmethod
    def clear_user_blacklist(cls, user_id):
        """
        Remove user from blacklist (allow all tokens again)
        
        Args:
            user_id: User ID
        
        Returns:
            bool: True if cleared successfully
        """
        try:
            cache_key = f"user_blacklist:{user_id}"
            cache.delete(cache_key)
            
            logger.info(f"User {user_id} removed from blacklist")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear user blacklist: {str(e)}")
            return False
    
    @classmethod
    def get_stats(cls):
        """
        Get blacklist statistics (if supported by cache backend)
        
        Returns:
            dict: Statistics about blacklisted tokens
        """
        try:
            # This is cache backend specific
            # For now, return basic info
            return {
                'backend': 'Redis',
                'prefix': cls.BLACKLIST_PREFIX,
                'status': 'active'
            }
        except Exception as e:
            logger.error(f"Failed to get blacklist stats: {str(e)}")
            return {}
