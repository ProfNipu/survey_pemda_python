"""
Custom middleware untuk session management
"""
from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
import time
from core.session_utils import should_enforce_single_session_web, track_user_session


class SessionInactivityMiddleware:
    """
    Middleware untuk auto-logout user jika inactive
    Track last activity time dan logout jika melebihi timeout
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Get timeout dari settings (default: 30 minutes)
        self.timeout = getattr(settings, 'SESSION_INACTIVITY_TIMEOUT', 1800)
    
    def __call__(self, request):
        # Skip untuk anonymous users
        if request.user.is_authenticated:
            # Get current time
            current_time = time.time()
            
            # Get last activity time dari session
            last_activity = request.session.get('last_activity')
            
            if last_activity:
                # Calculate inactive time
                inactive_time = current_time - last_activity
                
                # Check if user has been inactive too long
                if inactive_time > self.timeout:
                    # Logout user
                    logout(request)
                    # Set logout reason di session (untuk message)
                    request.session['logout_reason'] = 'inactivity'
            
            # Update last activity time
            request.session['last_activity'] = current_time
            try:
                if should_enforce_single_session_web(request.user):
                    session_key = getattr(request.session, 'session_key', None)
                    if session_key:
                        track_user_session(request.user, session_key)
            except Exception:
                pass
        
        response = self.get_response(request)
        return response


