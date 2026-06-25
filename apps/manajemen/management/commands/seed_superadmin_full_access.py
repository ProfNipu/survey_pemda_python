"""Ensure Super Admin group has full access.

Assigns all existing PermissionRule rows to the configured Super Admin group(s).
This avoids relying on PERMISSIONS_SUPERADMIN_OVERRIDE and makes permissions explicit.

Usage:
  python manage.py seed_superadmin_full_access
  python manage.py seed_superadmin_full_access --group "Super Admin"
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import Group

from apps.manajemen.models import PermissionRule, RoleRule


class Command(BaseCommand):
    help = 'Assign ALL PermissionRule to Super Admin group(s)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--group',
            default=None,
            help='Override group name (default uses settings.SUPERADMIN_GROUPS or "Super Admin")',
        )

    def handle(self, *args, **options):
        override_group = options.get('group')
        if override_group:
            group_names = [str(override_group)]
        else:
            group_names = getattr(settings, 'SUPERADMIN_GROUPS', ['Super Admin'])
            if not isinstance(group_names, (list, tuple)):
                group_names = [str(group_names)]

        rules = PermissionRule.objects.filter(is_active=True)
        if not rules.exists():
            self.stdout.write(self.style.WARNING('No PermissionRule found. Run seed_core_setup first.'))
            return

        total_assigned = 0
        for gname in group_names:
            grp, _ = Group.objects.get_or_create(name=gname)
            for rule in rules.iterator(chunk_size=500):
                _, created = RoleRule.objects.get_or_create(role=grp, rule=rule)
                total_assigned += int(created)

        self.stdout.write(self.style.SUCCESS(f'✅ Super Admin full access assigned. New assignments: {total_assigned}'))
