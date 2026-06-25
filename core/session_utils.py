"""
Utility functions for session management
Handle single session per user (force logout from other devices)

Special rule: Only enforce single session for NIP/NIK-based usernames
- NIP: 18 digits (e.g., 199411192019031001)
- NIK: 16 digits (e.g., 1234567890123456)
- Other usernames: Allow multiple devices
"""
from django.core.cache import cache
from django_redis import get_redis_connection
from django.conf import settings
import logging
import re

logger = logging.getLogger(__name__)


def is_nip_or_nik_username(username):
    """
    Check if username is NIP or NIK format
    NIP format: 199411192019031001 (18 digits)
    NIK format: 1234567890123456 (16 digits)
    
    Args:
        username: Username string to check
    
    Returns:
        bool: True if username is NIP (18 digits) or NIK (16 digits), False otherwise
    """
    if not username:
        return False
    
    username_str = str(username).strip()
    
    # Check if username is exactly 18 digits (NIP) or 16 digits (NIK)
    return bool(re.match(r'^\d{18}$', username_str)) or bool(re.match(r'^\d{16}$', username_str))


# Alias for backward compatibility
def is_nip_username(username):
    """
    Alias for is_nip_or_nik_username for backward compatibility
    """
    return is_nip_or_nik_username(username)


def force_single_session(user):
    """
    Force logout all other sessions for this user
    Keep only the newest session (current login)
    
    Args:
        user: Django User instance
    
    Returns:
        int: Number of old sessions deleted
    """
    try:
        # Get Redis connection
        redis_conn = get_redis_connection("default")
        
        # Get user's session tracking key
        user_session_key = f"{getattr(settings, 'APP_KEY_PREFIX', 'aplikasi-test')}:user_session:{user.id}"
        
        # Get old session key for this user (plain Django session_key)
        old_session_key = redis_conn.get(user_session_key)
        
        deleted_count = 0
        
        if old_session_key:
            old_session_key = old_session_key.decode()
            
            # Mark old session as superseded (so frontend can show SweetAlert)
            try:
                from importlib import import_module
                from django.conf import settings
                engine = import_module(settings.SESSION_ENGINE)
                SessionStore = engine.SessionStore
                store = SessionStore(session_key=old_session_key)
                # Load existing data (ignore errors)
                try:
                    store.load()
                except Exception:
                    pass
                store['session_superseded'] = True
                store['logout_reason'] = 'another_login'
                store.save()
                deleted_count += 1  # count as handled
                logger.info(f"Marked old session as superseded for user {user.id}: {old_session_key}")
            except Exception as e:
                logger.error(f"Failed to mark old session as superseded for user {user.id}: {e}")
        
        return deleted_count
        
    except Exception as e:
        logger.error(f"Error in force_single_session for user {user.id}: {e}")
        return 0


def track_user_session(user, session_key):
    """
    Track current session key for user
    Store mapping: user_id → session_key
    
    Args:
        user: Django User instance
        session_key: Current session key
    """
    try:
        redis_conn = get_redis_connection("default")
        
        # Store user → session mapping (plain Django session_key)
        user_session_key = f"{getattr(settings, 'APP_KEY_PREFIX', 'aplikasi-test')}:user_session:{user.id}"
        
        # Set with same TTL as session (1800 seconds)
        redis_conn.setex(user_session_key, 1800, session_key)
        
        logger.info(f"Tracking session for user {user.id}: {session_key}")
        
    except Exception as e:
        logger.error(f"Error tracking session for user {user.id}: {e}")


def get_active_sessions_count(user):
    """
    Get count of active sessions for user
    
    Args:
        user: Django User instance
    
    Returns:
        int: Number of active sessions
    """
    try:
        redis_conn = get_redis_connection("default")
        user_session_key = f"{getattr(settings, 'APP_KEY_PREFIX', 'aplikasi-test')}:user_session:{user.id}"
        
        # Check if user has active session
        if redis_conn.exists(user_session_key):
            return 1
        return 0
        
    except Exception as e:
        logger.error(f"Error getting session count for user {user.id}: {e}")
        return 0


def should_enforce_single_session(user):
    """
    Determine if single session should be enforced for this user
    
    Rule: Only enforce single session for NIP (18 digits) or NIK (16 digits) usernames
    Other usernames: Allow multiple devices
    
    Args:
        user: Django User instance
    
    Returns:
        bool: True if single session should be enforced, False otherwise
    """
    # Backward-compat global flag
    if not getattr(settings, 'SINGLE_SESSION_ENFORCE_NIP_NIK', False):
        return False
    return _is_user_nipnik(user)


def _is_user_nipnik(user):
    """Return True if user qualifies as NIP/NIK based on username or user.nip/nik"""
    if is_nip_or_nik_username(getattr(user, 'username', '')):
        return True
    if hasattr(user, 'nip') and user.nip and is_nip_or_nik_username(user.nip):
        return True
    if hasattr(user, 'nik') and user.nik and is_nip_or_nik_username(user.nik):
        return True
    return False


def should_enforce_single_session_web(user):
    """Web-only enforcement controlled by SINGLE_SESSION_ENFORCE_WEB_NIP_NIK"""
    if not getattr(settings, 'SINGLE_SESSION_ENFORCE_WEB_NIP_NIK', False):
        return False
    return _is_user_nipnik(user)


def should_enforce_single_session_api(user):
    """API-only enforcement controlled by SINGLE_SESSION_ENFORCE_API_NIP_NIK"""
    if not getattr(settings, 'SINGLE_SESSION_ENFORCE_API_NIP_NIK', False):
        return False
    return _is_user_nipnik(user)
