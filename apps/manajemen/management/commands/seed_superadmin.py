"""
Seed Super Admin user by adding to Super Admin group (group-based superadmin)
Usage:
    python manage.py seed_superadmin --user EMAIL_OR_USERNAME [--group "Super Admin"]
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = 'Add a user to Super Admin group (group-based superadmin)'

    def add_arguments(self, parser):
        parser.add_argument('--user', required=True, help='Email or username of the user')
        parser.add_argument('--group', default='Super Admin', help='Super admin group name (default: Super Admin)')

    def handle(self, *args, **options):
        user_key = options['user']
        group_name = options['group']
        U = get_user_model()
        u = U.objects.filter(email=user_key).first() or U.objects.filter(username=user_key).first()
        if not u:
            self.stderr.write(self.style.ERROR(f'User not found: {user_key}'))
            return

        g, _ = Group.objects.get_or_create(name=group_name)
        u.groups.add(g)
        self.stdout.write(self.style.SUCCESS(f'✓ Added {u.username} to group: {g.name}'))
        self.stdout.write(self.style.SUCCESS('✅ Superadmin seeding completed.'))
