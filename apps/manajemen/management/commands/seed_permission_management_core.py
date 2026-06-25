from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import Group

from apps.manajemen.models import (
    PermissionModule,
    PermissionControl,
    PermissionFunction,
    PermissionRule,
    RoleRule,
)

MODULE_NAME = 'pengaturan'
MODULE_LABEL = 'Pengaturan'
MODULE_ICON = 'fas fa-cogs'
MODULE_ORDER = 99

# Controls for granular permission management pages
CONTROLS = [
    ('permission_dashboard', 'Permission Dashboard'),
    ('permission_function', 'Permission Functions'),
    ('permission_control', 'Permission Controls'),
    ('permission_module', 'Permission Modules'),
    ('permission_rule', 'Permission Rules'),
    ('permission_role', 'Roles Management'),
    ('permission_user', 'Users Management'),
    ('permission_role_rule', 'Role → Rules Assignment'),
]

# Standard CRUD functions
FUNCTIONS = [
    ('view', 'Lihat'),
    ('create', 'Tambah'),
    ('edit', 'Ubah'),
    ('delete', 'Hapus'),
    ('bulk_delete', 'Hapus Banyak'),
    ('export', 'Export'),
]

class Command(BaseCommand):
    help = 'Seed Permission Module/Control/Function/Rules for core permission management (granular)'

    def handle(self, *args, **options):
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('🌱 Seeding Core Permission Management (granular)'))
        self.stdout.write('=' * 70)

        # Ensure module exists and is active
        module, _ = PermissionModule.objects.get_or_create(
            nama_module=MODULE_NAME,
            defaults={
                'label_module': MODULE_LABEL,
                'icon': MODULE_ICON,
                'order': MODULE_ORDER,
                'is_active': True,
            }
        )
        changed = False
        if module.label_module != MODULE_LABEL:
            module.label_module = MODULE_LABEL; changed = True
        if module.icon != MODULE_ICON:
            module.icon = MODULE_ICON; changed = True
        if module.order != MODULE_ORDER:
            module.order = MODULE_ORDER; changed = True
        if not module.is_active:
            module.is_active = True; changed = True
        if changed:
            module.save()

        # Controls
        control_objs = {}
        for name, label in CONTROLS:
            ctrl, _ = PermissionControl.objects.get_or_create(
                nama_kontrol=name,
                defaults={'label_kontrol': label}
            )
            if ctrl.label_kontrol != label:
                ctrl.label_kontrol = label
                ctrl.save()
            control_objs[name] = ctrl

        # Functions
        func_objs = {}
        for name, label in FUNCTIONS:
            func, _ = PermissionFunction.objects.get_or_create(
                nama_fungsi=name,
                defaults={'label_fungsi': label}
            )
            if func.label_fungsi != label:
                func.label_fungsi = label
                func.save()
            func_objs[name] = func

        # Rules
        created_rules = 0
        for ctrl_name, _ in CONTROLS:
            ctrl = control_objs[ctrl_name]
            for func_name, _ in FUNCTIONS:
                func = func_objs[func_name]
                _, created = PermissionRule.objects.get_or_create(
                    module=module, control=ctrl, function=func,
                    defaults={'is_active': True}
                )
                created_rules += int(created)
        self.stdout.write(f"  ✓ Rules created (new): {created_rules}")

        # Deactivate non-relevant functions for certain controls
        # Role → Rules Assignment is not a CRUD resource; only view/edit are meaningful.
        try:
            ctrl_role_rule = control_objs.get('permission_role_rule')
            if ctrl_role_rule:
                allowed = {'view', 'edit'}
                deactivated = PermissionRule.objects.filter(
                    module=module,
                    control=ctrl_role_rule,
                    function__nama_fungsi__in=[fn for fn, _ in FUNCTIONS if fn not in allowed],
                    is_active=True,
                ).update(is_active=False)
                if deactivated:
                    self.stdout.write(f"  ✓ Deactivated permission_role_rule non-CRUD rules: {deactivated}")
        except Exception:
            # Best-effort only; seeding should not fail hard on cleanup
            pass

        # Deactivate legacy duplicate control used by older seeders:
        # - pengaturan.manajemen_user.*
        # The actual Manajemen User pages use pengaturan.permission_user.*.
        try:
            legacy_ctrl = PermissionControl.objects.filter(nama_kontrol='manajemen_user').first()
            if legacy_ctrl:
                deactivated = PermissionRule.objects.filter(
                    module=module,
                    control=legacy_ctrl,
                    is_active=True,
                ).update(is_active=False)
                if deactivated:
                    self.stdout.write(f"  ✓ Deactivated legacy manajemen_user rules: {deactivated}")
        except Exception:
            pass

        # Assign all rules under module to Super Admin groups (as role, not bypass)
        group_names = getattr(settings, 'SUPERADMIN_GROUPS', ['Super Admin'])
        if not isinstance(group_names, (list, tuple)):
            group_names = [str(group_names)]
        rules = PermissionRule.objects.filter(module=module, is_active=True)
        assigned = 0
        for gname in group_names:
            grp, _ = Group.objects.get_or_create(name=gname)
            for rule in rules:
                _, created = RoleRule.objects.get_or_create(role=grp, rule=rule)
                assigned += int(created)
        self.stdout.write(f"  ✓ Role assignments (new): {assigned}")

        self.stdout.write(self.style.SUCCESS('✅ Core permission seeding completed'))
