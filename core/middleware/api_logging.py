"""
API Logging Middleware - HYBRID Approach
Logs ALL requests to file (fast, complete history)
Logs IMPORTANT events to database (queryable, analytics)
"""
import json
import time
import logging
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone

# File logger for ALL requests
file_logger = logging.getLogger('api_access')

# Will import at runtime to avoid circular import
APIAccessLog = None


def get_client_ip(request):
    """Get real client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', 'unknown')
    return ip


def get_api_version(path):
    """Extract API version from path"""
    if '/4.0/' in path or '/v4/' in path:
        return '4.0'
    elif '/5.0/' in path or '/v5/' in path:
        return '5.0'
    return None


def should_log_to_database(request, response, response_time):
    """
    Determine if this request should be logged to database
    
    Log to database only for IMPORTANT events:
    - Login attempts (success or fail)
    - Failed requests (4xx, 5xx)
    - Slow requests (>2 seconds)
    - Rate limit hits (429)
    - Token operations (logout, revoke)
    """
    status_code = response.status_code
    path = request.path.lower()
    
    # Login attempts (all)
    if 'login' in path or 'auth' in path:
        return True
    
    # Failed requests (4xx, 5xx)
    if status_code >= 400:
        return True
    
    # Slow requests (>2 seconds)
    if response_time > 2.0:
        return True
    
    # Rate limit hits
    if status_code == 429:
        return True
    
    # Token operations
    if any(keyword in path for keyword in ['logout', 'revoke', 'refresh']):
        return True
    
    # Don't log to database (only to file)
    return False


def safe_json_parse(data, max_size=10240):
    """
    Safely parse JSON data with size limit
    Returns dict or truncated message if too large
    """
    if not data:
        return None
    
    try:
        if len(data) > max_size:
            return {
                '_truncated': True,
                '_size': len(data),
                '_message': f'Body too large ({len(data)} bytes), truncated to {max_size} bytes'
            }
        return json.loads(data)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {'_error': 'Invalid JSON or binary data'}


class APILoggingMiddleware(MiddlewareMixin):
    """
    Hybrid logging middleware
    - Logs ALL requests to file (fast)
    - Logs IMPORTANT requests to database (queryable)
    """
    
    def __init__(self, get_response):
        super().__init__(get_response)
        # Lazy import to avoid circular dependency
        global APIAccessLog
        if APIAccessLog is None:
            from core.models import APIAccessLog
    
    def process_request(self, request):
        """Mark request start time"""
        request._start_time = time.time()
        return None
    
    def process_response(self, request, response):
        """Log request to file and optionally to database"""
        
        # Calculate response time
        if hasattr(request, '_start_time'):
            response_time = time.time() - request._start_time
        else:
            response_time = 0
        
        # Skip static files and health check
        if request.path.startswith('/static/') or request.path == '/health/':
            return response
        
        # Get request data
        method = request.method
        endpoint = request.path
        full_url = request.build_absolute_uri()
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        status_code = response.status_code
        api_version = get_api_version(endpoint)
        
        # Get user info
        user = None
        username = None
        if hasattr(request, 'jwt_user'):
            user = request.jwt_user
            username = user.username if user else None
        elif hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user
            username = user.username
        
        # Get request details
        query_params = dict(request.GET) if request.GET else None
        
        # Parse request body (limit size)
        request_body = None
        if method in ['POST', 'PUT', 'PATCH']:
            try:
                request_body = safe_json_parse(request.body)
            except:
                pass
        
        # Get selected headers
        request_headers = {
            'Content-Type': request.META.get('CONTENT_TYPE'),
            'Accept': request.META.get('HTTP_ACCEPT'),
            'Authorization': 'Bearer ***' if request.META.get('HTTP_AUTHORIZATION') else None,
        }
        request_headers = {k: v for k, v in request_headers.items() if v}
        
        # Get response size
        response_size = len(response.content) if hasattr(response, 'content') else None
        
        # Check if rate limited
        rate_limit_hit = status_code == 429
        
        # Get error message if failed
        error_message = None
        if status_code >= 400:
            try:
                if hasattr(response, 'content'):
                    error_data = json.loads(response.content)
                    error_message = error_data.get('message') or error_data.get('error')
            except:
                pass
        
        # Prepare log data
        log_data = {
            'timestamp': timezone.now().isoformat(),
            'method': method,
            'endpoint': endpoint,
            'full_url': full_url,
            'user_id': user.id if user else None,
            'username': username,
            'ip_address': ip_address,
            'user_agent': user_agent[:200],  # Truncate
            'status_code': status_code,
            'response_time': round(response_time, 3),
            'response_size': response_size,
            'api_version': api_version,
            'rate_limit_hit': rate_limit_hit,
        }
        
        # 1. ALWAYS log to file (ALL requests)
        try:
            file_logger.info(json.dumps(log_data))
        except Exception as e:
            # Don't fail request if logging fails
            print(f"File logging error: {e}")
        
        # 2. Conditionally log to database (IMPORTANT only)
        if should_log_to_database(request, response, response_time):
            try:
                APIAccessLog.objects.create(
                    method=method,
                    endpoint=endpoint[:500],  # Truncate to field limit
                    full_url=full_url,
                    user=user,
                    username=username,
                    ip_address=ip_address,
                    user_agent=user_agent[:1000] if user_agent else None,
                    request_headers=request_headers,
                    request_body=request_body,
                    query_params=query_params,
                    status_code=status_code,
                    response_size=response_size,
                    response_time=response_time,
                    api_version=api_version,
                    rate_limit_hit=rate_limit_hit,
                    error_message=error_message[:500] if error_message else None,
                )
            except Exception as e:
                # Don't fail request if database logging fails
                print(f"Database logging error: {e}")
        
        return response
