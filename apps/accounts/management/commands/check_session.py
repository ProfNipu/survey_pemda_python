"""
Management command to check session data
Usage: python manage.py check_session <session_key>
"""
from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session
from datetime import datetime


class Command(BaseCommand):
    help = 'Check session data for debugging'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Show all active sessions',
        )
        parser.add_argument(
            'session_key',
            nargs='?',
            type=str,
            help='Session key to check'
        )
    
    def handle(self, *args, **options):
        if options['all']:
            # Show all active sessions
            sessions = Session.objects.filter(expire_date__gte=datetime.now())
            self.stdout.write(f"\n{'='*80}")
            self.stdout.write(f"Active Sessions: {sessions.count()}")
            self.stdout.write(f"{'='*80}\n")
            
            for session in sessions:
                data = session.get_decoded()
                last_activity = data.get('last_activity', 'N/A')
                
                if last_activity != 'N/A':
                    last_activity_dt = datetime.fromtimestamp(last_activity)
                    inactive_time = (datetime.now() - last_activity_dt).total_seconds()
                    inactive_min = int(inactive_time / 60)
                else:
                    inactive_min = 'N/A'
                
                self.stdout.write(f"\nSession Key: {session.session_key}")
                self.stdout.write(f"User ID: {data.get('_auth_user_id', 'Anonymous')}")
                self.stdout.write(f"Last Activity: {last_activity}")
                self.stdout.write(f"Inactive Time: {inactive_min} minutes")
                self.stdout.write(f"Expire Date: {session.expire_date}")
                self.stdout.write(f"{'-'*80}")
        
        elif options['session_key']:
            # Show specific session
            try:
                session = Session.objects.get(session_key=options['session_key'])
                data = session.get_decoded()
                
                self.stdout.write(f"\n{'='*80}")
                self.stdout.write(f"Session Details")
                self.stdout.write(f"{'='*80}\n")
                self.stdout.write(f"Session Key: {session.session_key}")
                self.stdout.write(f"Expire Date: {session.expire_date}")
                self.stdout.write(f"\nDecoded Data:")
                self.stdout.write(f"{'-'*80}")
                
                for key, value in data.items():
                    if key == 'last_activity':
                        dt = datetime.fromtimestamp(value)
                        self.stdout.write(f"{key}: {value} ({dt})")
                    else:
                        self.stdout.write(f"{key}: {value}")
                
                self.stdout.write(f"\n{'='*80}\n")
                
            except Session.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Session not found: {options['session_key']}"))
        
        else:
            self.stdout.write(self.style.ERROR("Please provide --all or session_key"))
