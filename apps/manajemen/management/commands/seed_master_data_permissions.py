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

MODULE_NAME = 'manajemen_data'
MODULE_LABEL = 'Manajemen Data'
MODULE_ICON = 'fas fa-database'
MODULE_ORDER = 10

CONTROLS = [
    ('md_kategori_pegawai', 'Kategori Pegawai'),
    ('md_agama', 'Agama'),
    ('md_status_perkawinan', 'Status Perkawinan'),
    ('md_jenjang_pendidikan', 'Jenjang Pendidikan'),
    ('ms_daftar_pendidikan', 'Daftar Pendidikan'),
    ('md_kedudukan_pegawai', 'Kedudukan Pegawai'),
    ('md_jenis_jabatan', 'Jenis Jabatan'),
    ('md_kategori_jabatan', 'Kategori Jabatan'),
    ('md_pangkat', 'Pangkat'),
    ('md_jenjang_jabatan', 'Jenjang Jabatan'),
    ('md_eselon', 'Eselon'),
    ('md_diklat_struktural', 'Diklat Struktural'),
    ('md_jenis_surat', 'Jenis Surat'),
    ('md_pejabat_menetapkan', 'Pejabat Menetapkan'),
    ('md_jenis_organisasi', 'Jenis Organisasi'),
    ('md_kategori_pemberitahuan', 'Kategori Pemberitahuan'),
    ('md_kategori_peraturan', 'Kategori Peraturan'),
    ('md_peraturan', 'Peraturan'),
    ('md_tentang', 'Tentang'),
]

FUNCTIONS = [
    ('view', 'Lihat'),
    ('create', 'Tambah'),
    ('edit', 'Ubah'),
    ('delete', 'Hapus'),
    ('bulk_delete', 'Hapus Banyak'),
    ('export', 'Export'),
]


class Command(BaseCommand):
    help = 'Seed permissions for Manajemen Data (Master Data CRUD)'

    def handle(self, *args, **options):
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('🌱 Seeding Manajemen Data permissions'))
        self.stdout.write('=' * 70)

        module, _ = PermissionModule.objects.get_or_create(
            nama_module=MODULE_NAME,
            defaults={
                'label_module': MODULE_LABEL,
                'icon': MODULE_ICON,
                'order': MODULE_ORDER,
                'is_active': True,
            },
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
                defaults={'label_kontrol': label},
            )
            if ctrl.label_kontrol != label:
                ctrl.label_kontrol = label
                ctrl.save()
            control_objs[name] = ctrl

        func_objs = {}
        for name, label in FUNCTIONS:
            func, _ = PermissionFunction.objects.get_or_create(
                nama_fungsi=name,
                defaults={'label_fungsi': label},
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
                    module=module,
                    control=ctrl,
                    function=func,
                    defaults={'is_active': True},
                )
                created_rules += int(created)
        self.stdout.write(f'  ✓ Rules created (new): {created_rules}')

        # Deactivate legacy rules under module "master_data" to avoid duplicates in Role Rule UI
        # (historically some deployments seeded master data permissions under module name "master_data")
        try:
            legacy_module = PermissionModule.objects.filter(nama_module='master_data').first()
            if legacy_module:
                legacy_ctrls = PermissionControl.objects.filter(nama_kontrol__in=[c[0] for c in CONTROLS])
                legacy_rules = PermissionRule.objects.filter(module=legacy_module, control__in=legacy_ctrls, is_active=True)
                legacy_rule_ids = list(legacy_rules.values_list('id', flat=True))
                if legacy_rule_ids:
                    removed_rr = RoleRule.objects.filter(rule_id__in=legacy_rule_ids).delete()[0]
                    legacy_rules.update(is_active=False)
                    self.stdout.write(f'  ✓ Legacy rules deactivated: {len(legacy_rule_ids)} (role assignments removed: {removed_rr})')
        except Exception:
            pass

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
        self.stdout.write(f'  ✓ Role assignments (new): {assigned}')

        self.stdout.write(self.style.SUCCESS('✅ Manajemen Data permission seeding completed'))
