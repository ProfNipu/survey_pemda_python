"""
Rate Limiting System for API Endpoints
Uses Redis/Cache for fast, distributed rate limiting
"""
from django.core.cache import cache
from django.http import JsonResponse
from functools import wraps
import time
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Rate limiter using sliding window algorithm
    Stores request counts in Redis/cache with auto-expiration
    """
    
    PREFIX = "ratelimit:"
    
    @staticmethod
    def get_client_identifier(request, key_type='user_or_ip'):
        """
        Get client identifier for rate limiting
        
        Args:
            request: Django request object
            key_type: 'user', 'ip', or 'user_or_ip'
        
        Returns:
            str: Client identifier
        """
        if key_type == 'user' or key_type == 'user_or_ip':
            # Try to get authenticated user first
            if hasattr(request, 'jwt_user'):
                return f"user_{request.jwt_user.id}"
        
        if key_type == 'ip' or key_type == 'user_or_ip':
            # Fall back to IP address
            # Get real IP from proxy headers if behind proxy
            ip = request.META.get('HTTP_X_FORWARDED_FOR')
            if ip:
                # X-Forwarded-For can contain multiple IPs, get the first one
                ip = ip.split(',')[0].strip()
            else:
                ip = request.META.get('REMOTE_ADDR', 'unknown')
            return f"ip_{ip}"
        
        return 'unknown'
    
    @staticmethod
    def check_rate_limit(identifier, endpoint, max_requests, window_seconds):
        """
        Check if rate limit is exceeded
        
        Args:
            identifier: Client identifier (user_id or ip)
            endpoint: Endpoint name
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds
        
        Returns:
            tuple: (allowed: bool, retry_after: int, current_count: int)
        """
        cache_key = f"{RateLimiter.PREFIX}{endpoint}:{identifier}"
        
        # Get current request data
        current_data = cache.get(cache_key)
        
        current_time = time.time()
        
        if current_data is None:
            # First request
            cache.set(cache_key, {
                'count': 1,
                'start_time': current_time,
                'window': window_seconds
            }, window_seconds)
            return True, 0, 1
        
        # Check if window has expired
        elapsed = current_time - current_data['start_time']
        
        if elapsed > window_seconds:
            # Window expired, reset counter
            cache.set(cache_key, {
                'count': 1,
                'start_time': current_time,
                'window': window_seconds
            }, window_seconds)
            return True, 0, 1
        
        # Window still active
        current_count = current_data['count']
        
        if current_count >= max_requests:
            # Rate limit exceeded
            retry_after = int(window_seconds - elapsed)
            return False, retry_after, current_count
        
        # Increment counter
        current_data['count'] += 1
        cache.set(cache_key, current_data, window_seconds)
        
        return True, 0, current_data['count']
    
    @staticmethod
    def reset_limit(identifier, endpoint):
        """
        Reset rate limit for a specific client and endpoint
        Useful for testing or admin override
        
        Args:
            identifier: Client identifier
            endpoint: Endpoint name
        """
        cache_key = f"{RateLimiter.PREFIX}{endpoint}:{identifier}"
        cache.delete(cache_key)
        logger.info(f"Rate limit reset for {identifier} on {endpoint}")


def rate_limit(max_requests=100, window=60, key_type='user_or_ip'):
    """
    Rate limiting decorator for Django views
    
    Args:
        max_requests: Maximum number of requests allowed
        window: Time window in seconds
        key_type: 'user', 'ip', or 'user_or_ip' (default)
    
    Usage:
        @rate_limit(max_requests=10, window=60, key_type='ip')
        def my_view(request):
            ...
    
    Response codes:
        429 Too Many Requests - Rate limit exceeded
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Get client identifier
            identifier = RateLimiter.get_client_identifier(request, key_type)
            
            # Get endpoint name
            endpoint = view_func.__name__
            
            # Check rate limit
            allowed, retry_after, current_count = RateLimiter.check_rate_limit(
                identifier, endpoint, max_requests, window
            )
            
            if not allowed:
                # Rate limit exceeded
                logger.warning(
                    f"Rate limit exceeded for {identifier} on {endpoint}. "
                    f"Count: {current_count}/{max_requests} in {window}s"
                )
                
                response = JsonResponse({
                    'status': 'error',
                    'message': f'Rate limit exceeded. Maximum {max_requests} requests per {window} seconds',
                    'code': 'RATE_LIMIT_EXCEEDED',
                    'retry_after': retry_after,
                    'limit': {
                        'max_requests': max_requests,
                        'window_seconds': window,
                        'current_count': current_count
                    }
                }, status=429)
                
                # Add rate limit headers
                response['X-RateLimit-Limit'] = str(max_requests)
                response['X-RateLimit-Remaining'] = '0'
                response['X-RateLimit-Reset'] = str(int(time.time() + retry_after))
                response['Retry-After'] = str(retry_after)
                
                return response
            
            # Add rate limit info to response headers
            response = view_func(request, *args, **kwargs)
            
            # Add headers if response is JsonResponse or HttpResponse
            if hasattr(response, '__setitem__'):
                response['X-RateLimit-Limit'] = str(max_requests)
                response['X-RateLimit-Remaining'] = str(max_requests - current_count)
                response['X-RateLimit-Reset'] = str(int(time.time() + window))
            
            return response
        
        return wrapper
    return decorator


# Preset rate limit decorators for common use cases
def rate_limit_strict(view_func):
    """Strict rate limit: 5 requests per minute (for login, sensitive operations)"""
    return rate_limit(max_requests=5, window=60, key_type='ip')(view_func)


def rate_limit_moderate(view_func):
    """Moderate rate limit: 60 requests per minute (for authenticated endpoints)"""
    return rate_limit(max_requests=60, window=60, key_type='user_or_ip')(view_func)


def rate_limit_relaxed(view_func):
    """Relaxed rate limit: 200 requests per minute (for high-traffic endpoints)"""
    return rate_limit(max_requests=200, window=60, key_type='user_or_ip')(view_func)
