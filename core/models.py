"""
Core models
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class APIAccessLog(models.Model):
    """
    Log API access for monitoring, analytics, and security
    Only logs IMPORTANT events (not all requests)
    """
    
    # Request Information
    method = models.CharField(max_length=10)
    endpoint = models.CharField(max_length=500, db_index=True)
    full_url = models.TextField(null=True, blank=True)
    
    # User Information
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    username = models.CharField(max_length=150, null=True, blank=True)
    
    # Request Details
    ip_address = models.CharField(max_length=45, db_index=True)
    user_agent = models.TextField(null=True, blank=True)
    request_headers = models.JSONField(null=True, blank=True)
    request_body = models.JSONField(null=True, blank=True)
    query_params = models.JSONField(null=True, blank=True)
    
    # Response Details
    status_code = models.SmallIntegerField(db_index=True)
    response_size = models.IntegerField(null=True, blank=True)
    response_time = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    
    # Additional Info
    api_version = models.CharField(max_length=10, null=True, blank=True)
    rate_limit_hit = models.BooleanField(default=False)
    error_message = models.TextField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'ms_log_api'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['method', 'endpoint']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.method} {self.endpoint} - {self.status_code}"


class MsLogData(models.Model):
    """
    Hybrid Audit Trail - Simple & Flexible
    Tracks:
    1. Login activities (web, API v4.0, API v5.0)
    2. Data changes (create, update, delete)
    """
    
    # Target info
    table_name = models.CharField(max_length=191, db_index=True, help_text='Target table (users, pegawai, etc)')
    record_id = models.IntegerField(null=True, blank=True, help_text='ID of affected record')
    
    # Action type
    action = models.CharField(max_length=191, db_index=True, help_text='login, logout, create, update, delete')
    
    # User info
    user_id = models.IntegerField(null=True, blank=True, db_index=True, help_text='User who performed action')
    username = models.CharField(max_length=191, null=True, blank=True, help_text='Username for quick reference')
    
    # Data snapshots (JSON - flexible!)
    old_data = models.JSONField(null=True, blank=True, help_text='Data before change (for update/delete)')
    new_data = models.JSONField(null=True, blank=True, help_text='Data after change (for create/update)')
    
    # Client info
    ip_address = models.CharField(max_length=45, null=True, blank=True, db_index=True, help_text='Client IP address')
    user_agent = models.TextField(null=True, blank=True, help_text='Browser/client user agent')
    
    # Meta info (flexible!)
    via = models.CharField(max_length=50, null=True, blank=True, db_index=True, help_text='web, api_v4, api_v5')
    description = models.CharField(max_length=255, null=True, blank=True, help_text='Additional description')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ms_log_data'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_id', 'created_at']),
            models.Index(fields=['action', 'table_name']),
            models.Index(fields=['via', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.action} on {self.table_name} by {self.username or self.user_id} via {self.via}"
    
    @classmethod
    def log_login(cls, user, request, via='web', description=None):
        """
        Log successful user login
        
        Args:
            user: User instance
            request: Django request object
            via: 'web', 'api_v4', 'api_v5'
            description: Optional description
        """
        from core.middleware.api_logging import get_client_ip
        
        return cls.objects.create(
            table_name='users',
            record_id=user.id if user else None,
            action='login',
            user_id=user.id if user else None,
            username=user.username if user else None,
            old_data=None,
            new_data={
                'login_time': str(request.META.get('HTTP_DATE', '')),
                'user_data': {
                    'id': user.id,
                    'name': user.name if hasattr(user, 'name') else user.username,
                    'email': user.email if user.email else ''
                }
            },
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:1000],
            via=via,
            description=description or f'Login via {via}'
        )
    
    @classmethod
    def log_login_failed(cls, username, request, via='web', reason='', description=None):
        """
        Log failed login attempt
        
        Args:
            username: Attempted username
            request: Django request object
            via: 'web', 'api_v4', 'api_v5'
            reason: Failure reason
            description: Optional description
        """
        from core.middleware.api_logging import get_client_ip
        
        return cls.objects.create(
            table_name='users',
            record_id=None,
            action='login_failed',
            user_id=None,
            username=username,
            old_data={
                'attempted_username': username,
                'reason': reason
            },
            new_data=None,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:1000],
            via=via,
            description=description or f'Failed login attempt via {via}'
        )
    
    @classmethod
    def log_logout(cls, user, request, via='web', description=None):
        """
        Log user logout
        
        Args:
            user: User instance
            request: Django request object
            via: 'web', 'api_v4', 'api_v5'
            description: Optional description
        """
        from core.middleware.api_logging import get_client_ip
        
        return cls.objects.create(
            table_name='users',
            record_id=user.id if user else None,
            action='logout',
            user_id=user.id if user else None,
            username=user.username if user else None,
            old_data={
                'logout_time': str(request.META.get('HTTP_DATE', ''))
            },
            new_data=None,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:1000],
            via=via,
            description=description or f'Logout via {via}'
        )
    
    @classmethod
    def log_create(cls, user, instance, request=None, via='web', description=None):
        """
        Log data creation
        
        Args:
            user: User instance
            instance: Created instance
            request: Django request object (optional)
            via: 'web', 'api_v4', 'api_v5'
            description: Optional description
        """
        from core.middleware.api_logging import get_client_ip
        
        return cls.objects.create(
            table_name=instance._meta.db_table,
            record_id=instance.id,
            action='create',
            user_id=user.id if user else None,
            username=user.username if user else None,
            old_data=None,
            new_data={
                'data': instance.__dict__
            },
            ip_address=get_client_ip(request) if request else None,
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:1000] if request else None,
            via=via,
            description=description or f'Create {instance._meta.db_table} record'
        )
    
    @classmethod
    def log_update(cls, user, instance, old_data, request=None, via='web', description=None):
        """
        Log data update
        
        Args:
            user: User instance
            instance: Updated instance
            old_data: Data before update (dict)
            request: Django request object (optional)
            via: 'web', 'api_v4', 'api_v5'
            description: Optional description
        """
        from core.middleware.api_logging import get_client_ip
        
        return cls.objects.create(
            table_name=instance._meta.db_table,
            record_id=instance.id,
            action='update',
            user_id=user.id if user else None,
            username=user.username if user else None,
            old_data=old_data,
            new_data={
                'data': instance.__dict__
            },
            ip_address=get_client_ip(request) if request else None,
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:1000] if request else None,
            via=via,
            description=description or f'Update {instance._meta.db_table} record'
        )
    
    @classmethod
    def log_delete(cls, user, instance, request=None, via='web', description=None):
        """
        Log data deletion
        
        Args:
            user: User instance
            instance: Deleted instance
            request: Django request object (optional)
            via: 'web', 'api_v4', 'api_v5'
            description: Optional description
        """
        from core.middleware.api_logging import get_client_ip
        
        return cls.objects.create(
            table_name=instance._meta.db_table,
            record_id=instance.id,
            action='delete',
            user_id=user.id if user else None,
            username=user.username if user else None,
            old_data={
                'data': instance.__dict__
            },
            new_data=None,
            ip_address=get_client_ip(request) if request else None,
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:1000] if request else None,
            via=via,
            description=description or f'Delete {instance._meta.db_table} record'
        )
    
    @classmethod
    def log_system(cls, action, table_name='system', record_id=None, user=None, request=None, via='system', description=None):
        """
        Log error/exception untuk debugging dan monitoring
        
        Args:
            user: User instance (atau None jika tidak ada user context)
            action: Action yang error (e.g., 'password_change', 'login', 'data_update')
            error_message: Error message (string)
            error_details: Error details (dict) - bisa include traceback, params, dll
            request: Django request object (optional)
            via: 'web', 'api_v4', 'api_v5', 'system'
            description: Optional description
        """
        from core.middleware.api_logging import get_client_ip
        
        return cls.objects.create(
            table_name='system',
            record_id=user.id if user else None,
            action=f'{action}_error',
            user_id=user.id if user else None,
            username=user.username if user else None,
            old_data={
                'error_message': error_message,
                'error_details': error_details or {}
            },
            new_data=None,
            ip_address=get_client_ip(request) if request else None,
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:1000] if request else None,
            via=via,
            description=description or f'Error: {action} - {error_message[:100]}'
        )
