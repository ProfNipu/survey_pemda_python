"""
Webhook handlers for password sync from ESIMPEG
"""
import hmac
import hashlib
import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone

User = get_user_model()
logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def handle_password_changed(request):
    """
    Webhook endpoint untuk menerima notifikasi password change dari ESIMPEG
    
    Expected payload:
    {
        "username": "prakom@admin.com",
        "password_hash": "pbkdf2_sha256$...",
        "changed_at": "2026-03-30T10:00:00Z",
        "changed_by": "user_id"
    }
    
    Headers:
    - X-Webhook-Signature: HMAC SHA256 signature
    """
    try:
        # 1. Validate signature
        signature = request.headers.get('X-Webhook-Signature', '')
        secret_key = settings.ESIMPEG_WEBHOOK_SECRET
        
        if not secret_key:
            logger.error("ESIMPEG_WEBHOOK_SECRET not configured")
            return JsonResponse({
                'status': 'error',
                'message': 'Webhook secret not configured'
            }, status=500)
        
        # Calculate expected signature
        payload = request.body
        expected_signature = hmac.new(
            secret_key.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures (constant time comparison)
        if not hmac.compare_digest(signature, expected_signature):
            logger.warning(f"Invalid webhook signature from {request.META.get('REMOTE_ADDR')}")
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid signature'
            }, status=403)
        
        # 2. Parse payload
        try:
            data = json.loads(payload.decode('utf-8'))
        except json.JSONDecodeError:
            logger.error("Invalid JSON payload")
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON'
            }, status=400)
        
        # 3. Validate required fields
        username = data.get('username')
        password_hash = data.get('password_hash')
        
        if not username or not password_hash:
            logger.error("Missing required fields: username or password_hash")
            return JsonResponse({
                'status': 'error',
                'message': 'Missing required fields'
            }, status=400)
        
        # 4. Find user
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            logger.warning(f"User not found: {username}")
            return JsonResponse({
                'status': 'error',
                'message': 'User not found'
            }, status=404)
        
        # 5. Update password (already hashed from ESIMPEG)
        user.password = password_hash
        user.save(update_fields=['password'])
        
        # 6. Log success
        logger.info(f"Password synced successfully for user: {username}")
        
        # 7. Log to ms_log_data
        try:
            from core.models import MsLogData
            MsLogData.objects.create(
                user_id=user.id,
                action='password_sync',
                table_name='users',
                record_id=user.id,
                old_data={'note': 'Password synced from ESIMPEG via webhook'},
                new_data={
                    'success': True,
                    'via': 'webhook',
                    'changed_at': data.get('changed_at'),
                    'changed_by': data.get('changed_by')
                },
                ip_address=request.META.get('REMOTE_ADDR', ''),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        except Exception as log_err:
            logger.error(f"Failed to log password sync: {log_err}")
        
        return JsonResponse({
            'status': 'success',
            'message': 'Password synced successfully',
            'username': username,
            'synced_at': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': 'Internal server error'
        }, status=500)
