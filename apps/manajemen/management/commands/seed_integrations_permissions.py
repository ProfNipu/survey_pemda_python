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

MODULE_NAME = 'integrations'
MODULE_LABEL = 'Integrations'
MODULE_ICON = 'fas fa-plug'
MODULE_ORDER = 80

CONTROLS = [
    ('siasn_tokens', 'SIASN Tokens'),
    ('siasn_logs', 'SIASN API Logs'),
    ('siasn_pegawai', 'SIASN Pegawai Cache'),
    ('siasn_progress', 'SIASN Fetch Progress'),
    ('siasn_management', 'SIASN Management Dashboard'),
    ('siasn_fetch_docs', 'SIASN Fetch Docs'),
    ('siasn_endpoint_rules', 'SIASN Endpoint Rules'),
    ('siasn_etl', 'SIASN ETL'),
]

FUNCTIONS = [
    ('view', 'Lihat'),
    ('create', 'Tambah'),
    ('edit', 'Ubah'),
    ('delete', 'Hapus'),
]

class Command(BaseCommand):
    help = 'Seed permissions for Integrations (SIASN) management views'

    def handle(self, *args, **options):
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('🌱 Seeding Integrations (SIASN) permissions'))
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

        created_rules = 0
        for ctrl_name in control_objs.keys():
            ctrl = control_objs[ctrl_name]
            for func_name in func_objs.keys():
                func = func_objs[func_name]
                _, created = PermissionRule.objects.get_or_create(
                    module=module, control=ctrl, function=func,
                    defaults={'is_active': True}
                )
                created_rules += int(created)
        self.stdout.write(f"  ✓ Rules created (new): {created_rules}")

        # Assign to Super Admin groups (as role)
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

        self.stdout.write(self.style.SUCCESS('✅ Integrations permission seeding completed'))
