from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.db import connections
from django.core.cache import cache
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Q
import json
import logging

# JWT imports
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken, TokenError
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from datetime import timedelta
from core.rate_limiter import rate_limit, rate_limit_strict, rate_limit_moderate

logger = logging.getLogger(__name__)
User = get_user_model()


# Custom Permanent Token Class for v4.0
class PermanentAccessToken(AccessToken):
    """
    Custom JWT Token with permanent lifetime (100 years)
    For Laravel v4.0 API compatibility
    """
    @classmethod
    def for_user(cls, user):
        token = super().for_user(user)
        # Set token to expire in 100 years (effectively permanent)
        token.set_exp(lifetime=timedelta(days=36500))  # 100 years
        return token


# JWT Authentication Decorator
def jwt_required(view_func):
    """
    Decorator to require JWT authentication for API endpoints
    Checks Authorization: Bearer <token> header
    """
    from functools import wraps
    
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Get Authorization header
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header:
            return JsonResponse({
                'status': 'error',
                'message': 'Missing Authorization header',
                'code': 'MISSING_AUTH_HEADER',
                'version': '5.0'
            }, status=401)
        
        # Check Bearer format
        if not auth_header.startswith('Bearer '):
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid Authorization header format. Use: Bearer <token>',
                'code': 'INVALID_AUTH_FORMAT',
                'version': '5.0'
            }, status=401)
        
        # Extract token
        token_str = auth_header.split(' ')[1]
        
        try:
            # Verify token (support both v4.0 permanent and v5.0 time-based tokens)
            token = AccessToken(token_str)
            user_id = token.get('user_id')
            token_issued_at = token.get('iat')  # Issued at timestamp
            
            # Check if token is blacklisted
            from core.token_blacklist import TokenBlacklist
            if TokenBlacklist.is_blacklisted(token_str):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Token has been revoked',
                    'code': 'TOKEN_REVOKED',
                    'version': '5.0'
                }, status=401)
            
            # Get user
            try:
                user = User.objects.get(id=user_id)
                
                # Check if user is active
                if not user.is_active:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'User account is inactive',
                        'code': 'USER_INACTIVE',
                        'version': '5.0'
                    }, status=403)
                
                # Check if all user tokens are blacklisted (e.g., after password change)
                if TokenBlacklist.is_user_blacklisted(user_id, token_issued_at):
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Token has been revoked (user action)',
                        'code': 'TOKEN_REVOKED_USER',
                        'version': '5.0'
                    }, status=401)
                
                # Attach user and token to request
                request.jwt_user = user
                request.jwt_token = token_str  # Store token for logout
                
                # Call the original view
                return view_func(request, *args, **kwargs)
                
            except User.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'User not found',
                    'code': 'USER_NOT_FOUND',
                    'version': '5.0'
                }, status=404)
                
        except (TokenError, InvalidToken) as e:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid or expired token',
                'code': 'INVALID_TOKEN',
                'version': '5.0'
            }, status=401)
        except Exception as e:
            logger.error(f"JWT authentication error: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': 'Authentication failed',
                'code': 'AUTH_ERROR',
                'version': '5.0'
            }, status=401)
    
    return wrapper

