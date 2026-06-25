"""
API Access Log Model
Track all API requests for monitoring and analytics
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class APIAccessLog(models.Model):
    """
    Log all API access for monitoring, analytics, and security
    
    Usage:
        APIAccessLog.objects.create(
            method='GET',
            endpoint='/apiaplikasi-test/5.0/users/list',
            user=request.user,
            ip_address=get_client_ip(request),
            status_code=200,
            response_time=0.245
        )
    """
    
    # Request Information
    method = models.CharField(
        max_length=10,
        verbose_name='HTTP Method',
        help_text='GET, POST, PUT, DELETE, etc'
    )
    endpoint = models.CharField(
        max_length=500,
        db_index=True,
        verbose_name='API Endpoint',
        help_text='e.g., /apiaplikasi-test/5.0/users/list'
    )
    full_url = models.TextField(
        null=True,
        blank=True,
        verbose_name='Full URL',
        help_text='Complete URL with query parameters'
    )
    
    # User Information
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='User',
        help_text='User who made the request (NULL for unauthenticated)'
    )
    username = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        verbose_name='Username',
        help_text='Username for quick reference'
    )
    
    # Request Details
    ip_address = models.CharField(
        max_length=45,
        db_index=True,
        verbose_name='IP Address',
        help_text='IPv4 or IPv6 address'
    )
    user_agent = models.TextField(
        null=True,
        blank=True,
        verbose_name='User Agent',
        help_text='Browser or client information'
    )
    request_headers = models.JSONField(
        null=True,
        blank=True,
        verbose_name='Request Headers',
        help_text='HTTP request headers (selective)'
    )
    request_body = models.JSONField(
        null=True,
        blank=True,
        verbose_name='Request Body',
        help_text='POST/PUT request body (limited size)'
    )
    query_params = models.JSONField(
        null=True,
        blank=True,
        verbose_name='Query Parameters',
        help_text='GET query parameters'
    )
    
    # Response Details
    status_code = models.SmallIntegerField(
        db_index=True,
        verbose_name='Status Code',
        help_text='HTTP status code (200, 401, 500, etc)'
    )
    response_size = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Response Size (bytes)',
        help_text='Size of response body in bytes'
    )
    response_time = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name='Response Time (seconds)',
        help_text='Time taken to process request in seconds'
    )
    
    # Additional Info
    api_version = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name='API Version',
        help_text='API version (4.0, 5.0, etc)'
    )
    rate_limit_hit = models.BooleanField(
        default=False,
        verbose_name='Rate Limit Hit',
        help_text='Whether this request hit rate limit'
    )
    error_message = models.TextField(
        null=True,
        blank=True,
        verbose_name='Error Message',
        help_text='Error message if request failed'
    )
    
    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Created At'
    )
    
    class Meta:
        db_table = 'api_access_log'
        verbose_name = 'API Access Log'
        verbose_name_plural = 'API Access Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['method', 'endpoint'], name='api_log_method_endpoint_idx'),
            models.Index(fields=['created_at'], name='api_log_created_at_idx'),
            models.Index(fields=['user', 'created_at'], name='api_log_user_created_idx'),
        ]
    
    def __str__(self):
        return f"{self.method} {self.endpoint} - {self.status_code} ({self.created_at})"
    
    def __repr__(self):
        return f"<APIAccessLog: {self.method} {self.endpoint} [{self.status_code}]>"
    
    @property
    def is_success(self):
        """Check if request was successful (2xx status code)"""
        return 200 <= self.status_code < 300
    
    @property
    def is_client_error(self):
        """Check if request had client error (4xx status code)"""
        return 400 <= self.status_code < 500
    
    @property
    def is_server_error(self):
        """Check if request had server error (5xx status code)"""
        return self.status_code >= 500
    
    @property
    def is_slow(self, threshold=1.0):
        """Check if request was slow (> threshold seconds)"""
        return self.response_time and float(self.response_time) > threshold
    
    @classmethod
    def get_stats_today(cls):
        """Get statistics for today"""
        from django.db.models import Count, Avg, Max, Min
        from django.utils import timezone
        from datetime import datetime
        
        today = timezone.now().date()
        return cls.objects.filter(
            created_at__date=today
        ).aggregate(
            total_requests=Count('id'),
            successful_requests=Count('id', filter=models.Q(status_code__lt=400)),
            failed_requests=Count('id', filter=models.Q(status_code__gte=400)),
            avg_response_time=Avg('response_time'),
            max_response_time=Max('response_time'),
            min_response_time=Min('response_time'),
        )
    
    @classmethod
    def get_top_endpoints(cls, limit=10, days=7):
        """Get most hit endpoints in last N days"""
        from django.db.models import Count
        from django.utils import timezone
        from datetime import timedelta
        
        since = timezone.now() - timedelta(days=days)
        return cls.objects.filter(
            created_at__gte=since
        ).values('endpoint').annotate(
            hit_count=Count('id')
        ).order_by('-hit_count')[:limit]
    
    @classmethod
    def get_top_users(cls, limit=10, days=7):
        """Get most active users in last N days"""
        from django.db.models import Count
        from django.utils import timezone
        from datetime import timedelta
        
        since = timezone.now() - timedelta(days=days)
        return cls.objects.filter(
            created_at__gte=since,
            user__isnull=False
        ).values('username', 'user__email').annotate(
            request_count=Count('id')
        ).order_by('-request_count')[:limit]
