# Generated migration for API Access Log table
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='APIAccessLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                
                # Request Information
                ('method', models.CharField(max_length=10, verbose_name='HTTP Method')),
                ('endpoint', models.CharField(max_length=500, db_index=True, verbose_name='API Endpoint')),
                ('full_url', models.TextField(blank=True, null=True, verbose_name='Full URL')),
                
                # User Information
                ('username', models.CharField(max_length=150, blank=True, null=True, verbose_name='Username')),
                
                # Request Details
                ('ip_address', models.CharField(max_length=45, db_index=True, verbose_name='IP Address')),
                ('user_agent', models.TextField(blank=True, null=True, verbose_name='User Agent')),
                ('request_headers', models.JSONField(blank=True, null=True, verbose_name='Request Headers')),
                ('request_body', models.JSONField(blank=True, null=True, verbose_name='Request Body')),
                ('query_params', models.JSONField(blank=True, null=True, verbose_name='Query Parameters')),
                
                # Response Details
                ('status_code', models.SmallIntegerField(db_index=True, verbose_name='Status Code')),
                ('response_size', models.IntegerField(blank=True, null=True, verbose_name='Response Size (bytes)')),
                ('response_time', models.DecimalField(blank=True, decimal_places=3, max_digits=8, null=True, verbose_name='Response Time (seconds)')),
                
                # Additional Info
                ('api_version', models.CharField(blank=True, max_length=10, null=True, verbose_name='API Version')),
                ('rate_limit_hit', models.BooleanField(default=False, verbose_name='Rate Limit Hit')),
                ('error_message', models.TextField(blank=True, null=True, verbose_name='Error Message')),
                
                # Metadata
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Created At')),
                
                # Foreign Key
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, 
                                          to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'API Access Log',
                'verbose_name_plural': 'API Access Logs',
                'db_table': 'api_access_log',
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['method', 'endpoint'], name='api_log_method_endpoint_idx'),
                    models.Index(fields=['created_at'], name='api_log_created_at_idx'),
                    models.Index(fields=['user', 'created_at'], name='api_log_user_created_idx'),
                ],
            },
        ),
    ]