def landing_page(request):
    """
    Landing page = Login page (backend-only system)
    POST handler untuk login dari landing page
    """
    # Redirect jika sudah login
    if request.user.is_authenticated:
        return redirect('/dashboard/')
    
    # Note: app_name, app_long_name, app_instansi now auto-injected by context processor
    # No need to manually add context here!
    
    # Handle POST (login form submission)
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember = request.POST.get('remember', False)
        
        # Check if AJAX request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        # Check if user exists (by username or email)
        user_exists = User.objects.filter(
            Q(username=username) | Q(email=username)
        ).exists()
        
        # If user not exists, try login via ESIMPEG API first
        if not user_exists:
            logger.info(f"User {username} not found in local database, trying ESIMPEG API login...")
            
            # Try login via ESIMPEG API
            from apps.accounts.services import EsimpegAPIService
            esimpeg_api = EsimpegAPIService()
            
            try:
                api_response = esimpeg_api.login(username, password)
                
                if api_response:
                    # Login successful via API, create user in local database
                    user_data = api_response.get('user', {})
                    
                    logger.info(f"ESIMPEG API login successful for {username}, creating local user...")
                    
                    # Determine if password is default or custom
                    is_default_password = (password == 'Pegawai@Pessel')
                    
                    # Create user with the password used for login
                    # If default password, user will be forced to change
                    # If custom password, user can login directly
                    user = User.objects.create_user(
                        username=user_data.get('username', username),
                        email=user_data.get('email'),
                        name=user_data.get('name', username),
                        password=password,  # Use actual password from login
                        id_pegawai=user_data.get('id_pegawai', 0),
                        user_id_opd=user_data.get('user_id_opd', 0)
                    )
                    
                    # Log user creation
                    try:
                        from core.models import MsLogData
                        MsLogData.objects.create(
                            user_id=user.id,
                            action='user_created_from_api',
                            table_name='users',
                            record_id=user.id,
                            new_data={
                                'username': user.username,
                                'name': user.name,
                                'source': 'esimpeg_api',
                                'api_user_id': user_data.get('user_id'),
                                'id_pegawai': user_data.get('id_pegawai', 0),
                                'user_id_opd': user_data.get('user_id_opd', 0),
                                'is_default_password': is_default_password
                            },
                            ip_address=request.META.get('REMOTE_ADDR', ''),
                            user_agent=request.META.get('HTTP_USER_AGENT', '')
                        )
                    except Exception as log_err:
                        logger.error(f"Failed to log user creation: {log_err}")
                    
                    # Now authenticate with the actual password
                    user = authenticate(request, username=username, password=password)
                    
                    if user is None:
                        error_msg = 'Gagal membuat user lokal. Silakan coba lagi.'
                        if is_ajax:
                            return JsonResponse({'success': False, 'message': error_msg, 'type': 'error'})
                        messages.error(request, error_msg)
                        return render(request, 'landing.html')
                    
                    # Store ESIMPEG API tokens in session for future API calls
                    request.session['esimpeg_access_token'] = api_response.get('access_token')
                    request.session['esimpeg_refresh_token'] = api_response.get('refresh_token')
                    logger.info(f"Stored ESIMPEG tokens in session for user {username}")
                    
                    # Continue to login flow below
                    # If password is default (Pegawai@Pessel), will force change password
                    # If password is custom, will go directly to dashboard
                    
                else:
                    # API login failed, user not found
                    error_msg = 'Username atau password salah. Jika Anda pegawai baru, silakan hubungi administrator.'
                    
                    # Log failed login attempt
                    try:
                        from core.models import MsLogData
                        MsLogData.log_login_failed(username, request, via='web', reason='API login failed - user not found')
                    except Exception as e:
                        logger.error(f"Failed to log login failure: {e}")
                    
                    if is_ajax:
                        return JsonResponse({'success': False, 'message': error_msg, 'type': 'error'})
                    messages.error(request, error_msg)
                    return render(request, 'landing.html')
                    
            except Exception as api_err:
                logger.error(f"ESIMPEG API error: {api_err}")
                
                # API down or error, show error message
                error_msg = 'Sistem ESIMPEG sedang tidak tersedia. Silakan coba lagi nanti atau hubungi administrator.'
                
                if is_ajax:
                    return JsonResponse({'success': False, 'message': error_msg, 'type': 'error'})
                messages.error(request, error_msg)
                return render(request, 'landing.html')
        
        else:
            # User exists in local database, authenticate normally
            user = authenticate(request, username=username, password=password)
            
            # If authentication successful, try to get ESIMPEG token
            if user is not None:
                logger.info(f"User {username} exists locally, attempting ESIMPEG API login for token...")
                
                from apps.accounts.services import EsimpegAPIService
                esimpeg_api = EsimpegAPIService()
                
                try:
                    api_response = esimpeg_api.login(username, password)
                    
                    if api_response:
                        # Store ESIMPEG API tokens in session
                        request.session['esimpeg_access_token'] = api_response.get('access_token')
                        request.session['esimpeg_refresh_token'] = api_response.get('refresh_token')
                        logger.info(f"Stored ESIMPEG tokens in session for existing user {username}")
                    else:
                        logger.warning(f"Could not get ESIMPEG token for user {username} (user may not exist in ESIMPEG)")
                        
                except Exception as api_err:
                    logger.warning(f"ESIMPEG API error for existing user {username}: {api_err}")
                    # Continue with local login even if ESIMPEG API fails
        
        if user is not None:
            # CONDITIONAL SINGLE SESSION: Only enforce for NIP/NIK-based usernames
            from core.session_utils import (
                should_enforce_single_session_web,
                force_single_session,
                track_user_session
            )
            
            # Check if single session should be enforced (NIP/NIK usernames only)
            if should_enforce_single_session_web(user):
                # Delete old sessions for this user (logout from other devices)
                deleted = force_single_session(user)
                if deleted > 0:
                    logger.info(f"[NIP/NIK] Logged out {deleted} other session(s) for user {user.username}")
            else:
                logger.info(f"[Non-NIP/NIK] Allowing multiple devices for user {user.username}")
            
            # Login sukses (create new session)
            login(request, user)
            
            # Track this new session (only if single session enforced)
            if should_enforce_single_session_web(user):
                track_user_session(user, request.session.session_key)
            
            # Set session expiry
            if not remember:
                request.session.set_expiry(0)  # Expire saat browser ditutup
            else:
                request.session.set_expiry(2592000)  # 30 days
            
            # Log login activity to ms_log_data
            try:
                from core.models import MsLogData
                MsLogData.log_login(user, request, via='web')
            except Exception as e:
                logger.error(f"Failed to log login activity: {e}")
            
            success_msg = f'Selamat datang, {user.name}!'
            next_url = request.GET.get('next', '/dashboard/')
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': success_msg,
                    'redirect_url': next_url,
                    'type': 'success'
                })
            else:
                messages.success(request, success_msg)
                return redirect(next_url)
        else:
            # User exists but password wrong
            error_msg = 'Username atau password salah!'
            
            # Log failed login attempt (wrong password)
            try:
                from core.models import MsLogData
                MsLogData.log_login_failed(username, request, via='web', reason='Invalid password')
            except Exception as e:
                logger.error(f"Failed to log login failure: {e}")
            
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': error_msg,
                    'type': 'error'
                })
            else:
                messages.error(request, error_msg)
    
    # Render landing page dengan login form
    return render(request, 'landing.html')

@require_http_methods(["POST"])
def login_view(request):
    """Handle login from landing page"""
    username = request.POST.get('username')
    password = request.POST.get('password')
    
    if username and password:
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'✅ Selamat datang, {user.username}!')
            return redirect('/dashboard/')
        else:
            messages.error(request, 'Username atau password salah!')
    else:
        messages.error(request, 'Username dan password harus diisi!')
    
    return redirect('/')


