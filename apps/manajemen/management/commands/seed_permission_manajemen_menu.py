from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import Group
from apps.manajemen.models import (
    PermissionModule,
    PermissionControl,
    PermissionFunction,
    PermissionRule,
)

MODULE_NAME = 'pengaturan'
MODULE_LABEL = 'Pengaturan'
MODULE_ICON = 'fas fa-cogs'
MODULE_ORDER = 99

CONTROLS = [
    ('manajemen_menu', 'Manajemen Menu'),
    ('menu_category', 'Kategori Menu'),
]

FUNCTIONS = [
    ('view', 'Lihat'),
    ('create', 'Tambah'),
    ('edit', 'Ubah'),
    ('delete', 'Hapus'),
]


class Command(BaseCommand):
    help = 'Seed Permission Module/Control/Function/Rules for Manajemen Menu & Kategori; assign to Super Admin groups'

    def handle(self, *args, **options):
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('🌱 Seeding Permissions: Pengaturan → (Manajemen Menu, Kategori)'))
        self.stdout.write('=' * 70)

        module, _ = PermissionModule.objects.get_or_create(
            nama_module=MODULE_NAME,
            defaults={
                'label_module': MODULE_LABEL,
                'icon': MODULE_ICON,
                'order': MODULE_ORDER,
                'is_active': True,
            }
        )
        # Keep label/icon/order up-to-date
        changed = False
        if module.label_module != MODULE_LABEL:
            module.label_module = MODULE_LABEL
            changed = True
        if module.icon != MODULE_ICON:
            module.icon = MODULE_ICON
            changed = True
        if module.order != MODULE_ORDER:
            module.order = MODULE_ORDER
            changed = True
        if not module.is_active:
            module.is_active = True
            changed = True
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

        # Assign all rules under module to Super Admin groups
        group_names = getattr(settings, 'SUPERADMIN_GROUPS', ['Super Admin'])
        if not isinstance(group_names, (list, tuple)):
            group_names = [str(group_names)]
        rules = PermissionRule.objects.filter(module=module, is_active=True)
        assigned = 0
        for gname in group_names:
            grp, _ = Group.objects.get_or_create(name=gname)
            for rule in rules:
                _, created = rule.role_assignments.get_or_create(role=grp)
                assigned += int(created)
        self.stdout.write(f"  ✓ Role assignments (new): {assigned}")

        self.stdout.write(self.style.SUCCESS('✅ Permission seeding completed'))
