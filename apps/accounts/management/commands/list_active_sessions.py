"""
Management command to list all active user sessions
Usage: python manage.py list_active_sessions
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django_redis import get_redis_connection
from django.conf import settings

User = get_user_model()


class Command(BaseCommand):
    help = 'List all active user sessions'
    
    def handle(self, *args, **options):
        try:
            redis_conn = get_redis_connection("default")
            
            self.stdout.write(f"\n{'='*80}")
            self.stdout.write(f"Active User Sessions")
            self.stdout.write(f"{'='*80}\n")
            
            # Get all user session tracking keys
            key_prefix = getattr(settings, 'APP_KEY_PREFIX', 'aplikasi-test')
            user_session_keys = redis_conn.keys(f"{key_prefix}:user_session:*")
            
            if not user_session_keys:
                self.stdout.write(self.style.WARNING("No active sessions found."))
                return
            
            self.stdout.write(f"Total Active Users: {len(user_session_keys)}\n")
            self.stdout.write(f"{'-'*80}")
            
            for key in user_session_keys:
                # Extract user ID from key
                user_id = key.decode().split(':')[-1]
                
                try:
                    user = User.objects.get(id=user_id)
                    session_key = redis_conn.get(key)
                    
                    if session_key:
                        session_key = session_key.decode()
                        ttl = redis_conn.ttl(key)
                        ttl_min = ttl // 60 if ttl > 0 else 0
                        
                        self.stdout.write(f"\nUser ID: {user.id}")
                        self.stdout.write(f"Username: {user.username}")
                        self.stdout.write(f"Name: {user.name}")
                        self.stdout.write(f"Session Key: {session_key[-20:]}")  # Last 20 chars
                        self.stdout.write(f"TTL: {ttl_min} minutes ({ttl} seconds)")
                        
                        # Check if actual session exists
                        session_exists = redis_conn.exists(session_key)
                        if session_exists:
                            self.stdout.write(self.style.SUCCESS("Status: ✅ Active"))
                        else:
                            self.stdout.write(self.style.ERROR("Status: ❌ Expired"))
                        
                except User.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"\nUser ID {user_id}: Not found in database"))
            
            self.stdout.write(f"\n{'='*80}\n")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