def logout_view(request):
    """Handle logout - supports both GET and POST"""
    logout(request)
    messages.success(request, '✅ Anda telah logout. Sampai jumpa!')
    return redirect('landing_page')


@csrf_exempt
def health_check(request):
    """Health check endpoint for Docker healthcheck"""
    try:
        # Check database connection
        db_conn = connections['default']
        db_conn.cursor()
        
        # Check Redis connection
        cache.set('health_check', 'ok', 30)
        cache_status = cache.get('health_check')
        
        return JsonResponse({
            'status': 'healthy',
            'database': 'connected',
            'cache': 'connected' if cache_status == 'ok' else 'disconnected',
            'message': f"{getattr(settings, 'APP_NAME', 'Aplikasi')} is running"
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e)
        }, status=500)


def session_status(request):
    """Return current session status flags for frontend polling"""
    return JsonResponse({
        'authenticated': request.user.is_authenticated,
        'session_superseded': bool(request.session.get('session_superseded', False)),
        'logout_reason': request.session.get('logout_reason', '')
    })


def _dev_allowed(request):
    """Allow access if DEBUG=True or user is superadmin. Used for test error pages."""
    try:
        from apps.manajemen.helpers import is_superadmin
        return bool(getattr(settings, 'DEBUG', False) or (request.user.is_authenticated and is_superadmin(request.user)))
    except Exception:
        return False


@require_http_methods(["GET"])  # Test 400 page
def dev_test_400(request):
    if not _dev_allowed(request):
        return redirect('/')
    return render(request, '400.html', status=400)


@require_http_methods(["GET"])  # Test 404 page
def dev_test_404(request):
    if not _dev_allowed(request):
        return redirect('/')
    return render(request, '404.html', status=404)


@require_http_methods(["GET"])  # Test 500 page
def dev_test_500(request):
    if not _dev_allowed(request):
        return redirect('/')
    return render(request, '500.html', status=500)

@csrf_exempt
@require_http_methods(["GET", "POST"])
@rate_limit(max_requests=10, window=60, key_type='ip')  # 10 login attempts per minute per IP
def api_login_v4(request):
    """
    API Login endpoint v4.0 - Laravel Compatible (OLD VERSION)
    
    URL: /apiaplikasi-test/4.0/login/username-aplikasi-test
    Method: GET or POST
    Query Params:
        - login_username: Username, email, atau NIP
        - login_password: Password
    
    Response Format (OLD):
        Success: {
            "status": "success",
            "message": "Login berhasil",
            "data": {
                "user_id": 123,
                "username": "username",
                "name": "Nama User",
                "email": "email@example.com",
                "id_pegawai": 456,
                "session_key": "xxx..."
            }
        }
        Error: {
            "status": "error",
            "message": "Error message",
            "code": "ERROR_CODE"
        }
    
    NOTE: This is the old version (v4.0) for backward compatibility.
          New applications should use v5.0
    """
    # Get credentials from query params (support both GET and POST)
    login_username = request.GET.get('login_username') or request.POST.get('login_username')
    login_password = request.GET.get('login_password') or request.POST.get('login_password')
    
    # Validation
    if not login_username or not login_password:
        return JsonResponse({
            'data': None,
            'success_message': None,
            'errors': ['Username dan password harus diisi'],
            'error_message': 'Username dan password harus diisi'
        }, status=400)
    
    # Check if user exists (by username or email)
    user_exists = User.objects.filter(
        Q(username=login_username) | Q(email=login_username)
    ).exists()
    
    if not user_exists:
        return JsonResponse({
            'data': None,
            'success_message': None,
            'errors': ['Username tidak ditemukan. Silakan hubungi administrator untuk registrasi akun.'],
            'error_message': 'Username tidak ditemukan. Silakan hubungi administrator untuk registrasi akun.'
        }, status=404)
    
    # Authenticate user
    user = authenticate(request, username=login_username, password=login_password)
    
    if user is not None:
        # Check if user is active
        if not user.is_active:
            return JsonResponse({
                'data': None,
                'success_message': None,
                'errors': ['Akun tidak aktif. Silakan hubungi administrator.'],
                'error_message': 'Akun tidak aktif. Silakan hubungi administrator.'
            }, status=403)
        
        # Login user (create session)
        login(request, user)
        
        # Track session for single-session enforcement (optional)
        from core.session_utils import should_enforce_single_session, track_user_session
        if should_enforce_single_session(user):
            track_user_session(user, request.session.session_key)
        
        # Success response (Laravel v4.0 format)
        return JsonResponse({
            'data': {
                'username': user.username,
                'name': user.name,
                'email': user.email or user.username,  # Use username if email empty
                'password': user.password,  # Hash password (for compatibility)
                'user_id_opd': user.user_id_opd or 0,
                'usermode': 'user'  # Default usermode
            },
            'success_message': 'Login Success',
            'errors': [],
            'error_message': None
        }, status=200)
    else:
        # Password incorrect
        return JsonResponse({
            'data': None,
            'success_message': None,
            'errors': ['Username atau password salah'],
            'error_message': 'Username atau password salah'
        }, status=401)


