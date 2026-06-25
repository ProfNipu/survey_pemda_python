"""
Management command to check Redis session data
Usage: python manage.py check_redis_sessions
"""
from django.core.management.base import BaseCommand
from django.core.cache import cache
from django_redis import get_redis_connection
import json


class Command(BaseCommand):
    help = 'Check Redis session data and statistics'
    
    def handle(self, *args, **options):
        try:
            # Get Redis connection
            redis_conn = get_redis_connection("default")
            
            # Get all keys
            all_keys = redis_conn.keys("*")
            session_keys = [k.decode() for k in all_keys if b'session' in k.lower()]
            
            self.stdout.write(f"\n{'='*80}")
            self.stdout.write(f"Redis Session Statistics")
            self.stdout.write(f"{'='*80}\n")
            
            self.stdout.write(f"Redis Host: {redis_conn.connection_pool.connection_kwargs.get('host')}")
            self.stdout.write(f"Redis Port: {redis_conn.connection_pool.connection_kwargs.get('port')}")
            self.stdout.write(f"Redis DB: {redis_conn.connection_pool.connection_kwargs.get('db')}")
            self.stdout.write(f"\nTotal Redis Keys: {len(all_keys)}")
            self.stdout.write(f"Session Keys: {len(session_keys)}")
            
            if session_keys:
                self.stdout.write(f"\n{'-'*80}")
                self.stdout.write("Session Keys:")
                self.stdout.write(f"{'-'*80}")
                for key in session_keys[:10]:  # Show first 10
                    ttl = redis_conn.ttl(key)
                    ttl_min = ttl // 60 if ttl > 0 else 0
                    self.stdout.write(f"\nKey: {key}")
                    self.stdout.write(f"TTL: {ttl_min} minutes ({ttl} seconds)")
                    
                    # Try to get value
                    try:
                        value = redis_conn.get(key)
                        if value:
                            self.stdout.write(f"Size: {len(value)} bytes")
                    except:
                        pass
            
            # Test cache operations
            self.stdout.write(f"\n{'='*80}")
            self.stdout.write("Testing Cache Operations:")
            self.stdout.write(f"{'='*80}\n")
            
            # Set test key
            test_key = 'test_session_check'
            test_value = {'user_id': 1, 'username': 'test', 'last_activity': 'now'}
            cache.set(test_key, test_value, 60)
            
            # Get test key
            retrieved = cache.get(test_key)
            
            if retrieved == test_value:
                self.stdout.write(self.style.SUCCESS("✅ Cache SET/GET: WORKING"))
            else:
                self.stdout.write(self.style.ERROR("❌ Cache SET/GET: FAILED"))
            
            # Delete test key
            cache.delete(test_key)
            
            # Check info
            info = redis_conn.info()
            self.stdout.write(f"\nRedis Version: {info.get('redis_version')}")
            self.stdout.write(f"Used Memory: {info.get('used_memory_human')}")
            self.stdout.write(f"Connected Clients: {info.get('connected_clients')}")
            self.stdout.write(f"Total Connections: {info.get('total_connections_received')}")
            self.stdout.write(f"Total Commands: {info.get('total_commands_processed')}")
            
            self.stdout.write(f"\n{'='*80}\n")
            self.stdout.write(self.style.SUCCESS("✅ Redis Connection: HEALTHY"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error connecting to Redis: {str(e)}"))
