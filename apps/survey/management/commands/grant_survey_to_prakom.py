from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from apps.manajemen.models import PermissionModule, PermissionRule, RoleRule

User = get_user_model()


class Command(BaseCommand):
    help = 'Grant survey permissions to prakom user groups'

    def handle(self, *args, **options):
        self.stdout.write('=' * 70)
        self.stdout.write('🔑 Granting Survey Permissions to Prakom')
        self.stdout.write('=' * 70)

        # 1. Find prakom users
        self.stdout.write('\n1. Finding prakom users...')
        prakom_users = User.objects.filter(username__icontains='prakom')
        
        if not prakom_users.exists():
            self.stdout.write('  ✗ No prakom user found')
            return
        
        for user in prakom_users:
            self.stdout.write(f'  ✓ Found: {user.username} ({user.email})')
            self.stdout.write(f'    is_superuser: {user.is_superuser}')
            groups = user.groups.all()
            if groups.exists():
                self.stdout.write(f'    Groups: {", ".join([g.name for g in groups])}')
            else:
                self.stdout.write(f'    Groups: None')

        # 2. Get survey module
        self.stdout.write('\n2. Getting survey permissions...')
        survey_module = PermissionModule.objects.filter(nama_module='survey').first()
        
        if not survey_module:
            self.stdout.write('  ✗ Survey module not found')
            return
        
        survey_rules = PermissionRule.objects.filter(module=survey_module)
        self.stdout.write(f'  ✓ Found {survey_rules.count()} survey permission rules')

        # 3. Assign permissions to all prakom user groups
        self.stdout.write('\n3. Assigning permissions...')
        total_assigned = 0
        
        for user in prakom_users:
            user_groups = user.groups.all()
            
            if not user_groups.exists():
                self.stdout.write(f'  ⚠ User {user.username} has no groups')
                continue
            
            for group in user_groups:
                self.stdout.write(f'\n  Processing group: {group.name}')
                assigned = 0
                
                for rule in survey_rules:
                    role_rule, created = RoleRule.objects.get_or_create(
                        role=group,
                        rule=rule
                    )
                    if created:
                        assigned += 1
                        total_assigned += 1
                        perm_key = f"{rule.module.nama_module}.{rule.control.nama_kontrol}.{rule.function.nama_fungsi}"
                        self.stdout.write(f'    ✓ Assigned: {perm_key}')
                
                if assigned == 0:
                    self.stdout.write(f'    ℹ All permissions already assigned')
                else:
                    self.stdout.write(f'    ✓ Total assigned to {group.name}: {assigned}')

        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(f'✅ Done! Total new permissions assigned: {total_assigned}')
        self.stdout.write('=' * 70)