@csrf_exempt
@require_http_methods(["GET", "POST"])
@rate_limit(max_requests=10, window=60, key_type='ip')  # 10 login attempts per minute per IP
def api_jwt_login_v4(request):
    """
    JWT Login endpoint v4.0 - Laravel Compatible with PERMANENT Token
    
    URL: /apiaplikasi-test/4.0/login/get-token
    Method: GET or POST
    Query Params or Body:
        - login_email: Username atau email
        - login_password: Password
    
    Response (Laravel v4.0 Format):
        Success: {
            "data": {
                "name": "User Name",
                "email": "email@example.com",
                "image": "img.jpg",
                "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
            },
            "success_message": "",
            "errors": [],
            "error_message": null
        }
    
    WARNING: Token has 100 years lifetime (effectively permanent)
    """
    try:
        # Get credentials from query params or body
        if request.method == 'GET':
            login_email = request.GET.get('login_email', '')
            login_password = request.GET.get('login_password', '')
        else:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                login_email = data.get('login_email', '')
                login_password = data.get('login_password', '')
            else:
                login_email = request.POST.get('login_email', '')
                login_password = request.POST.get('login_password', '')
        
        # Validation
        if not login_email or not login_password:
            return JsonResponse({
                'data': None,
                'success_message': '',
                'errors': ['Username dan password harus diisi'],
                'error_message': 'Username dan password harus diisi'
            }, status=400)
        
        # Check if user exists (by username or email)
        user_exists = User.objects.filter(
            Q(username=login_email) | Q(email=login_email)
        ).exists()
        
        if not user_exists:
            return JsonResponse({
                'data': None,
                'success_message': '',
                'errors': ['Username tidak ditemukan'],
                'error_message': 'Username tidak ditemukan'
            }, status=404)
        
        # Authenticate user
        user = authenticate(request, username=login_email, password=login_password)
        
        if user is not None:
            # Check if user is active
            if not user.is_active:
                return JsonResponse({
                    'data': None,
                    'success_message': '',
                    'errors': ['Akun tidak aktif'],
                    'error_message': 'Akun tidak aktif'
                }, status=403)
            
            # Generate PERMANENT JWT token (100 years lifetime)
            permanent_token = PermanentAccessToken.for_user(user)
            token_string = str(permanent_token)
            
            # Update last login
            from django.utils import timezone
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            
            # Log login activity to ms_log_data
            try:
                from core.models import MsLogData
                MsLogData.log_login(user, request, via='api_v4')
            except Exception as e:
                logger.error(f"Failed to log login activity: {e}")
            
            # Success response (Laravel v4.0 format)
            return JsonResponse({
                'data': {
                    'name': user.name,
                    'email': user.email or user.username,
                    'image': user.image or 'img.jpg',
                    'token': token_string
                },
                'success_message': '',
                'errors': [],
                'error_message': None
            }, status=200)
        else:
            # Log failed login attempt
            try:
                from core.models import MsLogData
                MsLogData.log_login_failed(login_email, request, via='api_v4', reason='Invalid credentials')
            except Exception as e:
                logger.error(f"Failed to log login failure: {e}")
            
            # Invalid credentials
            return JsonResponse({
                'data': None,
                'success_message': '',
                'errors': ['Username atau password salah'],
                'error_message': 'Username atau password salah'
            }, status=401)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'data': None,
            'success_message': '',
            'errors': ['Invalid JSON format'],
            'error_message': 'Invalid JSON format'
        }, status=400)
    except Exception as e:
        logger.error(f"JWT v4.0 login error: {str(e)}")
        return JsonResponse({
            'data': None,
            'success_message': '',
            'errors': ['Internal server error'],
            'error_message': 'Internal server error'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET", "POST"])
@rate_limit(max_requests=10, window=60, key_type='ip')  # 10 login attempts per minute per IP
def api_login_v5(request):
    """
    API Login endpoint v5.0 - NEW VERSION
    
    URL: /apiaplikasi-test/5.0/login/username-aplikasi-test
    Method: GET or POST
    Query Params:
        - login_username: Username, email, atau NIP
        - login_password: Password
    
    Response Format (NEW - dapat dikustomisasi):
        Success: {
            "status": "success",
            "message": "Login berhasil",
            "data": {
                "user_id": 123,
                "username": "username",
                "name": "Nama User",
                "email": "email@example.com",
                "id_pegawai": 456,
                "session_key": "xxx...",
                "is_active": true
            },
            "version": "5.0"
        }
        Error: {
            "status": "error",
            "message": "Error message",
            "code": "ERROR_CODE",
            "version": "5.0"
        }
    
    NOTE: This is the new version (v5.0).
          Response format bisa dikustomisasi sesuai kebutuhan.
    """
    # Get credentials from query params (support both GET and POST)
    login_username = request.GET.get('login_username') or request.POST.get('login_username')
    login_password = request.GET.get('login_password') or request.POST.get('login_password')
    
    # Validation
    if not login_username or not login_password:
        return JsonResponse({
            'status': 'error',
            'message': 'Username dan password harus diisi',
            'code': 'MISSING_CREDENTIALS',
            'version': '5.0'
        }, status=400)
    
    # Check if user exists (by username or email)
    user_exists = User.objects.filter(
        Q(username=login_username) | Q(email=login_username)
    ).exists()
    
    if not user_exists:
        return JsonResponse({
            'status': 'error',
            'message': 'Username tidak ditemukan. Silakan hubungi administrator untuk registrasi akun.',
            'code': 'USER_NOT_FOUND',
            'version': '5.0'
        }, status=404)
    
    # Authenticate user
    user = authenticate(request, username=login_username, password=login_password)
    
    if user is not None:
        # Check if user is active
        if not user.is_active:
            return JsonResponse({
                'status': 'error',
                'message': 'Akun tidak aktif. Silakan hubungi administrator.',
                'code': 'USER_INACTIVE',
                'version': '5.0'
            }, status=403)
        
        # Login user (create session)
        login(request, user)
        
        # Track session for single-session enforcement (optional)
        from core.session_utils import should_enforce_single_session, track_user_session
        if should_enforce_single_session(user):
            track_user_session(user, request.session.session_key)
        
        # Success response (NEW FORMAT - dapat dikustomisasi)
        return JsonResponse({
            'status': 'success',
            'message': 'Login berhasil',
            'data': {
                'user_id': user.id,
                'username': user.username,
                'name': user.name,
                'email': user.email or '',
                'id_pegawai': user.id_pegawai,
                'session_key': request.session.session_key,
                'is_active': user.is_active
            },
            'version': '5.0'
        }, status=200)
    else:
        # Password incorrect
        return JsonResponse({
            'status': 'error',
            'message': 'Username atau password salah',
            'code': 'INVALID_CREDENTIALS',
            'version': '5.0'
        }, status=401)


@csrf_exempt
@require_http_methods(["GET"])
@jwt_required
@rate_limit(max_requests=100, window=60, key_type='user_or_ip')  # 100 requests per minute
def api_users_list_v5(request):
    """
    API Users List endpoint v5.0 - REQUIRES JWT AUTHENTICATION
    
    URL: /apiaplikasi-test/5.0/users/list
    Method: GET
    Headers:
        Authorization: Bearer <token>  (REQUIRED)
    Query Params (optional):
        - page: Page number (default: 1)
        - per_page: Items per page (default: 50, max: 100)
        - search: Search by username/name/email
        - is_active: Filter by active status (true/false)
    
    Response:
        {
            "status": "success",
            "message": "Users retrieved successfully",
            "data": {
                "users": [...],
                "pagination": {
                    "total": 100,
                    "page": 1,
                    "per_page": 50,
                    "total_pages": 2
                }
            },
            "version": "5.0"
        }
    """
    try:
        # Get query parameters
        page = int(request.GET.get('page', 1))
        per_page = min(int(request.GET.get('per_page', 50)), 100)  # Max 100
        search = request.GET.get('search', '').strip()
        is_active_filter = request.GET.get('is_active', '').strip()
        
        # Base queryset
        users = User.objects.all()
        
        # Apply search filter
        if search:
            users = users.filter(
                Q(username__icontains=search) |
                Q(name__icontains=search) |
                Q(email__icontains=search)
            )
        
        # Apply active status filter
        if is_active_filter:
            if is_active_filter.lower() in ['true', '1', 'yes']:
                users = users.filter(is_active=True)
            elif is_active_filter.lower() in ['false', '0', 'no']:
                users = users.filter(is_active=False)
        
        # Get total count before pagination
        total_users = users.count()
        
        # Calculate pagination
        total_pages = (total_users + per_page - 1) // per_page  # Ceiling division
        
        # Validate page number
        if page < 1:
            page = 1
        if page > total_pages and total_pages > 0:
            page = total_pages
        
        # Apply pagination
        start = (page - 1) * per_page
        end = start + per_page
        users_page = users[start:end]
        
        # Build users list
        users_data = []
        for user in users_page:
            users_data.append({
                'user_id': user.id,
                'username': user.username,
                'name': user.name,
                'email': user.email or '',
                'id_pegawai': user.id_pegawai or 0,
                'user_id_opd': user.user_id_opd or 0,
                'is_active': user.is_active,
                'date_joined': user.date_joined.isoformat() if user.date_joined else None,
                'last_login': user.last_login.isoformat() if user.last_login else None
            })
        
        # Success response
        return JsonResponse({
            'status': 'success',
            'message': f'Retrieved {len(users_data)} users successfully',
            'data': {
                'users': users_data,
                'pagination': {
                    'total': total_users,
                    'page': page,
                    'per_page': per_page,
                    'total_pages': total_pages
                }
            },
            'version': '5.0'
        }, status=200)
        
    except ValueError as e:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid pagination parameters',
            'code': 'INVALID_PARAMETERS',
            'version': '5.0'
        }, status=400)
    except Exception as e:
        logger.error(f"Users list error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Internal server error',
            'code': 'SERVER_ERROR',
            'version': '5.0'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@rate_limit(max_requests=10, window=60, key_type='ip')  # 10 login attempts per minute per IP
def api_jwt_login_v5(request):
    """
    JWT Login endpoint v5.0
    
    URL: /apiaplikasi-test/5.0/auth/login
    Method: POST
    Body (JSON or form-data):
        - username: Username, email, atau NIP
        - password: Password
    
    Response:
        Success: {
            "status": "success",
            "message": "Login successful",
            "data": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                "token_type": "Bearer",
                "expires_in": 86400,
                "user": {
                    "user_id": 1,
                    "username": "username",
                    "name": "Full Name",
                    "email": "email@example.com"
                }
            },
            "version": "5.0"
        }
    """
    try:
        # Get credentials from JSON body or form-data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
        else:
            username = request.POST.get('username')
            password = request.POST.get('password')
        
        # Validation
        if not username or not password:
            return JsonResponse({
                'status': 'error',
                'message': 'Username dan password harus diisi',
                'code': 'MISSING_CREDENTIALS',
                'version': '5.0'
            }, status=400)
        
        # Check if user exists
        user_exists = User.objects.filter(
            Q(username=username) | Q(email=username)
        ).exists()
        
        if not user_exists:
            return JsonResponse({
                'status': 'error',
                'message': 'Username tidak ditemukan',
                'code': 'USER_NOT_FOUND',
                'version': '5.0'
            }, status=404)
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if user is active
            if not user.is_active:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Akun tidak aktif',
                    'code': 'USER_INACTIVE',
                    'version': '5.0'
                }, status=403)
            
            # Enforce single-device for NIP/NIK users (API-only flag)
            try:
                from core.session_utils import should_enforce_single_session_api
                if should_enforce_single_session_api(user):
                    from core.token_blacklist import TokenBlacklist
                    TokenBlacklist.blacklist_all_user_tokens(user.id, reason='login_new_device')
                    # Also mark existing web session as superseded (if any)
                    from core.session_utils import force_single_session
                    force_single_session(user)
            except Exception as _e:
                logger.error(f"Failed to enforce single-device for API login: {_e}")
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            
            # Update last login
            from django.utils import timezone
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            
            # Log login activity to ms_log_data
            try:
                from core.models import MsLogData
                MsLogData.log_login(user, request, via='api_v5')
            except Exception as e:
                logger.error(f"Failed to log login activity: {e}")
            
            # Success response
            return JsonResponse({
                'status': 'success',
                'message': 'Login successful',
                'data': {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'token_type': 'Bearer',
                    'expires_in': 86400,  # 24 hours in seconds
                    'user': {
                        'user_id': user.id,
                        'username': user.username,
                        'name': user.name,
                        'email': user.email or '',
                        'id_pegawai': user.id_pegawai or 0,
                        'is_active': user.is_active
                    }
                },
                'version': '5.0'
            }, status=200)
        else:
            # Log failed login attempt
            try:
                from core.models import MsLogData
                MsLogData.log_login_failed(username, request, via='api_v5', reason='Invalid credentials')
            except Exception as e:
                logger.error(f"Failed to log login failure: {e}")
            
            # Invalid credentials
            return JsonResponse({
                'status': 'error',
                'message': 'Username atau password salah',
                'code': 'INVALID_CREDENTIALS',
                'version': '5.0'
            }, status=401)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON format',
            'code': 'INVALID_JSON',
            'version': '5.0'
        }, status=400)
    except Exception as e:
        logger.error(f"JWT login error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Internal server error',
            'code': 'SERVER_ERROR',
            'version': '5.0'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_jwt_verify_v5(request):
    """
    JWT Token Verification endpoint v5.0
    
    URL: /apiaplikasi-test/5.0/auth/verify
    Method: POST
    Headers:
        Authorization: Bearer <access_token>
    OR Body:
        - token: <access_token>
    
    Response:
        Valid: {
            "status": "success",
            "message": "Token is valid",
            "data": {
                "user_id": 1,
                "username": "username",
                "token_type": "access",
                "exp": 1234567890
            },
            "version": "5.0"
        }
    """
    try:
        # Get token from Authorization header or body
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token_str = auth_header.split(' ')[1]
        else:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                token_str = data.get('token', '')
            else:
                token_str = request.POST.get('token', '')
        
        if not token_str:
            return JsonResponse({
                'status': 'error',
                'message': 'Token tidak ditemukan',
                'code': 'MISSING_TOKEN',
                'version': '5.0'
            }, status=400)
        
        # Verify token
        try:
            token = AccessToken(token_str)
            user_id = token.get('user_id')
            # Blacklist checks
            try:
                from core.token_blacklist import TokenBlacklist
                if TokenBlacklist.is_blacklisted(token_str):
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Token telah dicabut',
                        'code': 'TOKEN_REVOKED',
                        'version': '5.0'
                    }, status=401)
                token_issued_at = token.get('iat')
                if TokenBlacklist.is_user_blacklisted(user_id, token_issued_at):
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Token tidak berlaku (user diblacklist)',
                        'code': 'TOKEN_REVOKED_USER',
                        'version': '5.0'
                    }, status=401)
            except Exception as _e:
                logger.error(f"Blacklist verification error: {_e}")
            
            # Get user
            user = User.objects.get(id=user_id)
            
            return JsonResponse({
                'status': 'success',
                'message': 'Token is valid',
                'data': {
                    'user_id': user.id,
                    'username': user.username,
                    'name': user.name,
                    'email': user.email or '',
                    'token_type': token.get('token_type'),
                    'exp': token.get('exp')
                },
                'version': '5.0'
            }, status=200)
            
        except (TokenError, InvalidToken) as e:
            return JsonResponse({
                'status': 'error',
                'message': 'Token tidak valid atau sudah expired',
                'code': 'INVALID_TOKEN',
                'version': '5.0'
            }, status=401)
        except User.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'User tidak ditemukan',
                'code': 'USER_NOT_FOUND',
                'version': '5.0'
            }, status=404)
            
    except Exception as e:
        logger.error(f"JWT verify error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Internal server error',
            'code': 'SERVER_ERROR',
            'version': '5.0'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_jwt_refresh_v5(request):
    """
    JWT Token Refresh endpoint v5.0
    
    URL: /apiaplikasi-test/5.0/auth/refresh
    Method: POST
    Body (JSON or form-data):
        - refresh_token: <refresh_token>
    
    Response:
        Success: {
            "status": "success",
            "message": "Token refreshed successfully",
            "data": {
                "access_token": "new_access_token",
                "token_type": "Bearer",
                "expires_in": 86400
            },
            "version": "5.0"
        }
    """
    try:
        # Get refresh token from body
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            refresh_token = data.get('refresh_token', '')
        else:
            refresh_token = request.POST.get('refresh_token', '')
        
        if not refresh_token:
            return JsonResponse({
                'status': 'error',
                'message': 'Refresh token harus diisi',
                'code': 'MISSING_REFRESH_TOKEN',
                'version': '5.0'
            }, status=400)
        
        try:
            # Validate and check blacklist
            refresh = RefreshToken(refresh_token)
            user_id = refresh.get('user_id')
            token_issued_at = refresh.get('iat')
            try:
                from core.token_blacklist import TokenBlacklist
                if TokenBlacklist.is_user_blacklisted(user_id, token_issued_at):
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Refresh token ditolak (user diblacklist)',
                        'code': 'REFRESH_REVOKED',
                        'version': '5.0'
                    }, status=401)
            except Exception as _e:
                logger.error(f"Refresh blacklist check failed: {_e}")
            # Issue new access token
            access_token = str(refresh.access_token)
            return JsonResponse({
                'status': 'success',
                'message': 'Token refreshed successfully',
                'data': {
                    'access_token': access_token,
                    'token_type': 'Bearer',
                    'expires_in': 86400
                },
                'version': '5.0'
            }, status=200)
            
        except (TokenError, InvalidToken):
            return JsonResponse({
                'status': 'error',
                'message': 'Refresh token tidak valid atau sudah expired',
                'code': 'INVALID_REFRESH_TOKEN',
                'version': '5.0'
            }, status=401)
            
    except Exception as e:
        logger.error(f"JWT refresh error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Internal server error',
            'code': 'SERVER_ERROR',
            'version': '5.0'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
def api_logout_v5(request):
    """
    Logout endpoint - Blacklist current token
    
    URL: /apiaplikasi-test/5.0/auth/logout
    Method: POST
    Headers:
        Authorization: Bearer <token>  (REQUIRED)
    
    Response:
        Success: {
            "status": "success",
            "message": "Logged out successfully",
            "version": "5.0"
        }
    """
    try:
        from core.token_blacklist import TokenBlacklist
        
        # Get token from request (set by @jwt_required decorator)
        token_str = request.jwt_token
        user = request.jwt_user
        
        # Add token to blacklist
        if TokenBlacklist.add(token_str):
            logger.info(f"User {user.username} logged out. Token blacklisted.")
            return JsonResponse({
                'status': 'success',
                'message': 'Logged out successfully',
                'version': '5.0'
            }, status=200)
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Failed to revoke token',
                'code': 'LOGOUT_FAILED',
                'version': '5.0'
            }, status=500)
            
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Internal server error',
            'code': 'SERVER_ERROR',
            'version': '5.0'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
def api_revoke_all_tokens_v5(request):
    """
    Revoke all tokens for current user
    Useful for: password change, security breach
    
    URL: /apiaplikasi-test/5.0/auth/revoke-all-tokens
    Method: POST
    Headers:
        Authorization: Bearer <token>  (REQUIRED)
    
    Response:
        Success: {
            "status": "success",
            "message": "All tokens revoked",
            "version": "5.0"
        }
    """
    try:
        from core.token_blacklist import TokenBlacklist
        
        user = request.jwt_user
        
        # Blacklist all tokens for this user
        if TokenBlacklist.blacklist_all_user_tokens(user.id, reason="user_revoke_all"):
            logger.info(f"All tokens revoked for user {user.username}")
            return JsonResponse({
                'status': 'success',
                'message': 'All your tokens have been revoked',
                'info': 'You need to login again',
                'version': '5.0'
            }, status=200)
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Failed to revoke all tokens',
                'code': 'REVOKE_FAILED',
                'version': '5.0'
            }, status=500)
            
    except Exception as e:
        logger.error(f"Revoke all tokens error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Internal server error',
            'code': 'SERVER_ERROR',
            'version': '5.0'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
def api_revoke_by_username_v5(request):
    """
    Revoke all tokens for a specific user (by username)
    Admin action: Revoke tokens for another user
    
    URL: /apiaplikasi-test/5.0/auth/revoke-by-username
    Method: POST
    Headers:
        Authorization: Bearer <token>  (REQUIRED)
    Body (JSON or form-data):
        - username: Username to revoke
        - reason: Reason for revocation (optional)
    
    Response:
        Success: {
            "status": "success",
            "message": "All tokens for user 'username' have been revoked",
            "version": "5.0"
        }
    """
    try:
        from core.token_blacklist import TokenBlacklist
        
        # Get requesting user (from @jwt_required)
        admin_user = request.jwt_user
        
        # Get target username from request
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                target_username = data.get('username', '').strip()
                reason = data.get('reason', 'admin_revoke')
            except json.JSONDecodeError:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid JSON format',
                    'code': 'INVALID_JSON',
                    'version': '5.0'
                }, status=400)
        else:
            target_username = request.POST.get('username', '').strip()
            reason = request.POST.get('reason', 'admin_revoke')
        
        # Validation
        if not target_username:
            return JsonResponse({
                'status': 'error',
                'message': 'Username is required',
                'code': 'MISSING_USERNAME',
                'version': '5.0'
            }, status=400)
        
        # Find target user
        try:
            target_user = User.objects.get(username=target_username)
        except User.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': f'User "{target_username}" not found',
                'code': 'USER_NOT_FOUND',
                'version': '5.0'
            }, status=404)
        
        # Prevent self-revoke (use /auth/revoke-all-tokens instead)
        if target_user.id == admin_user.id:
            return JsonResponse({
                'status': 'error',
                'message': 'Cannot revoke your own tokens. Use /auth/revoke-all-tokens instead',
                'code': 'SELF_REVOKE_NOT_ALLOWED',
                'version': '5.0'
            }, status=400)
        
        # Revoke all tokens for target user
        if TokenBlacklist.blacklist_all_user_tokens(target_user.id, reason=reason):
            logger.info(f"User {admin_user.username} revoked all tokens for user {target_username}. Reason: {reason}")
            return JsonResponse({
                'status': 'success',
                'message': f'All tokens for user "{target_username}" have been revoked',
                'info': {
                    'target_user': target_username,
                    'target_user_id': target_user.id,
                    'revoked_by': admin_user.username,
                    'reason': reason
                },
                'version': '5.0'
            }, status=200)
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Failed to revoke tokens',
                'code': 'REVOKE_FAILED',
                'version': '5.0'
            }, status=500)
    
    except Exception as e:
        logger.error(f"Admin revoke user tokens error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Internal server error',
            'code': 'SERVER_ERROR',
            'version': '5.0'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_logout_v4(request):
    """
    Logout endpoint v4.0 (Laravel compatible)
    Log logout to ms_log_data
    
    URL: /apiaplikasi-test/4.0/logout
    Method: POST
    Headers: Authorization: Bearer <token>
    
    Response:
        {
            "data": {
                "message": "Logout successful"
            },
            "success_message": "Logout berhasil",
            "errors": [],
            "error_message": null
        }
    """
    try:
        # Get token from header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return JsonResponse({
                'data': None,
                'success_message': '',
                'errors': ['Token tidak ditemukan'],
                'error_message': 'Token tidak ditemukan'
            }, status=401)
        
        token = auth_header.split(' ')[1]
        
        # Verify token and get user
        try:
            from rest_framework_simplejwt.tokens import AccessToken
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            user = User.objects.get(id=user_id)
        except Exception:
            return JsonResponse({
                'data': None,
                'success_message': '',
                'errors': ['Token tidak valid'],
                'error_message': 'Token tidak valid'
            }, status=401)
        
        # Log logout to ms_log_data
        try:
            MsLogData.log_logout(
                user=user,
                request=request,
                via='api_v4',
                description='Manual logout via API v4.0'
            )
        except Exception as e:
            logger.error(f"Failed to log logout: {e}")
        
        # Blacklist token
        try:
            TokenBlacklist.blacklist_token(token, reason='User logout')
        except Exception as e:
            logger.warning(f"Failed to blacklist token: {e}")
        
        return JsonResponse({
            'data': {
                'message': 'Logout successful',
                'username': user.username
            },
            'success_message': 'Logout berhasil',
            'errors': [],
            'error_message': None
        }, status=200)
        
    except Exception as e:
        logger.error(f"Logout v4 error: {str(e)}")
        return JsonResponse({
            'data': None,
            'success_message': '',
            'errors': ['Server error'],
            'error_message': 'Server error'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_logout_v5(request):
    """
    Logout endpoint v5.0
    Log logout to ms_log_data
    
    URL: /apiaplikasi-test/5.0/auth/logout
    Method: POST
    Headers: Authorization: Bearer <token>
    
    Response:
        {
            "status": "success",
            "message": "Logout successful",
            "data": {
                "username": "user@example.com"
            },
            "version": "5.0"
        }
    """
    try:
        # Get token from header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return JsonResponse({
                'status': 'error',
                'message': 'Token tidak ditemukan',
                'code': 'TOKEN_MISSING',
                'version': '5.0'
            }, status=401)
        
        token = auth_header.split(' ')[1]
        
        # Verify token and get user
        try:
            from rest_framework_simplejwt.tokens import AccessToken
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            user = User.objects.get(id=user_id)
        except Exception:
            return JsonResponse({
                'status': 'error',
                'message': 'Token tidak valid atau sudah expired',
                'code': 'INVALID_TOKEN',
                'version': '5.0'
            }, status=401)
        
        # Log logout to ms_log_data
        try:
            MsLogData.log_logout(
                user=user,
                request=request,
                via='api_v5',
                description='Manual logout via API v5.0'
            )
        except Exception as e:
            logger.error(f"Failed to log logout: {e}")
        
        # Blacklist token
        try:
            TokenBlacklist.blacklist_token(token, reason='User logout')
        except Exception as e:
            logger.warning(f"Failed to blacklist token: {e}")
        
        return JsonResponse({
            'status': 'success',
            'message': 'Logout successful',
            'data': {
                'username': user.username,
                'logout_at': timezone.now().isoformat()
            },
            'version': '5.0'
        }, status=200)
        
    except Exception as e:
        logger.error(f"Logout v5 error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Internal server error',
            'code': 'SERVER_ERROR',
            'version': '5.0'
        }, status=500)
            
    except Exception as e:
        logger.error(f"Revoke by username error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Internal server error',
            'code': 'SERVER_ERROR',
            'version': '5.0'
        }, status=500)
