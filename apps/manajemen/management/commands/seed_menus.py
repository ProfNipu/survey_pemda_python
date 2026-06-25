"""
Seed initial MenuItem data for DB-driven sidebar
Run: python manage.py seed_menus
"""
from django.core.management.base import BaseCommand
from django.db import models
from django.db.models import Q
from decouple import config
from apps.manajemen.models import MenuItem


class Command(BaseCommand):
    help = 'Seed initial MenuItem records for dynamic sidebar'

    def handle(self, *args, **options):
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('🌱 Seeding Menu Items'))
        self.stdout.write('=' * 70)

        disabled_raw = config('APP_DISABLED_MENU_CATEGORIES', default='')
        disabled_categories = set()
        try:
            for part in (disabled_raw or '').split(','):
                part = (part or '').strip()
                if part:
                    disabled_categories.add(int(part))
        except Exception:
            disabled_categories = set()

        created_count = 0

        def _dedupe_and_get_root_by_name(name: str):
            qs = MenuItem.objects.filter(name=name, parent__isnull=True).order_by('id')
            obj = qs.first()
            if not obj:
                return None
            dups = qs.exclude(id=obj.id)
            if dups.exists():
                dups.update(is_active=False)
            return obj

        def _ensure_root_menu(
            *,
            name: str,
            defaults: dict,
            legacy_names: list[str] | None = None,
        ):
            legacy_names = legacy_names or []
            for legacy in legacy_names:
                legacy_obj = _dedupe_and_get_root_by_name(legacy)
                if legacy_obj:
                    legacy_obj.name = name
                    legacy_obj.save(update_fields=['name'])
            obj = _dedupe_and_get_root_by_name(name)
            created_local = False
            if not obj:
                obj = MenuItem.objects.create(name=name, parent=None, **defaults)
                created_local = True
            return obj, created_local

        # Beranda (category 6)
        dashboard, created = _ensure_root_menu(
            name='Beranda',
            legacy_names=['Dashboard'],
            defaults={
                'permission_key': 'dashboard.dashboard_main.view',
                'url_name': 'dashboard:index',
                'icon': 'fas fa-home',
                'type': 'module',
                'order': 1,
                'category': 6,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Beranda')
        else:
            changed = False
            if dashboard.url_name != 'dashboard:index':
                dashboard.url_name = 'dashboard:index'; changed = True
            if dashboard.permission_key != 'dashboard.dashboard_main.view':
                dashboard.permission_key = 'dashboard.dashboard_main.view'; changed = True
            if dashboard.icon != 'fas fa-home':
                dashboard.icon = 'fas fa-home'; changed = True
            if dashboard.type != 'module':
                dashboard.type = 'module'; changed = True
            if (dashboard.order or 0) != 1:
                dashboard.order = 1; changed = True
            if (dashboard.category or 0) != 6:
                dashboard.category = 6; changed = True
            if dashboard.parent_id is not None:
                dashboard.parent = None; changed = True
            if not dashboard.is_active:
                dashboard.is_active = True; changed = True
            if changed:
                dashboard.save()
                self.stdout.write('  ✓ Updated: Beranda')

        # Rename legacy group labels to new naming to avoid duplicates
        try:
            legacy_app = MenuItem.objects.filter(name='Manajemen Aplikasi', parent__isnull=True).first()
            if legacy_app:
                legacy_app.name = 'Pengaturan Aplikasi'
                legacy_app.save(update_fields=['name'])
            legacy_md = MenuItem.objects.filter(name='Manajemen Data', parent__isnull=True).first()
            if legacy_md:
                legacy_md.name = 'Data Induk'
                legacy_md.save(update_fields=['name'])
            legacy_md2 = MenuItem.objects.filter(name='Master Data', parent__isnull=True).first()
            if legacy_md2:
                legacy_md2.name = 'Data Induk'
                legacy_md2.save(update_fields=['name'])
            legacy_anjab = MenuItem.objects.filter(name='Manajemen Analisis Jabatan', parent__isnull=True).first()
            if legacy_anjab:
                legacy_anjab.name = 'Analisis Jabatan'
                legacy_anjab.save(update_fields=['name'])
            legacy_bkn = MenuItem.objects.filter(name='Manajemen Referensi Data BKN', parent__isnull=True).first()
            if legacy_bkn:
                legacy_bkn.name = 'Referensi BKN'
                legacy_bkn.save(update_fields=['name'])

            # Cleanup legacy Assessment root group (Mr_assessment is now under Kepegawaian → Riwayat)
            legacy_assessment = MenuItem.objects.filter(name='Assessment', parent__isnull=True).first()
            if legacy_assessment and legacy_assessment.is_active:
                MenuItem.objects.filter(parent=legacy_assessment).update(is_active=False)
                legacy_assessment.is_active = False
                legacy_assessment.save(update_fields=['is_active'])
        except Exception:
            pass

        # Pengaturan Sistem group (category 1)
        super_admin_group, created = _ensure_root_menu(
            name='Pengaturan Aplikasi',
            legacy_names=['Manajemen Aplikasi'],
            defaults={
                'type': 'menuItem',
                'icon': 'fas fa-cogs',
                'order': 1,
                'category': 1,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Pengaturan Aplikasi (group)')

        # Unify Dashboard Granular menu item (rename older labels to one canonical name)
        perm_dash = MenuItem.objects.filter(parent=super_admin_group, url_name='manajemen_aplikasi:dashboard').first()
        if perm_dash:
            changed = False
            if perm_dash.name != 'Manajemen Akses Granular':
                perm_dash.name = 'Manajemen Akses Granular'; changed = True
            if perm_dash.permission_key != 'pengaturan.manajemen_permission.view':
                perm_dash.permission_key = 'pengaturan.manajemen_permission.view'; changed = True
            if perm_dash.icon != 'fas fa-shield-alt':
                perm_dash.icon = 'fas fa-shield-alt'; changed = True
            if perm_dash.type != 'module':
                perm_dash.type = 'module'; changed = True
            if (perm_dash.order or 0) != 1:
                perm_dash.order = 1; changed = True
            if (perm_dash.category or 0) != 1:
                perm_dash.category = 1; changed = True
            if not perm_dash.is_active:
                perm_dash.is_active = True; changed = True
            if changed:
                perm_dash.save()
                self.stdout.write('  ✓ Updated: Manajemen Akses Granular')
        else:
            perm_dash, created = MenuItem.objects.get_or_create(
                name='Manajemen Akses Granular',
                parent=super_admin_group,
                defaults={
                    'permission_key': 'pengaturan.manajemen_permission.view',
                    'url_name': 'manajemen_aplikasi:dashboard',
                    'icon': 'fas fa-shield-alt',
                    'type': 'module',
                    'order': 1,
                    'category': 1,
                    'is_active': True,
                }
            )
            created_count += int(created)
            if created:
                self.stdout.write('  ✓ Created: Manajemen Akses Granular')

        # Deactivate duplicate items pointing to the same url under the same parent
        try:
            duplicates = MenuItem.objects.filter(parent=super_admin_group, url_name='manajemen_aplikasi:dashboard').exclude(pk=perm_dash.pk)
            deactivated = 0
            for dup in duplicates:
                if dup.is_active or dup.parent_id is not None or dup.name != 'Manajemen Akses Granular':
                    dup.is_active = False
                    dup.parent = None
                    dup.save(update_fields=['is_active', 'parent'])
                    deactivated += 1
            if deactivated:
                self.stdout.write(f'  ✓ Deactivated granular duplicates: {deactivated}')
        except Exception:
            pass

        # Manajemen Menu (category 1)
        manajemen_menu, created = MenuItem.objects.get_or_create(
            name='Manajemen Menu',
            parent=super_admin_group,
            defaults={
                'permission_key': 'pengaturan.manajemen_menu.view',
                'url_name': 'manajemen_aplikasi:menu_list',
                'icon': 'fas fa-sitemap',
                'type': 'module',
                'order': 2,
                'category': 1,
                'is_active': True,
            }
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Manajemen Menu')
        else:
            changed = False
            if manajemen_menu.permission_key != 'pengaturan.manajemen_menu.view':
                manajemen_menu.permission_key = 'pengaturan.manajemen_menu.view'; changed = True
            if manajemen_menu.url_name != 'manajemen_aplikasi:menu_list':
                manajemen_menu.url_name = 'manajemen_aplikasi:menu_list'; changed = True
            if manajemen_menu.icon != 'fas fa-sitemap':
                manajemen_menu.icon = 'fas fa-sitemap'; changed = True
            if manajemen_menu.type != 'module':
                manajemen_menu.type = 'module'; changed = True
            if (manajemen_menu.order or 0) != 2:
                manajemen_menu.order = 2; changed = True
            if (manajemen_menu.category or 0) != 1:
                manajemen_menu.category = 1; changed = True
            if manajemen_menu.parent_id != super_admin_group.id:
                manajemen_menu.parent = super_admin_group; changed = True
            if not manajemen_menu.is_active:
                manajemen_menu.is_active = True; changed = True
            if changed:
                manajemen_menu.save()
                self.stdout.write('  ✓ Updated: Manajemen Menu')

        try:
            duplicates = MenuItem.objects.filter(url_name='manajemen_aplikasi:menu_list').exclude(pk=manajemen_menu.pk)
            deactivated = 0
            for dup in duplicates:
                if dup.is_active or dup.parent_id is not None:
                    dup.is_active = False
                    dup.parent = None
                    dup.save(update_fields=['is_active', 'parent'])
                    deactivated += 1
            if deactivated:
                self.stdout.write(f'  ✓ Deactivated menu duplicates: {deactivated}')
        except Exception:
            pass

        # Integrasi (category 4)
        siasn_group, created = _ensure_root_menu(
            name='Integrasi SIASN',
            legacy_names=[],
            defaults={
                'type': 'menuItem',
                'icon': 'fas fa-sync-alt',
                'order': 1,
                'category': 4,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Integrasi SIASN (group)')

        legacy_siasn_home = MenuItem.objects.filter(
            parent=siasn_group,
            url_name='integrations:siasn_management',
        ).order_by('id').first()
        if not legacy_siasn_home:
            legacy_siasn_home = MenuItem.objects.filter(
                parent=siasn_group,
                name='Manajemen SIASN',
            ).order_by('id').first()

        if legacy_siasn_home:
            siasn_management_menu = legacy_siasn_home
            created = False
        else:
            siasn_management_menu, created = MenuItem.objects.get_or_create(
                name='Beranda SIASN',
                parent=siasn_group,
                defaults={
                    'permission_key': 'integrations.siasn_management.view',
                    'url_name': 'integrations:siasn_home',
                    'icon': 'fas fa-th-large',
                    'type': 'module',
                    'order': 1,
                    'category': 4,
                    'is_active': True,
                }
            )

        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Beranda SIASN')

        changed = False
        if siasn_management_menu.name != 'Beranda SIASN':
            siasn_management_menu.name = 'Beranda SIASN'; changed = True
        if siasn_management_menu.permission_key != 'integrations.siasn_management.view':
            siasn_management_menu.permission_key = 'integrations.siasn_management.view'; changed = True
        if siasn_management_menu.url_name != 'integrations:siasn_home':
            siasn_management_menu.url_name = 'integrations:siasn_home'; changed = True
        if siasn_management_menu.icon != 'fas fa-th-large':
            siasn_management_menu.icon = 'fas fa-th-large'; changed = True
        if siasn_management_menu.type != 'module':
            siasn_management_menu.type = 'module'; changed = True
        if (siasn_management_menu.order or 0) != 1:
            siasn_management_menu.order = 1; changed = True
        if (siasn_management_menu.category or 0) != 4:
            siasn_management_menu.category = 4; changed = True
        if siasn_management_menu.parent_id != siasn_group.id:
            siasn_management_menu.parent = siasn_group; changed = True
        if not siasn_management_menu.is_active:
            siasn_management_menu.is_active = True; changed = True
        if changed:
            siasn_management_menu.save()
            self.stdout.write('  ✓ Updated: Beranda SIASN')

        MenuItem.objects.filter(parent=siasn_group).filter(
            Q(name='Manajemen SIASN') | Q(url_name='integrations:siasn_management')
        ).exclude(id=siasn_management_menu.id).update(is_active=False)

        siasn_dash, created = MenuItem.objects.get_or_create(
            name='SIASN Dashboard',
            parent=siasn_group,
            defaults={
                'permission_key': 'siasn.siasn_dashboard.view',
                'url_name': 'integrations:siasn_dashboard',
                'icon': 'fas fa-sync-alt',
                'type': 'module',
                'order': 1,
                'category': 4,
                'is_active': False,
            }
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: SIASN Dashboard')
        else:
            if siasn_dash.is_active:
                siasn_dash.is_active = False
                siasn_dash.save(update_fields=['is_active'])
                self.stdout.write('  ✓ Updated: SIASN Dashboard (deactivated)')

        siasn_fetch_docs, created = MenuItem.objects.get_or_create(
            name='Dokumentasi Fetch SIASN',
            parent=siasn_group,
            defaults={
                'permission_key': 'integrations.siasn_fetch_docs.view',
                'url_name': 'integrations:siasn_fetch_docs',
                'icon': 'fas fa-book',
                'type': 'module',
                'order': 2,
                'category': 4,
                'is_active': True,
            }
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Dokumentasi Fetch SIASN')

        siasn_endpoint_rules, created = MenuItem.objects.get_or_create(
            name='Konfigurasi Endpoint SIASN',
            parent=siasn_group,
            defaults={
                'permission_key': 'integrations.siasn_endpoint_rules.view',
                'url_name': 'integrations:siasn_endpoint_rules',
                'icon': 'fas fa-cog',
                'type': 'module',
                'order': 3,
                'category': 4,
                'is_active': True,
            }
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Konfigurasi Endpoint SIASN')

        siasn_etl_apply_data_utama, created = MenuItem.objects.get_or_create(
            name='Apply Data Utama (ETL)',
            parent=siasn_group,
            defaults={
                'permission_key': 'integrations.siasn_etl.view',
                'url_name': 'integrations:siasn_apply_data_utama',
                'icon': 'fas fa-database',
                'type': 'module',
                'order': 4,
                'category': 4,
                'is_active': True,
            }
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Apply Data Utama (ETL)')

        siasn_tokens_menu, created = MenuItem.objects.get_or_create(
            name='Token SIASN',
            parent=siasn_group,
            defaults={
                'permission_key': 'integrations.siasn_tokens.view',
                'url_name': 'integrations:token_list',
                'icon': 'fas fa-key',
                'type': 'module',
                'order': 5,
                'category': 4,
                'is_active': True,
            }
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Token SIASN')
        else:
            changed = False
            if siasn_tokens_menu.permission_key != 'integrations.siasn_tokens.view':
                siasn_tokens_menu.permission_key = 'integrations.siasn_tokens.view'; changed = True
            if siasn_tokens_menu.url_name != 'integrations:token_list':
                siasn_tokens_menu.url_name = 'integrations:token_list'; changed = True
            if siasn_tokens_menu.icon != 'fas fa-key':
                siasn_tokens_menu.icon = 'fas fa-key'; changed = True
            if siasn_tokens_menu.type != 'module':
                siasn_tokens_menu.type = 'module'; changed = True
            if (siasn_tokens_menu.order or 0) != 5:
                siasn_tokens_menu.order = 5; changed = True
            if (siasn_tokens_menu.category or 0) != 4:
                siasn_tokens_menu.category = 4; changed = True
            if siasn_tokens_menu.parent_id != siasn_group.id:
                siasn_tokens_menu.parent = siasn_group; changed = True
            if not siasn_tokens_menu.is_active:
                siasn_tokens_menu.is_active = True; changed = True
            if changed:
                siasn_tokens_menu.save()
                self.stdout.write('  ✓ Updated: Token SIASN')

        # Data Induk (category 5)
        manajemen_data_group, created = _ensure_root_menu(
            name='Data Induk',
            legacy_names=['Manajemen Data', 'Master Data'],
            defaults={
                'type': 'menuItem',
                'icon': 'fas fa-database',
                'order': 1,
                'category': 5,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Data Induk (group)')
        else:
            changed = False
            if manajemen_data_group.type != 'menuItem':
                manajemen_data_group.type = 'menuItem'; changed = True
            if manajemen_data_group.icon != 'fas fa-database':
                manajemen_data_group.icon = 'fas fa-database'; changed = True
            if (manajemen_data_group.order or 0) != 1:
                manajemen_data_group.order = 1; changed = True
            if (manajemen_data_group.category or 0) != 5:
                manajemen_data_group.category = 5; changed = True
            if not manajemen_data_group.is_active:
                manajemen_data_group.is_active = True; changed = True
            if changed:
                manajemen_data_group.save()
                self.stdout.write('  ✓ Updated: Data Induk (group)')

        # Cleanup: remove nested "Data Induk" under Data Induk (if it exists from older seed)
        try:
            nested_data_induk = MenuItem.objects.filter(name='Data Induk', parent=manajemen_data_group).first()
            if nested_data_induk:
                # Move its children up to the root Data Induk
                MenuItem.objects.filter(parent=nested_data_induk).update(parent=manajemen_data_group)
                # Deactivate the nested node to avoid duplicated label in sidebar
                nested_data_induk.is_active = False
                nested_data_induk.save(update_fields=['is_active'])
        except Exception:
            pass

        # Dedupe: ensure no duplicate (parent, name) exists under Data Induk tree.
        # Multiple legacy seed runs can create duplicated children, which breaks get_or_create().
        try:
            queue = [manajemen_data_group.id]
            visited = set()
            while queue:
                current_parent_id = queue.pop(0)
                if current_parent_id in visited:
                    continue
                visited.add(current_parent_id)

                children = list(MenuItem.objects.filter(parent_id=current_parent_id).order_by('name', 'id'))
                seen_names = set()
                for ch in children:
                    key = (ch.name or '').strip().lower()
                    if key in seen_names:
                        ch.is_active = False
                        ch.parent = None
                        ch.save(update_fields=['is_active', 'parent'])
                        continue
                    seen_names.add(key)
                    queue.append(ch.id)
        except Exception:
            pass

        # Analisis Jabatan (category 5)
        manajemen_anjab_group, created = _ensure_root_menu(
            name='Analisis Jabatan',
            legacy_names=['Manajemen Analisis Jabatan'],
            defaults={
                'type': 'menuItem',
                'icon': 'fas fa-clipboard-list',
                'order': 2,
                'category': 5,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Analisis Jabatan (group)')
        else:
            changed = False
            if manajemen_anjab_group.type != 'menuItem':
                manajemen_anjab_group.type = 'menuItem'; changed = True
            if manajemen_anjab_group.icon != 'fas fa-clipboard-list':
                manajemen_anjab_group.icon = 'fas fa-clipboard-list'; changed = True
            if (manajemen_anjab_group.order or 0) != 2:
                manajemen_anjab_group.order = 2; changed = True
            if (manajemen_anjab_group.category or 0) != 5:
                manajemen_anjab_group.category = 5; changed = True
            if not manajemen_anjab_group.is_active:
                manajemen_anjab_group.is_active = True; changed = True
            if changed:
                manajemen_anjab_group.save()
                self.stdout.write('  ✓ Updated: Analisis Jabatan (group)')

        # Referensi BKN (category 5)
        manajemen_bkn_group, created = _ensure_root_menu(
            name='Referensi BKN',
            legacy_names=['Manajemen Referensi Data BKN'],
            defaults={
                'type': 'menuItem',
                'icon': 'fas fa-cloud',
                'order': 3,
                'category': 5,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Referensi BKN (group)')
        else:
            changed = False
            if manajemen_bkn_group.type != 'menuItem':
                manajemen_bkn_group.type = 'menuItem'; changed = True
            if manajemen_bkn_group.icon != 'fas fa-cloud':
                manajemen_bkn_group.icon = 'fas fa-cloud'; changed = True
            if (manajemen_bkn_group.order or 0) != 3:
                manajemen_bkn_group.order = 3; changed = True
            if (manajemen_bkn_group.category or 0) != 5:
                manajemen_bkn_group.category = 5; changed = True
            if not manajemen_bkn_group.is_active:
                manajemen_bkn_group.is_active = True; changed = True
            if changed:
                manajemen_bkn_group.save()
                self.stdout.write('  ✓ Updated: Referensi BKN (group)')

        # Master Data: Kepegawaian (category 5)
        kepegawaian_group, created = _ensure_root_menu(
            name='Kepegawaian',
            legacy_names=[],
            defaults={
                'type': 'menuItem',
                'icon': 'fas fa-users',
                'order': 5,
                'category': 5,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Kepegawaian (group)')
        else:
            changed = False
            if kepegawaian_group.type != 'menuItem':
                kepegawaian_group.type = 'menuItem'; changed = True
            if kepegawaian_group.icon != 'fas fa-users':
                kepegawaian_group.icon = 'fas fa-users'; changed = True
            if (kepegawaian_group.order or 0) != 5:
                kepegawaian_group.order = 5; changed = True
            if (kepegawaian_group.category or 0) != 5:
                kepegawaian_group.category = 5; changed = True
            if kepegawaian_group.parent_id is not None:
                kepegawaian_group.parent = None; changed = True
            if not kepegawaian_group.is_active:
                kepegawaian_group.is_active = True; changed = True
            if changed:
                kepegawaian_group.save()
                self.stdout.write('  ✓ Updated: Kepegawaian (group)')

        # Note: Mr_assessment follows the same pattern as other riwayat modules.
        # It is seeded under Kepegawaian → Riwayat (see below), not as a separate root group.

        tabel_pegawai, created = MenuItem.objects.get_or_create(
            name='Tabel Pegawai',
            parent=kepegawaian_group,
            defaults={
                'permission_key': 'kepegawaian.Ms_pegawai.view',
                'url_name': 'manajemen_data_kepegawaian:ms_pegawai_list',
                'icon': 'fas fa-users',
                'type': 'module',
                'order': 1,
                'category': 5,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Tabel Pegawai')
        else:
            changed = False
            if tabel_pegawai.permission_key != 'kepegawaian.Ms_pegawai.view':
                tabel_pegawai.permission_key = 'kepegawaian.Ms_pegawai.view'; changed = True
            if tabel_pegawai.url_name != 'manajemen_data_kepegawaian:ms_pegawai_list':
                tabel_pegawai.url_name = 'manajemen_data_kepegawaian:ms_pegawai_list'; changed = True
            if tabel_pegawai.icon != 'fas fa-users':
                tabel_pegawai.icon = 'fas fa-users'; changed = True
            if tabel_pegawai.type != 'module':
                tabel_pegawai.type = 'module'; changed = True
            if (tabel_pegawai.order or 0) != 1:
                tabel_pegawai.order = 1; changed = True
            if (tabel_pegawai.category or 0) != 5:
                tabel_pegawai.category = 5; changed = True
            if tabel_pegawai.parent_id != kepegawaian_group.id:
                tabel_pegawai.parent = kepegawaian_group; changed = True
            if not tabel_pegawai.is_active:
                tabel_pegawai.is_active = True; changed = True
            if changed:
                tabel_pegawai.save()
                self.stdout.write('  ✓ Updated: Tabel Pegawai')

        riwayat_group, created = MenuItem.objects.get_or_create(
            name='Riwayat',
            parent=kepegawaian_group,
            defaults={
                'type': 'menuItem',
                'icon': 'fas fa-history',
                'order': 2,
                'category': 5,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Kepegawaian → Riwayat (group)')
        else:
            changed = False
            if riwayat_group.type != 'menuItem':
                riwayat_group.type = 'menuItem'; changed = True
            if riwayat_group.icon != 'fas fa-history':
                riwayat_group.icon = 'fas fa-history'; changed = True
            if (riwayat_group.order or 0) != 2:
                riwayat_group.order = 2; changed = True
            if (riwayat_group.category or 0) != 5:
                riwayat_group.category = 5; changed = True
            if riwayat_group.parent_id != kepegawaian_group.id:
                riwayat_group.parent = kepegawaian_group; changed = True
            if not riwayat_group.is_active:
                riwayat_group.is_active = True; changed = True
            if changed:
                riwayat_group.save()
                self.stdout.write('  ✓ Updated: Kepegawaian → Riwayat (group)')

        tata_naskah_pegawai, created = MenuItem.objects.get_or_create(
            name='Tata Naskah Pegawai',
            parent=kepegawaian_group,
            defaults={
                'permission_key': 'kepegawaian.Ms_tata_naskah_pegawai.view',
                'url_name': 'manajemen_data_kepegawaian:ms_tata_naskah_pegawai_list',
                'icon': 'fas fa-file-signature',
                'type': 'module',
                'order': 3,
                'category': 5,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Kepegawaian → Tata Naskah Pegawai')
        else:
            changed = False
            if tata_naskah_pegawai.permission_key != 'kepegawaian.Ms_tata_naskah_pegawai.view':
                tata_naskah_pegawai.permission_key = 'kepegawaian.Ms_tata_naskah_pegawai.view'; changed = True
            if tata_naskah_pegawai.url_name != 'manajemen_data_kepegawaian:ms_tata_naskah_pegawai_list':
                tata_naskah_pegawai.url_name = 'manajemen_data_kepegawaian:ms_tata_naskah_pegawai_list'; changed = True
            if tata_naskah_pegawai.icon != 'fas fa-file-signature':
                tata_naskah_pegawai.icon = 'fas fa-file-signature'; changed = True
            if tata_naskah_pegawai.type != 'module':
                tata_naskah_pegawai.type = 'module'; changed = True
            if (tata_naskah_pegawai.order or 0) != 3:
                tata_naskah_pegawai.order = 3; changed = True
            if (tata_naskah_pegawai.category or 0) != 5:
                tata_naskah_pegawai.category = 5; changed = True
            if tata_naskah_pegawai.parent_id != kepegawaian_group.id:
                tata_naskah_pegawai.parent = kepegawaian_group; changed = True
            if not tata_naskah_pegawai.is_active:
                tata_naskah_pegawai.is_active = True; changed = True
            if changed:
                tata_naskah_pegawai.save()
                self.stdout.write('  ✓ Updated: Kepegawaian → Tata Naskah Pegawai')

        # Cleanup legacy duplicates: sometimes 'Tabel Pegawai' was accidentally put under Kepegawaian → Riwayat
        try:
            dup_qs = MenuItem.objects.filter(parent=riwayat_group, is_active=True).filter(
                models.Q(url_name='manajemen_data_kepegawaian:ms_pegawai_list')
                | models.Q(name='Tabel Pegawai')
            )
            for dup in dup_qs:
                dup.is_active = False
                dup.save()
                self.stdout.write('  ✓ Deactivated legacy duplicate menu: Kepegawaian → Riwayat → Tabel Pegawai')
        except Exception:
            pass

        riwayat_pangkat, created = MenuItem.objects.get_or_create(
            name='Riwayat Pangkat',
            parent=riwayat_group,
            defaults={
                'permission_key': 'kepegawaian.Mr_pangkat.view',
                'url_name': 'manajemen_data_kepegawaian:mr_pangkat_list',
                'icon': 'fas fa-layer-group',
                'type': 'module',
                'order': 1,
                'category': 5,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Kepegawaian → Riwayat → Riwayat Pangkat')
        else:
            changed = False
            if riwayat_pangkat.permission_key != 'kepegawaian.Mr_pangkat.view':
                riwayat_pangkat.permission_key = 'kepegawaian.Mr_pangkat.view'; changed = True
            if riwayat_pangkat.url_name != 'manajemen_data_kepegawaian:mr_pangkat_list':
                riwayat_pangkat.url_name = 'manajemen_data_kepegawaian:mr_pangkat_list'; changed = True
            if riwayat_pangkat.icon != 'fas fa-layer-group':
                riwayat_pangkat.icon = 'fas fa-layer-group'; changed = True
            if riwayat_pangkat.type != 'module':
                riwayat_pangkat.type = 'module'; changed = True
            if (riwayat_pangkat.order or 0) != 1:
                riwayat_pangkat.order = 1; changed = True
            if (riwayat_pangkat.category or 0) != 5:
                riwayat_pangkat.category = 5; changed = True
            if riwayat_pangkat.parent_id != riwayat_group.id:
                riwayat_pangkat.parent = riwayat_group; changed = True
            if not riwayat_pangkat.is_active:
                riwayat_pangkat.is_active = True; changed = True
            if changed:
                riwayat_pangkat.save()
                self.stdout.write('  ✓ Updated: Kepegawaian → Riwayat → Riwayat Pangkat')

        riwayat_jabatan, created = MenuItem.objects.get_or_create(
            name='Riwayat Jabatan',
            parent=riwayat_group,
            defaults={
                'permission_key': 'kepegawaian.Mr_jabatan.view',
                'url_name': 'manajemen_data_kepegawaian:mr_jabatan_list',
                'icon': 'fas fa-briefcase',
                'type': 'module',
                'order': 2,
                'category': 5,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Kepegawaian → Riwayat → Riwayat Jabatan')
        else:
            changed = False
            if riwayat_jabatan.permission_key != 'kepegawaian.Mr_jabatan.view':
                riwayat_jabatan.permission_key = 'kepegawaian.Mr_jabatan.view'; changed = True
            if riwayat_jabatan.url_name != 'manajemen_data_kepegawaian:mr_jabatan_list':
                riwayat_jabatan.url_name = 'manajemen_data_kepegawaian:mr_jabatan_list'; changed = True
            if riwayat_jabatan.icon != 'fas fa-briefcase':
                riwayat_jabatan.icon = 'fas fa-briefcase'; changed = True
            if riwayat_jabatan.type != 'module':
                riwayat_jabatan.type = 'module'; changed = True
            if (riwayat_jabatan.order or 0) != 2:
                riwayat_jabatan.order = 2; changed = True
            if (riwayat_jabatan.category or 0) != 5:
                riwayat_jabatan.category = 5; changed = True
            if riwayat_jabatan.parent_id != riwayat_group.id:
                riwayat_jabatan.parent = riwayat_group; changed = True
            if not riwayat_jabatan.is_active:
                riwayat_jabatan.is_active = True; changed = True
            if changed:
                riwayat_jabatan.save()
                self.stdout.write('  ✓ Updated: Kepegawaian → Riwayat → Riwayat Jabatan')

        riwayat_pendidikan, created = MenuItem.objects.get_or_create(
            name='Riwayat Pendidikan',
            parent=riwayat_group,
            defaults={
                'permission_key': 'kepegawaian.Mr_pendidikan.view',
                'url_name': 'manajemen_data_kepegawaian:mr_pendidikan_list',
                'icon': 'fas fa-graduation-cap',
                'type': 'module',
                'order': 3,
                'category': 5,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Kepegawaian → Riwayat → Riwayat Pendidikan')
        else:
            changed = False
            if riwayat_pendidikan.permission_key != 'kepegawaian.Mr_pendidikan.view':
                riwayat_pendidikan.permission_key = 'kepegawaian.Mr_pendidikan.view'; changed = True
            if riwayat_pendidikan.url_name != 'manajemen_data_kepegawaian:mr_pendidikan_list':
                riwayat_pendidikan.url_name = 'manajemen_data_kepegawaian:mr_pendidikan_list'; changed = True
            if riwayat_pendidikan.icon != 'fas fa-graduation-cap':
                riwayat_pendidikan.icon = 'fas fa-graduation-cap'; changed = True
            if riwayat_pendidikan.type != 'module':
                riwayat_pendidikan.type = 'module'; changed = True
            if (riwayat_pendidikan.order or 0) != 3:
                riwayat_pendidikan.order = 3; changed = True
            if (riwayat_pendidikan.category or 0) != 5:
                riwayat_pendidikan.category = 5; changed = True
            if riwayat_pendidikan.parent_id != riwayat_group.id:
                riwayat_pendidikan.parent = riwayat_group; changed = True
            if not riwayat_pendidikan.is_active:
                riwayat_pendidikan.is_active = True; changed = True
            if changed:
                riwayat_pendidikan.save()
                self.stdout.write('  ✓ Updated: Kepegawaian → Riwayat → Riwayat Pendidikan')

        riwayat_ortu, created = MenuItem.objects.get_or_create(
            name='Riwayat Ortu',
            parent=riwayat_group,
            defaults={
                'permission_key': 'kepegawaian.Mr_ortu.view',
                'url_name': 'manajemen_data_kepegawaian:mr_ortu_list',
                'icon': 'fas fa-users',
                'type': 'module',
                'order': 4,
                'category': 5,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Kepegawaian → Riwayat → Riwayat Ortu')
        else:
            changed = False
            if riwayat_ortu.permission_key != 'kepegawaian.Mr_ortu.view':
                riwayat_ortu.permission_key = 'kepegawaian.Mr_ortu.view'; changed = True
            if riwayat_ortu.url_name != 'manajemen_data_kepegawaian:mr_ortu_list':
                riwayat_ortu.url_name = 'manajemen_data_kepegawaian:mr_ortu_list'; changed = True
            if riwayat_ortu.icon != 'fas fa-users':
                riwayat_ortu.icon = 'fas fa-users'; changed = True
            if riwayat_ortu.type != 'module':
                riwayat_ortu.type = 'module'; changed = True
            if (riwayat_ortu.order or 0) != 4:
                riwayat_ortu.order = 4; changed = True
            if (riwayat_ortu.category or 0) != 5:
                riwayat_ortu.category = 5; changed = True
            if riwayat_ortu.parent_id != riwayat_group.id:
                riwayat_ortu.parent = riwayat_group; changed = True
            if not riwayat_ortu.is_active:
                riwayat_ortu.is_active = True; changed = True
            if changed:
                riwayat_ortu.save()
                self.stdout.write('  ✓ Updated: Kepegawaian → Riwayat → Riwayat Ortu')

        riwayat_pasangan, created = MenuItem.objects.get_or_create(
            name='Riwayat Pasangan',
            parent=riwayat_group,
            defaults={
                'permission_key': 'kepegawaian.Mr_pasangan.view',
                'url_name': 'manajemen_data_kepegawaian:mr_pasangan_list',
                'icon': 'fas fa-user-friends',
                'type': 'module',
                'order': 5,
                'category': 5,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Kepegawaian → Riwayat → Riwayat Pasangan')
        else:
            changed = False
            if riwayat_pasangan.permission_key != 'kepegawaian.Mr_pasangan.view':
                riwayat_pasangan.permission_key = 'kepegawaian.Mr_pasangan.view'; changed = True
            if riwayat_pasangan.url_name != 'manajemen_data_kepegawaian:mr_pasangan_list':
                riwayat_pasangan.url_name = 'manajemen_data_kepegawaian:mr_pasangan_list'; changed = True
            if riwayat_pasangan.icon != 'fas fa-user-friends':
                riwayat_pasangan.icon = 'fas fa-user-friends'; changed = True
            if riwayat_pasangan.type != 'module':
                riwayat_pasangan.type = 'module'; changed = True
            if (riwayat_pasangan.order or 0) != 5:
                riwayat_pasangan.order = 5; changed = True
            if (riwayat_pasangan.category or 0) != 5:
                riwayat_pasangan.category = 5; changed = True
            if riwayat_pasangan.parent_id != riwayat_group.id:
                riwayat_pasangan.parent = riwayat_group; changed = True
            if not riwayat_pasangan.is_active:
                riwayat_pasangan.is_active = True; changed = True
            if changed:
                riwayat_pasangan.save()
                self.stdout.write('  ✓ Updated: Kepegawaian → Riwayat → Riwayat Pasangan')

        riwayat_anak, created = MenuItem.objects.get_or_create(
            name='Riwayat Anak',
            parent=riwayat_group,
            defaults={
                'permission_key': 'kepegawaian.Mr_anak.view',
                'url_name': 'manajemen_data_kepegawaian:mr_anak_list',
                'icon': 'fas fa-child',
                'type': 'module',
                'order': 6,
                'category': 5,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Kepegawaian → Riwayat → Riwayat Anak')
        else:
            changed = False
            if riwayat_anak.permission_key != 'kepegawaian.Mr_anak.view':
                riwayat_anak.permission_key = 'kepegawaian.Mr_anak.view'; changed = True
            if riwayat_anak.url_name != 'manajemen_data_kepegawaian:mr_anak_list':
                riwayat_anak.url_name = 'manajemen_data_kepegawaian:mr_anak_list'; changed = True
            if riwayat_anak.icon != 'fas fa-child':
                riwayat_anak.icon = 'fas fa-child'; changed = True
            if riwayat_anak.type != 'module':
                riwayat_anak.type = 'module'; changed = True
            if (riwayat_anak.order or 0) != 6:
                riwayat_anak.order = 6; changed = True
            if (riwayat_anak.category or 0) != 5:
                riwayat_anak.category = 5; changed = True
            if riwayat_anak.parent_id != riwayat_group.id:
                riwayat_anak.parent = riwayat_group; changed = True
            if not riwayat_anak.is_active:
                riwayat_anak.is_active = True; changed = True
            if changed:
                riwayat_anak.save()
                self.stdout.write('  ✓ Updated: Kepegawaian → Riwayat → Riwayat Anak')

        diklat_struktural, created = MenuItem.objects.get_or_create(
            name='Diklat Struktural',
            parent=riwayat_group,
            defaults={
                'permission_key': 'kepegawaian.Mr_diklat_struktural.view',
                'url_name': 'manajemen_data_kepegawaian:mr_diklat_struktural_list',
                'icon': 'fas fa-chalkboard-teacher',
                'type': 'module',
                'order': 7,
                'category': 5,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Kepegawaian → Riwayat → Diklat Struktural')
        else:
            changed = False
            if diklat_struktural.permission_key != 'kepegawaian.Mr_diklat_struktural.view':
                diklat_struktural.permission_key = 'kepegawaian.Mr_diklat_struktural.view'; changed = True
            if diklat_struktural.url_name != 'manajemen_data_kepegawaian:mr_diklat_struktural_list':
                diklat_struktural.url_name = 'manajemen_data_kepegawaian:mr_diklat_struktural_list'; changed = True
            if diklat_struktural.icon != 'fas fa-chalkboard-teacher':
                diklat_struktural.icon = 'fas fa-chalkboard-teacher'; changed = True
            if diklat_struktural.type != 'module':
                diklat_struktural.type = 'module'; changed = True
            if (diklat_struktural.order or 0) != 7:
                diklat_struktural.order = 7; changed = True
            if (diklat_struktural.category or 0) != 5:
                diklat_struktural.category = 5; changed = True
            if diklat_struktural.parent_id != riwayat_group.id:
                diklat_struktural.parent = riwayat_group; changed = True
            if not diklat_struktural.is_active:
                diklat_struktural.is_active = True; changed = True
            if changed:
                diklat_struktural.save()
                self.stdout.write('  ✓ Updated: Kepegawaian → Riwayat → Diklat Struktural')

        diklat_fungsional, created = MenuItem.objects.get_or_create(
            name='Diklat Fungsional',
            parent=riwayat_group,
            defaults={
                'permission_key': 'kepegawaian.Mr_diklat_fungsional.view',
                'url_name': 'manajemen_data_kepegawaian:mr_diklat_fungsional_list',
                'icon': 'fas fa-chalkboard',
                'type': 'module',
                'order': 8,
                'category': 5,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Kepegawaian → Riwayat → Diklat Fungsional')
        else:
            changed = False
            if diklat_fungsional.permission_key != 'kepegawaian.Mr_diklat_fungsional.view':
                diklat_fungsional.permission_key = 'kepegawaian.Mr_diklat_fungsional.view'; changed = True
            if diklat_fungsional.url_name != 'manajemen_data_kepegawaian:mr_diklat_fungsional_list':
                diklat_fungsional.url_name = 'manajemen_data_kepegawaian:mr_diklat_fungsional_list'; changed = True
            if diklat_fungsional.icon != 'fas fa-chalkboard':
                diklat_fungsional.icon = 'fas fa-chalkboard'; changed = True
            if diklat_fungsional.type != 'module':
                diklat_fungsional.type = 'module'; changed = True
            if (diklat_fungsional.order or 0) != 8:
                diklat_fungsional.order = 8; changed = True
            if (diklat_fungsional.category or 0) != 5:
                diklat_fungsional.category = 5; changed = True
            if diklat_fungsional.parent_id != riwayat_group.id:
                diklat_fungsional.parent = riwayat_group; changed = True
            if not diklat_fungsional.is_active:
                diklat_fungsional.is_active = True; changed = True
            if changed:
                diklat_fungsional.save()
                self.stdout.write('  ✓ Updated: Kepegawaian → Riwayat → Diklat Fungsional')

        diklat_teknis, created = MenuItem.objects.get_or_create(
            name='Diklat Teknis',
            parent=riwayat_group,
            defaults={
                'permission_key': 'kepegawaian.Mr_diklat_teknis.view',
                'url_name': 'manajemen_data_kepegawaian:mr_diklat_teknis_list',
                'icon': 'fas fa-tools',
                'type': 'module',
                'order': 9,
                'category': 5,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Kepegawaian → Riwayat → Diklat Teknis')
        else:
            changed = False
            if diklat_teknis.permission_key != 'kepegawaian.Mr_diklat_teknis.view':
                diklat_teknis.permission_key = 'kepegawaian.Mr_diklat_teknis.view'; changed = True
            if diklat_teknis.url_name != 'manajemen_data_kepegawaian:mr_diklat_teknis_list':
                diklat_teknis.url_name = 'manajemen_data_kepegawaian:mr_diklat_teknis_list'; changed = True
            if diklat_teknis.icon != 'fas fa-tools':
                diklat_teknis.icon = 'fas fa-tools'; changed = True
            if diklat_teknis.type != 'module':
                diklat_teknis.type = 'module'; changed = True
            if (diklat_teknis.order or 0) != 9:
                diklat_teknis.order = 9; changed = True
            if (diklat_teknis.category or 0) != 5:
                diklat_teknis.category = 5; changed = True
            if diklat_teknis.parent_id != riwayat_group.id:
                diklat_teknis.parent = riwayat_group; changed = True
            if not diklat_teknis.is_active:
                diklat_teknis.is_active = True; changed = True
            if changed:
                diklat_teknis.save()
                self.stdout.write('  ✓ Updated: Kepegawaian → Riwayat → Diklat Teknis')

        seminar, created = MenuItem.objects.get_or_create(
            name='Seminar',
            parent=riwayat_group,
            defaults={
                'permission_key': 'kepegawaian.Mr_seminar.view',
                'url_name': 'manajemen_data_kepegawaian:mr_seminar_list',
                'icon': 'fas fa-microphone-alt',
                'type': 'module',
                'order': 10,
                'category': 5,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Kepegawaian → Riwayat → Seminar')
        else:
            changed = False
            if seminar.permission_key != 'kepegawaian.Mr_seminar.view':
                seminar.permission_key = 'kepegawaian.Mr_seminar.view'; changed = True
            if seminar.url_name != 'manajemen_data_kepegawaian:mr_seminar_list':
                seminar.url_name = 'manajemen_data_kepegawaian:mr_seminar_list'; changed = True
            if seminar.icon != 'fas fa-microphone-alt':
                seminar.icon = 'fas fa-microphone-alt'; changed = True
            if seminar.type != 'module':
                seminar.type = 'module'; changed = True
            if (seminar.order or 0) != 10:
                seminar.order = 10; changed = True
            if (seminar.category or 0) != 5:
                seminar.category = 5; changed = True
            if seminar.parent_id != riwayat_group.id:
                seminar.parent = riwayat_group; changed = True
            if not seminar.is_active:
                seminar.is_active = True; changed = True
            if changed:
                seminar.save()
                self.stdout.write('  ✓ Updated: Kepegawaian → Riwayat → Seminar')

        angka_kredit, created = MenuItem.objects.get_or_create(
            name='Angka Kredit',
            parent=riwayat_group,
            defaults={
                'permission_key': 'kepegawaian.Mr_angka_kredit.view',
                'url_name': 'manajemen_data_kepegawaian:mr_angka_kredit_list',
                'icon': 'fas fa-calculator',
                'type': 'module',
                'order': 11,
                'category': 5,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Kepegawaian → Riwayat → Angka Kredit')
        else:
            changed = False
            if angka_kredit.permission_key != 'kepegawaian.Mr_angka_kredit.view':
                angka_kredit.permission_key = 'kepegawaian.Mr_angka_kredit.view'; changed = True
            if angka_kredit.url_name != 'manajemen_data_kepegawaian:mr_angka_kredit_list':
                angka_kredit.url_name = 'manajemen_data_kepegawaian:mr_angka_kredit_list'; changed = True
            if angka_kredit.icon != 'fas fa-calculator':
                angka_kredit.icon = 'fas fa-calculator'; changed = True
            if angka_kredit.type != 'module':
                angka_kredit.type = 'module'; changed = True
            if (angka_kredit.order or 0) != 11:
                angka_kredit.order = 11; changed = True
            if (angka_kredit.category or 0) != 5:
                angka_kredit.category = 5; changed = True
            if angka_kredit.parent_id != riwayat_group.id:
                angka_kredit.parent = riwayat_group; changed = True
            if not angka_kredit.is_active:
                angka_kredit.is_active = True; changed = True
            if changed:
                angka_kredit.save()
                self.stdout.write('  ✓ Updated: Kepegawaian → Riwayat → Angka Kredit')

        hukuman_disiplin, created = MenuItem.objects.get_or_create(
            name='Hukuman Disiplin',
            parent=riwayat_group,
            defaults={
                'permission_key': 'kepegawaian.Mr_hukuman_disiplin.view',
                'url_name': 'manajemen_data_kepegawaian:mr_hukuman_disiplin_list',
                'icon': 'fas fa-gavel',
                'type': 'module',
                'order': 12,
                'category': 5,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Kepegawaian → Riwayat → Hukuman Disiplin')
        else:
            changed = False
            if hukuman_disiplin.permission_key != 'kepegawaian.Mr_hukuman_disiplin.view':
                hukuman_disiplin.permission_key = 'kepegawaian.Mr_hukuman_disiplin.view'; changed = True
            if hukuman_disiplin.url_name != 'manajemen_data_kepegawaian:mr_hukuman_disiplin_list':
                hukuman_disiplin.url_name = 'manajemen_data_kepegawaian:mr_hukuman_disiplin_list'; changed = True
            if hukuman_disiplin.icon != 'fas fa-gavel':
                hukuman_disiplin.icon = 'fas fa-gavel'; changed = True
            if hukuman_disiplin.type != 'module':
                hukuman_disiplin.type = 'module'; changed = True
            if (hukuman_disiplin.order or 0) != 12:
                hukuman_disiplin.order = 12; changed = True
            if (hukuman_disiplin.category or 0) != 5:
                hukuman_disiplin.category = 5; changed = True
            if hukuman_disiplin.parent_id != riwayat_group.id:
                hukuman_disiplin.parent = riwayat_group; changed = True
            if not hukuman_disiplin.is_active:
                hukuman_disiplin.is_active = True; changed = True
            if changed:
                hukuman_disiplin.save()
                self.stdout.write('  ✓ Updated: Kepegawaian → Riwayat → Hukuman Disiplin')

        skp, created = MenuItem.objects.get_or_create(
            name='SKP',
            parent=riwayat_group,
            defaults={
                'permission_key': 'kepegawaian.Mr_skp.view',
                'url_name': 'manajemen_data_kepegawaian:mr_skp_list',
                'icon': 'fas fa-clipboard-check',
                'type': 'module',
                'order': 13,
                'category': 5,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Kepegawaian → Riwayat → SKP')
        else:
            changed = False
            if skp.permission_key != 'kepegawaian.Mr_skp.view':
                skp.permission_key = 'kepegawaian.Mr_skp.view'; changed = True
            if skp.url_name != 'manajemen_data_kepegawaian:mr_skp_list':
                skp.url_name = 'manajemen_data_kepegawaian:mr_skp_list'; changed = True
            if skp.icon != 'fas fa-clipboard-check':
                skp.icon = 'fas fa-clipboard-check'; changed = True
            if skp.type != 'module':
                skp.type = 'module'; changed = True
            if (skp.order or 0) != 13:
                skp.order = 13; changed = True
            if (skp.category or 0) != 5:
                skp.category = 5; changed = True
            if skp.parent_id != riwayat_group.id:
                skp.parent = riwayat_group; changed = True
            if not skp.is_active:
                skp.is_active = True; changed = True
            if changed:
                skp.save()
                self.stdout.write('  ✓ Updated: Kepegawaian → Riwayat → SKP')

        tugas_ln, created = MenuItem.objects.get_or_create(
            name='Tugas Ke Luar Negeri',
            parent=riwayat_group,
            defaults={
                'permission_key': 'kepegawaian.Mr_tugas_ln.view',
                'url_name': 'manajemen_data_kepegawaian:mr_tugas_ln_list',
                'icon': 'fas fa-plane-departure',
                'type': 'module',
                'order': 14,
                'category': 5,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Kepegawaian → Riwayat → Tugas Ke Luar Negeri')
        else:
            changed = False
            if tugas_ln.permission_key != 'kepegawaian.Mr_tugas_ln.view':
                tugas_ln.permission_key = 'kepegawaian.Mr_tugas_ln.view'; changed = True
            if tugas_ln.url_name != 'manajemen_data_kepegawaian:mr_tugas_ln_list':
                tugas_ln.url_name = 'manajemen_data_kepegawaian:mr_tugas_ln_list'; changed = True
            if tugas_ln.icon != 'fas fa-plane-departure':
                tugas_ln.icon = 'fas fa-plane-departure'; changed = True
            if tugas_ln.type != 'module':
                tugas_ln.type = 'module'; changed = True
            if (tugas_ln.order or 0) != 14:
                tugas_ln.order = 14; changed = True
            if (tugas_ln.category or 0) != 5:
                tugas_ln.category = 5; changed = True
            if tugas_ln.parent_id != riwayat_group.id:
                tugas_ln.parent = riwayat_group; changed = True
            if not tugas_ln.is_active:
                tugas_ln.is_active = True; changed = True
            if changed:
                tugas_ln.save()
                self.stdout.write('  ✓ Updated: Kepegawaian → Riwayat → Tugas Ke Luar Negeri')

        tanda_jasa, created = MenuItem.objects.get_or_create(
            name='Tanda Jasa',
            parent=riwayat_group,
            defaults={
                'permission_key': 'kepegawaian.Mr_tandajasa.view',
                'url_name': 'manajemen_data_kepegawaian:mr_tandajasa_list',
                'icon': 'fas fa-award',
                'type': 'module',
                'order': 15,
                'category': 5,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Kepegawaian → Riwayat → Tanda Jasa')
        else:
            changed = False
            if tanda_jasa.permission_key != 'kepegawaian.Mr_tandajasa.view':
                tanda_jasa.permission_key = 'kepegawaian.Mr_tandajasa.view'; changed = True
            if tanda_jasa.url_name != 'manajemen_data_kepegawaian:mr_tandajasa_list':
                tanda_jasa.url_name = 'manajemen_data_kepegawaian:mr_tandajasa_list'; changed = True
            if tanda_jasa.icon != 'fas fa-award':
                tanda_jasa.icon = 'fas fa-award'; changed = True
            if tanda_jasa.type != 'module':
                tanda_jasa.type = 'module'; changed = True
            if (tanda_jasa.order or 0) != 15:
                tanda_jasa.order = 15; changed = True
            if (tanda_jasa.category or 0) != 5:
                tanda_jasa.category = 5; changed = True
            if tanda_jasa.parent_id != riwayat_group.id:
                tanda_jasa.parent = riwayat_group; changed = True
            if not tanda_jasa.is_active:
                tanda_jasa.is_active = True; changed = True
            if changed:
                tanda_jasa.save()
                self.stdout.write('  ✓ Updated: Kepegawaian → Riwayat → Tanda Jasa')

        gaji_berkala, created = MenuItem.objects.get_or_create(
            name='Gaji Berkala',
            parent=riwayat_group,
            defaults={
                'permission_key': 'kepegawaian.Mr_gaji_berkala.view',
                'url_name': 'manajemen_data_kepegawaian:mr_gaji_berkala_list',
                'icon': 'fas fa-money-check-alt',
                'type': 'module',
                'order': 16,
                'category': 5,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Kepegawaian → Riwayat → Gaji Berkala')
        else:
            changed = False
            if gaji_berkala.permission_key != 'kepegawaian.Mr_gaji_berkala.view':
                gaji_berkala.permission_key = 'kepegawaian.Mr_gaji_berkala.view'; changed = True
            if gaji_berkala.url_name != 'manajemen_data_kepegawaian:mr_gaji_berkala_list':
                gaji_berkala.url_name = 'manajemen_data_kepegawaian:mr_gaji_berkala_list'; changed = True
            if gaji_berkala.icon != 'fas fa-money-check-alt':
                gaji_berkala.icon = 'fas fa-money-check-alt'; changed = True
            if gaji_berkala.type != 'module':
                gaji_berkala.type = 'module'; changed = True
            if (gaji_berkala.order or 0) != 16:
                gaji_berkala.order = 16; changed = True
            if (gaji_berkala.category or 0) != 5:
                gaji_berkala.category = 5; changed = True
            if gaji_berkala.parent_id != riwayat_group.id:
                gaji_berkala.parent = riwayat_group; changed = True
            if not gaji_berkala.is_active:
                gaji_berkala.is_active = True; changed = True
            if changed:
                gaji_berkala.save()
                self.stdout.write('  ✓ Updated: Kepegawaian → Riwayat → Gaji Berkala')

        kinerja, created = MenuItem.objects.get_or_create(
            name='Kinerja',
            parent=riwayat_group,
            defaults={
                'permission_key': 'kepegawaian.Mr_kinerja.view',
                'url_name': 'manajemen_data_kepegawaian:mr_kinerja_list',
                'icon': 'fas fa-chart-line',
                'type': 'module',
                'order': 17,
                'category': 5,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Kepegawaian → Riwayat → Kinerja')
        else:
            changed = False
            if kinerja.permission_key != 'kepegawaian.Mr_kinerja.view':
                kinerja.permission_key = 'kepegawaian.Mr_kinerja.view'; changed = True
            if kinerja.url_name != 'manajemen_data_kepegawaian:mr_kinerja_list':
                kinerja.url_name = 'manajemen_data_kepegawaian:mr_kinerja_list'; changed = True
            if kinerja.icon != 'fas fa-chart-line':
                kinerja.icon = 'fas fa-chart-line'; changed = True
            if kinerja.type != 'module':
                kinerja.type = 'module'; changed = True
            if (kinerja.order or 0) != 17:
                kinerja.order = 17; changed = True
            if (kinerja.category or 0) != 5:
                kinerja.category = 5; changed = True
            if kinerja.parent_id != riwayat_group.id:
                kinerja.parent = riwayat_group; changed = True
            if not kinerja.is_active:
                kinerja.is_active = True; changed = True
            if changed:
                kinerja.save()
                self.stdout.write('  ✓ Updated: Kepegawaian → Riwayat → Kinerja')

        assessment, created = MenuItem.objects.get_or_create(
            name='Assessment Pegawai',
            parent=riwayat_group,
            defaults={
                'permission_key': 'kepegawaian.Mr_assessment.view',
                'url_name': 'manajemen_data_kepegawaian:mr_assessment_list',
                'icon': 'fas fa-clipboard-check',
                'type': 'module',
                'order': 18,
                'category': 5,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Kepegawaian → Riwayat → Assessment Pegawai')
        else:
            changed = False
            if assessment.permission_key != 'kepegawaian.Mr_assessment.view':
                assessment.permission_key = 'kepegawaian.Mr_assessment.view'; changed = True
            if assessment.url_name != 'manajemen_data_kepegawaian:mr_assessment_list':
                assessment.url_name = 'manajemen_data_kepegawaian:mr_assessment_list'; changed = True
            if assessment.icon != 'fas fa-clipboard-check':
                assessment.icon = 'fas fa-clipboard-check'; changed = True
            if assessment.type != 'module':
                assessment.type = 'module'; changed = True
            if (assessment.order or 0) != 18:
                assessment.order = 18; changed = True
            if (assessment.category or 0) != 5:
                assessment.category = 5; changed = True
            if assessment.parent_id != riwayat_group.id:
                assessment.parent = riwayat_group; changed = True
            if not assessment.is_active:
                assessment.is_active = True; changed = True
            if changed:
                assessment.save()
                self.stdout.write('  ✓ Updated: Kepegawaian → Riwayat → Assessment Pegawai')

        struktural_group, created = MenuItem.objects.get_or_create(
            name='Struktural',
            parent=kepegawaian_group,
            defaults={
                'type': 'menuItem',
                'icon': 'fas fa-sitemap',
                'order': 3,
                'category': 5,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Kepegawaian → Struktural (group)')
        else:
            changed = False
            if struktural_group.type != 'menuItem':
                struktural_group.type = 'menuItem'; changed = True
            if struktural_group.icon != 'fas fa-sitemap':
                struktural_group.icon = 'fas fa-sitemap'; changed = True
            if (struktural_group.order or 0) != 3:
                struktural_group.order = 3; changed = True
            if (struktural_group.category or 0) != 5:
                struktural_group.category = 5; changed = True
            if struktural_group.parent_id != kepegawaian_group.id:
                struktural_group.parent = kepegawaian_group; changed = True
            if not struktural_group.is_active:
                struktural_group.is_active = True; changed = True
            if changed:
                struktural_group.save()
                self.stdout.write('  ✓ Updated: Kepegawaian → Struktural (group)')

        # Relasi Organisasi (category 5)
        relasi_org_group, created = _ensure_root_menu(
            name='Relasi Organisasi',
            legacy_names=[],
            defaults={
                'type': 'menuItem',
                'icon': 'fas fa-sitemap',
                'order': 4,
                'category': 5,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Relasi Organisasi (group)')
        else:
            changed = False
            if relasi_org_group.type != 'menuItem':
                relasi_org_group.type = 'menuItem'; changed = True
            if relasi_org_group.icon != 'fas fa-sitemap':
                relasi_org_group.icon = 'fas fa-sitemap'; changed = True
            if (relasi_org_group.order or 0) != 4:
                relasi_org_group.order = 4; changed = True
            if (relasi_org_group.category or 0) != 5:
                relasi_org_group.category = 5; changed = True
            if relasi_org_group.parent_id is not None:
                relasi_org_group.parent = None; changed = True
            if not relasi_org_group.is_active:
                relasi_org_group.is_active = True; changed = True
            if changed:
                relasi_org_group.save()
                self.stdout.write('  ✓ Updated: Relasi Organisasi (group)')

        unit_org_tabel_url = 'manajemen_relasi_organisasi:unit_organisasi_tabel_list'
        unit_org_qs = MenuItem.objects.filter(parent=relasi_org_group, url_name=unit_org_tabel_url)
        unit_org = unit_org_qs.first()
        created = False
        if not unit_org:
            unit_org = MenuItem.objects.create(
                name='Unit Organisasi Tabel',
                parent=relasi_org_group,
                permission_key='manajemen_relasi_organisasi.ma_re_or_unit_organisasi.view',
                url_name=unit_org_tabel_url,
                icon='fas fa-sitemap',
                type='module',
                order=1,
                category=5,
                is_active=True,
            )
            created = True
            created_count += 1
            self.stdout.write('  ✓ Created: Unit Organisasi Tabel')
        else:
            changed = False
            if unit_org.name != 'Unit Organisasi Tabel':
                unit_org.name = 'Unit Organisasi Tabel'; changed = True
            if unit_org.permission_key != 'manajemen_relasi_organisasi.ma_re_or_unit_organisasi.view':
                unit_org.permission_key = 'manajemen_relasi_organisasi.ma_re_or_unit_organisasi.view'; changed = True
            if unit_org.icon != 'fas fa-sitemap':
                unit_org.icon = 'fas fa-sitemap'; changed = True
            if unit_org.type != 'module':
                unit_org.type = 'module'; changed = True
            if (unit_org.order or 0) != 1:
                unit_org.order = 1; changed = True
            if (unit_org.category or 0) != 5:
                unit_org.category = 5; changed = True
            if unit_org.parent_id != relasi_org_group.id:
                unit_org.parent = relasi_org_group; changed = True
            if not unit_org.is_active:
                unit_org.is_active = True; changed = True
            if changed:
                unit_org.save()
                self.stdout.write('  ✓ Updated: Unit Organisasi Tabel')

        duplicates = MenuItem.objects.filter(parent=relasi_org_group, url_name=unit_org_tabel_url).exclude(id=unit_org.id)
        dup_count = duplicates.count()
        if dup_count:
            duplicates.delete()
            self.stdout.write(f'  ✓ Deleted duplicates: Unit Organisasi Tabel ({dup_count})')

        unit_org_struktural_url = 'manajemen_relasi_organisasi:unit_organisasi_struktural_list'
        unit_org_hirarki_qs = MenuItem.objects.filter(parent=relasi_org_group, url_name=unit_org_struktural_url)
        unit_org_hirarki = unit_org_hirarki_qs.first()
        created = False
        if not unit_org_hirarki:
            unit_org_hirarki = MenuItem.objects.create(
                name='Unit Organisasi Struktural',
                parent=relasi_org_group,
                permission_key='manajemen_relasi_organisasi.ma_re_or_unit_organisasi.view',
                url_name=unit_org_struktural_url,
                icon='fas fa-sitemap',
                type='module',
                order=2,
                category=5,
                is_active=True,
            )
            created = True
            created_count += 1
            self.stdout.write('  ✓ Created: Unit Organisasi Struktural')
        else:
            changed = False
            if unit_org_hirarki.name != 'Unit Organisasi Struktural':
                unit_org_hirarki.name = 'Unit Organisasi Struktural'; changed = True
            if unit_org_hirarki.permission_key != 'manajemen_relasi_organisasi.ma_re_or_unit_organisasi.view':
                unit_org_hirarki.permission_key = 'manajemen_relasi_organisasi.ma_re_or_unit_organisasi.view'; changed = True
            if unit_org_hirarki.icon != 'fas fa-sitemap':
                unit_org_hirarki.icon = 'fas fa-sitemap'; changed = True
            if unit_org_hirarki.type != 'module':
                unit_org_hirarki.type = 'module'; changed = True
            if (unit_org_hirarki.order or 0) != 2:
                unit_org_hirarki.order = 2; changed = True
            if (unit_org_hirarki.category or 0) != 5:
                unit_org_hirarki.category = 5; changed = True
            if unit_org_hirarki.parent_id != relasi_org_group.id:
                unit_org_hirarki.parent = relasi_org_group; changed = True
            if not unit_org_hirarki.is_active:
                unit_org_hirarki.is_active = True; changed = True
            if changed:
                unit_org_hirarki.save()
                self.stdout.write('  ✓ Updated: Unit Organisasi Struktural')

        duplicates = MenuItem.objects.filter(parent=relasi_org_group, url_name=unit_org_struktural_url).exclude(id=unit_org_hirarki.id)
        dup_count = duplicates.count()
        if dup_count:
            duplicates.delete()
            self.stdout.write(f'  ✓ Deleted duplicates: Unit Organisasi Struktural ({dup_count})')

        jabatan_struktural_tabel_url = 'manajemen_relasi_organisasi:jabatan_struktural_tabel_list'
        jabatan_qs = MenuItem.objects.filter(parent=relasi_org_group, url_name=jabatan_struktural_tabel_url)
        jabatan_item = jabatan_qs.first()
        created = False
        if not jabatan_item:
            jabatan_item = MenuItem.objects.create(
                name='Jabatan Struktural Tabel',
                parent=relasi_org_group,
                permission_key='manajemen_relasi_organisasi.ma_re_or_jabatan_struktural.view',
                url_name=jabatan_struktural_tabel_url,
                icon='fas fa-briefcase',
                type='module',
                order=3,
                category=5,
                is_active=True,
            )
            created = True
            created_count += 1
            self.stdout.write('  ✓ Created: Jabatan Struktural Tabel')
        else:
            changed = False
            if jabatan_item.name != 'Jabatan Struktural Tabel':
                jabatan_item.name = 'Jabatan Struktural Tabel'; changed = True
            if jabatan_item.permission_key != 'manajemen_relasi_organisasi.ma_re_or_jabatan_struktural.view':
                jabatan_item.permission_key = 'manajemen_relasi_organisasi.ma_re_or_jabatan_struktural.view'; changed = True
            if jabatan_item.icon != 'fas fa-briefcase':
                jabatan_item.icon = 'fas fa-briefcase'; changed = True
            if jabatan_item.type != 'module':
                jabatan_item.type = 'module'; changed = True
            if (jabatan_item.order or 0) != 3:
                jabatan_item.order = 3; changed = True
            if (jabatan_item.category or 0) != 5:
                jabatan_item.category = 5; changed = True
            if jabatan_item.parent_id != relasi_org_group.id:
                jabatan_item.parent = relasi_org_group; changed = True
            if not jabatan_item.is_active:
                jabatan_item.is_active = True; changed = True
            if changed:
                jabatan_item.save()
                self.stdout.write('  ✓ Updated: Jabatan Struktural Tabel')

        duplicates = MenuItem.objects.filter(parent=relasi_org_group, url_name=jabatan_struktural_tabel_url).exclude(id=jabatan_item.id)
        dup_count = duplicates.count()
        if dup_count:
            duplicates.delete()
            self.stdout.write(f'  ✓ Deleted duplicates: Jabatan Struktural Tabel ({dup_count})')

        jabatan_struktural_tree_url = 'manajemen_relasi_organisasi:jabatan_struktural_tree_list'
        jabatan_tree_qs = MenuItem.objects.filter(parent=relasi_org_group, url_name=jabatan_struktural_tree_url)
        jabatan_tree_item = jabatan_tree_qs.first()
        created = False
        if not jabatan_tree_item:
            jabatan_tree_item = MenuItem.objects.create(
                name='Jabatan Struktural Tree',
                parent=relasi_org_group,
                permission_key='manajemen_relasi_organisasi.ma_re_or_jabatan_struktural.view',
                url_name=jabatan_struktural_tree_url,
                icon='fas fa-sitemap',
                type='module',
                order=4,
                category=5,
                is_active=True,
            )
            created = True
            created_count += 1
            self.stdout.write('  ✓ Created: Jabatan Struktural Tree')
        else:
            changed = False
            if jabatan_tree_item.name != 'Jabatan Struktural Tree':
                jabatan_tree_item.name = 'Jabatan Struktural Tree'; changed = True
            if jabatan_tree_item.permission_key != 'manajemen_relasi_organisasi.ma_re_or_jabatan_struktural.view':
                jabatan_tree_item.permission_key = 'manajemen_relasi_organisasi.ma_re_or_jabatan_struktural.view'; changed = True
            if jabatan_tree_item.icon != 'fas fa-sitemap':
                jabatan_tree_item.icon = 'fas fa-sitemap'; changed = True
            if jabatan_tree_item.type != 'module':
                jabatan_tree_item.type = 'module'; changed = True
            if (jabatan_tree_item.order or 0) != 4:
                jabatan_tree_item.order = 4; changed = True
            if (jabatan_tree_item.category or 0) != 5:
                jabatan_tree_item.category = 5; changed = True
            if jabatan_tree_item.parent_id != relasi_org_group.id:
                jabatan_tree_item.parent = relasi_org_group; changed = True
            if not jabatan_tree_item.is_active:
                jabatan_tree_item.is_active = True; changed = True
            if changed:
                jabatan_tree_item.save()
                self.stdout.write('  ✓ Updated: Jabatan Struktural Tree')

        duplicates = MenuItem.objects.filter(parent=relasi_org_group, url_name=jabatan_struktural_tree_url).exclude(id=jabatan_tree_item.id)
        dup_count = duplicates.count()
        if dup_count:
            duplicates.delete()
            self.stdout.write(f'  ✓ Deleted duplicates: Jabatan Struktural Tree ({dup_count})')

        jabatan_non_struktural_url = 'manajemen_relasi_organisasi:jabatan_non_struktural_list'
        jabatan_non_qs = MenuItem.objects.filter(parent=relasi_org_group, url_name=jabatan_non_struktural_url)
        jabatan_non_item = jabatan_non_qs.first()
        created = False
        if not jabatan_non_item:
            jabatan_non_item = MenuItem.objects.create(
                name='Jabatan Non Struktural',
                parent=relasi_org_group,
                permission_key='manajemen_relasi_organisasi.ma_re_or_jabatan_non_struktural.view',
                url_name=jabatan_non_struktural_url,
                icon='fas fa-user-tag',
                type='module',
                order=5,
                category=5,
                is_active=True,
            )
            created = True
            created_count += 1
            self.stdout.write('  ✓ Created: Jabatan Non Struktural')
        else:
            changed = False
            if jabatan_non_item.name != 'Jabatan Non Struktural':
                jabatan_non_item.name = 'Jabatan Non Struktural'; changed = True
            if jabatan_non_item.permission_key != 'manajemen_relasi_organisasi.ma_re_or_jabatan_non_struktural.view':
                jabatan_non_item.permission_key = 'manajemen_relasi_organisasi.ma_re_or_jabatan_non_struktural.view'; changed = True
            if jabatan_non_item.icon != 'fas fa-user-tag':
                jabatan_non_item.icon = 'fas fa-user-tag'; changed = True
            if jabatan_non_item.type != 'module':
                jabatan_non_item.type = 'module'; changed = True
            if (jabatan_non_item.order or 0) != 5:
                jabatan_non_item.order = 5; changed = True
            if (jabatan_non_item.category or 0) != 5:
                jabatan_non_item.category = 5; changed = True
            if jabatan_non_item.parent_id != relasi_org_group.id:
                jabatan_non_item.parent = relasi_org_group; changed = True
            if not jabatan_non_item.is_active:
                jabatan_non_item.is_active = True; changed = True
            if changed:
                jabatan_non_item.save()
                self.stdout.write('  ✓ Updated: Jabatan Non Struktural')

        duplicates = MenuItem.objects.filter(parent=relasi_org_group, url_name=jabatan_non_struktural_url).exclude(id=jabatan_non_item.id)
        dup_count = duplicates.count()
        if dup_count:
            duplicates.delete()
            self.stdout.write(f'  ✓ Deleted duplicates: Jabatan Non Struktural ({dup_count})')

        legacy_urls = [
            'manajemen_relasi_organisasi:unit_organisasi_list',
            'manajemen_relasi_organisasi:unit_organisasi_hirarki',
        ]
        legacy = MenuItem.objects.filter(parent=relasi_org_group, url_name__in=legacy_urls)
        legacy_count = legacy.count()
        if legacy_count:
            legacy.delete()
            self.stdout.write(f'  ✓ Deleted legacy menus: Unit Organisasi ({legacy_count})')

        bkn_lokasi_kerja_url = 'manajemen_referensi_data_bkn:bkn_lokasi_kerja_list'
        bkn_lokasi_kerja_qs = MenuItem.objects.filter(parent=manajemen_bkn_group, url_name=bkn_lokasi_kerja_url)
        bkn_lokasi_kerja = bkn_lokasi_kerja_qs.first()
        created = False
        if not bkn_lokasi_kerja:
            bkn_lokasi_kerja = MenuItem.objects.create(
                name='Lokasi Kerja',
                parent=manajemen_bkn_group,
                permission_key='manajemen_referensi_data_bkn.bkn_lokasi_kerja.view',
                url_name=bkn_lokasi_kerja_url,
                icon='fas fa-map-marker-alt',
                type='module',
                order=1,
                category=1,
                is_active=True,
            )
            created = True
            created_count += 1
            self.stdout.write('  ✓ Created: Lokasi Kerja')
        else:
            changed = False
            if bkn_lokasi_kerja.name != 'Lokasi Kerja':
                bkn_lokasi_kerja.name = 'Lokasi Kerja'; changed = True
            if bkn_lokasi_kerja.permission_key != 'manajemen_referensi_data_bkn.bkn_lokasi_kerja.view':
                bkn_lokasi_kerja.permission_key = 'manajemen_referensi_data_bkn.bkn_lokasi_kerja.view'; changed = True
            if bkn_lokasi_kerja.icon != 'fas fa-map-marker-alt':
                bkn_lokasi_kerja.icon = 'fas fa-map-marker-alt'; changed = True
            if bkn_lokasi_kerja.type != 'module':
                bkn_lokasi_kerja.type = 'module'; changed = True
            if (bkn_lokasi_kerja.order or 0) != 1:
                bkn_lokasi_kerja.order = 1; changed = True
            if (bkn_lokasi_kerja.category or 0) != 1:
                bkn_lokasi_kerja.category = 1; changed = True
            if bkn_lokasi_kerja.parent_id != manajemen_bkn_group.id:
                bkn_lokasi_kerja.parent = manajemen_bkn_group; changed = True
            if not bkn_lokasi_kerja.is_active:
                bkn_lokasi_kerja.is_active = True; changed = True
            if changed:
                bkn_lokasi_kerja.save()
                self.stdout.write('  ✓ Updated: Lokasi Kerja')

        duplicates = MenuItem.objects.filter(parent=manajemen_bkn_group, url_name=bkn_lokasi_kerja_url).exclude(id=bkn_lokasi_kerja.id)
        dup_count = duplicates.count()
        if dup_count:
            duplicates.delete()
            self.stdout.write(f'  ✓ Deleted duplicates: Lokasi Kerja ({dup_count})')

        bkn_alasan_hukuman_url = 'manajemen_referensi_data_bkn:bkn_alasan_hukuman_list'
        bkn_alasan_hukuman_qs = MenuItem.objects.filter(parent=manajemen_bkn_group, url_name=bkn_alasan_hukuman_url)
        bkn_alasan_hukuman = bkn_alasan_hukuman_qs.first()
        created = False
        if not bkn_alasan_hukuman:
            bkn_alasan_hukuman = MenuItem.objects.create(
                name='Alasan Hukuman',
                parent=manajemen_bkn_group,
                permission_key='manajemen_referensi_data_bkn.bkn_alasan_hukuman.view',
                url_name=bkn_alasan_hukuman_url,
                icon='fas fa-gavel',
                type='module',
                order=2,
                category=1,
                is_active=True,
            )
            created = True
            created_count += 1
            self.stdout.write('  ✓ Created: Alasan Hukuman')
        else:
            changed = False
            if bkn_alasan_hukuman.name != 'Alasan Hukuman':
                bkn_alasan_hukuman.name = 'Alasan Hukuman'; changed = True
            if bkn_alasan_hukuman.permission_key != 'manajemen_referensi_data_bkn.bkn_alasan_hukuman.view':
                bkn_alasan_hukuman.permission_key = 'manajemen_referensi_data_bkn.bkn_alasan_hukuman.view'; changed = True
            if bkn_alasan_hukuman.icon != 'fas fa-gavel':
                bkn_alasan_hukuman.icon = 'fas fa-gavel'; changed = True
            if bkn_alasan_hukuman.type != 'module':
                bkn_alasan_hukuman.type = 'module'; changed = True
            if (bkn_alasan_hukuman.order or 0) != 2:
                bkn_alasan_hukuman.order = 2; changed = True
            if (bkn_alasan_hukuman.category or 0) != 1:
                bkn_alasan_hukuman.category = 1; changed = True
            if bkn_alasan_hukuman.parent_id != manajemen_bkn_group.id:
                bkn_alasan_hukuman.parent = manajemen_bkn_group; changed = True
            if not bkn_alasan_hukuman.is_active:
                bkn_alasan_hukuman.is_active = True; changed = True
            if changed:
                bkn_alasan_hukuman.save()
                self.stdout.write('  ✓ Updated: Alasan Hukuman')

        duplicates = MenuItem.objects.filter(parent=manajemen_bkn_group, url_name=bkn_alasan_hukuman_url).exclude(id=bkn_alasan_hukuman.id)
        dup_count = duplicates.count()
        if dup_count:
            duplicates.delete()
            self.stdout.write(f'  ✓ Deleted duplicates: Alasan Hukuman ({dup_count})')

        bkn_jenis_hukuman_url = 'manajemen_referensi_data_bkn:bkn_jenis_hukuman_list'
        bkn_jenis_hukuman_qs = MenuItem.objects.filter(parent=manajemen_bkn_group, url_name=bkn_jenis_hukuman_url)
        bkn_jenis_hukuman = bkn_jenis_hukuman_qs.first()
        created = False
        if not bkn_jenis_hukuman:
            bkn_jenis_hukuman = MenuItem.objects.create(
                name='Jenis Hukuman',
                parent=manajemen_bkn_group,
                permission_key='manajemen_referensi_data_bkn.bkn_jenis_hukuman.view',
                url_name=bkn_jenis_hukuman_url,
                icon='fas fa-gavel',
                type='module',
                order=3,
                category=1,
                is_active=True,
            )
            created = True
            created_count += 1
            self.stdout.write('  ✓ Created: Jenis Hukuman')
        else:
            changed = False
            if bkn_jenis_hukuman.name != 'Jenis Hukuman':
                bkn_jenis_hukuman.name = 'Jenis Hukuman'; changed = True
            if bkn_jenis_hukuman.permission_key != 'manajemen_referensi_data_bkn.bkn_jenis_hukuman.view':
                bkn_jenis_hukuman.permission_key = 'manajemen_referensi_data_bkn.bkn_jenis_hukuman.view'; changed = True
            if bkn_jenis_hukuman.icon != 'fas fa-gavel':
                bkn_jenis_hukuman.icon = 'fas fa-gavel'; changed = True
            if bkn_jenis_hukuman.type != 'module':
                bkn_jenis_hukuman.type = 'module'; changed = True
            if (bkn_jenis_hukuman.order or 0) != 3:
                bkn_jenis_hukuman.order = 3; changed = True
            if (bkn_jenis_hukuman.category or 0) != 1:
                bkn_jenis_hukuman.category = 1; changed = True
            if bkn_jenis_hukuman.parent_id != manajemen_bkn_group.id:
                bkn_jenis_hukuman.parent = manajemen_bkn_group; changed = True
            if not bkn_jenis_hukuman.is_active:
                bkn_jenis_hukuman.is_active = True; changed = True
            if changed:
                bkn_jenis_hukuman.save()
                self.stdout.write('  ✓ Updated: Jenis Hukuman')

        duplicates = MenuItem.objects.filter(parent=manajemen_bkn_group, url_name=bkn_jenis_hukuman_url).exclude(id=bkn_jenis_hukuman.id)
        dup_count = duplicates.count()
        if dup_count:
            duplicates.delete()
            self.stdout.write(f'  ✓ Deleted duplicates: Jenis Hukuman ({dup_count})')

        bkn_tingkat_hukdis_url = 'manajemen_referensi_data_bkn:bkn_tingkat_hukdis_list'
        bkn_tingkat_hukdis_qs = MenuItem.objects.filter(parent=manajemen_bkn_group, url_name=bkn_tingkat_hukdis_url)
        bkn_tingkat_hukdis = bkn_tingkat_hukdis_qs.first()
        created = False
        if not bkn_tingkat_hukdis:
            bkn_tingkat_hukdis = MenuItem.objects.create(
                name='Tingkat Hukuman Disiplin',
                parent=manajemen_bkn_group,
                permission_key='manajemen_referensi_data_bkn.bkn_tingkat_hukdis.view',
                url_name=bkn_tingkat_hukdis_url,
                icon='fas fa-gavel',
                type='module',
                order=4,
                category=1,
                is_active=True,
            )
            created = True
            created_count += 1
            self.stdout.write('  ✓ Created: Tingkat Hukuman Disiplin')
        else:
            changed = False
            if bkn_tingkat_hukdis.name != 'Tingkat Hukuman Disiplin':
                bkn_tingkat_hukdis.name = 'Tingkat Hukuman Disiplin'; changed = True
            if bkn_tingkat_hukdis.permission_key != 'manajemen_referensi_data_bkn.bkn_tingkat_hukdis.view':
                bkn_tingkat_hukdis.permission_key = 'manajemen_referensi_data_bkn.bkn_tingkat_hukdis.view'; changed = True
            if bkn_tingkat_hukdis.icon != 'fas fa-gavel':
                bkn_tingkat_hukdis.icon = 'fas fa-gavel'; changed = True
            if bkn_tingkat_hukdis.type != 'module':
                bkn_tingkat_hukdis.type = 'module'; changed = True
            if (bkn_tingkat_hukdis.order or 0) != 4:
                bkn_tingkat_hukdis.order = 4; changed = True
            if (bkn_tingkat_hukdis.category or 0) != 1:
                bkn_tingkat_hukdis.category = 1; changed = True
            if bkn_tingkat_hukdis.parent_id != manajemen_bkn_group.id:
                bkn_tingkat_hukdis.parent = manajemen_bkn_group; changed = True
            if not bkn_tingkat_hukdis.is_active:
                bkn_tingkat_hukdis.is_active = True; changed = True
            if changed:
                bkn_tingkat_hukdis.save()
                self.stdout.write('  ✓ Updated: Tingkat Hukuman Disiplin')

        duplicates = MenuItem.objects.filter(parent=manajemen_bkn_group, url_name=bkn_tingkat_hukdis_url).exclude(id=bkn_tingkat_hukdis.id)
        dup_count = duplicates.count()
        if dup_count:
            duplicates.delete()
            self.stdout.write(f'  ✓ Deleted duplicates: Tingkat Hukuman Disiplin ({dup_count})')

        bkn_nomorpp_hukdis_url = 'manajemen_referensi_data_bkn:bkn_nomorpp_hukdis_list'
        bkn_nomorpp_hukdis_qs = MenuItem.objects.filter(parent=manajemen_bkn_group, url_name=bkn_nomorpp_hukdis_url)
        bkn_nomorpp_hukdis = bkn_nomorpp_hukdis_qs.first()
        created = False
        if not bkn_nomorpp_hukdis:
            bkn_nomorpp_hukdis = MenuItem.objects.create(
                name='Nomor PP Hukdis',
                parent=manajemen_bkn_group,
                permission_key='manajemen_referensi_data_bkn.bkn_nomorpp_hukdis.view',
                url_name=bkn_nomorpp_hukdis_url,
                icon='fas fa-file-alt',
                type='module',
                order=5,
                category=1,
                is_active=True,
            )
            created = True
            created_count += 1
            self.stdout.write('  ✓ Created: Nomor PP Hukdis')
        else:
            changed = False
            if bkn_nomorpp_hukdis.name != 'Nomor PP Hukdis':
                bkn_nomorpp_hukdis.name = 'Nomor PP Hukdis'; changed = True
            if bkn_nomorpp_hukdis.permission_key != 'manajemen_referensi_data_bkn.bkn_nomorpp_hukdis.view':
                bkn_nomorpp_hukdis.permission_key = 'manajemen_referensi_data_bkn.bkn_nomorpp_hukdis.view'; changed = True
            if bkn_nomorpp_hukdis.icon != 'fas fa-file-alt':
                bkn_nomorpp_hukdis.icon = 'fas fa-file-alt'; changed = True
            if bkn_nomorpp_hukdis.type != 'module':
                bkn_nomorpp_hukdis.type = 'module'; changed = True
            if (bkn_nomorpp_hukdis.order or 0) != 5:
                bkn_nomorpp_hukdis.order = 5; changed = True
            if (bkn_nomorpp_hukdis.category or 0) != 1:
                bkn_nomorpp_hukdis.category = 1; changed = True
            if bkn_nomorpp_hukdis.parent_id != manajemen_bkn_group.id:
                bkn_nomorpp_hukdis.parent = manajemen_bkn_group; changed = True
            if not bkn_nomorpp_hukdis.is_active:
                bkn_nomorpp_hukdis.is_active = True; changed = True
            if changed:
                bkn_nomorpp_hukdis.save()
                self.stdout.write('  ✓ Updated: Nomor PP Hukdis')

        duplicates = MenuItem.objects.filter(parent=manajemen_bkn_group, url_name=bkn_nomorpp_hukdis_url).exclude(id=bkn_nomorpp_hukdis.id)
        dup_count = duplicates.count()
        if dup_count:
            duplicates.delete()
            self.stdout.write(f'  ✓ Deleted duplicates: Nomor PP Hukdis ({dup_count})')

        bkn_jabatan_fungsional_url = 'manajemen_referensi_data_bkn:bkn_jabatan_fungsional_list'
        bkn_jabatan_fungsional_qs = MenuItem.objects.filter(parent=manajemen_bkn_group, url_name=bkn_jabatan_fungsional_url)
        bkn_jabatan_fungsional = bkn_jabatan_fungsional_qs.first()
        created = False
        if not bkn_jabatan_fungsional:
            bkn_jabatan_fungsional = MenuItem.objects.create(
                name='Jabatan Fungsional',
                parent=manajemen_bkn_group,
                permission_key='manajemen_referensi_data_bkn.bkn_jabatan_fungsional.view',
                url_name=bkn_jabatan_fungsional_url,
                icon='fas fa-id-badge',
                type='module',
                order=6,
                category=1,
                is_active=True,
            )
            created = True
            created_count += 1
            self.stdout.write('  ✓ Created: Jabatan Fungsional')
        else:
            changed = False
            if bkn_jabatan_fungsional.name != 'Jabatan Fungsional':
                bkn_jabatan_fungsional.name = 'Jabatan Fungsional'; changed = True
            if bkn_jabatan_fungsional.permission_key != 'manajemen_referensi_data_bkn.bkn_jabatan_fungsional.view':
                bkn_jabatan_fungsional.permission_key = 'manajemen_referensi_data_bkn.bkn_jabatan_fungsional.view'; changed = True
            if bkn_jabatan_fungsional.icon != 'fas fa-id-badge':
                bkn_jabatan_fungsional.icon = 'fas fa-id-badge'; changed = True
            if bkn_jabatan_fungsional.type != 'module':
                bkn_jabatan_fungsional.type = 'module'; changed = True
            if (bkn_jabatan_fungsional.order or 0) != 6:
                bkn_jabatan_fungsional.order = 6; changed = True
            if (bkn_jabatan_fungsional.category or 0) != 1:
                bkn_jabatan_fungsional.category = 1; changed = True
            if bkn_jabatan_fungsional.parent_id != manajemen_bkn_group.id:
                bkn_jabatan_fungsional.parent = manajemen_bkn_group; changed = True
            if not bkn_jabatan_fungsional.is_active:
                bkn_jabatan_fungsional.is_active = True; changed = True
            if changed:
                bkn_jabatan_fungsional.save()
                self.stdout.write('  ✓ Updated: Jabatan Fungsional')

        duplicates = MenuItem.objects.filter(parent=manajemen_bkn_group, url_name=bkn_jabatan_fungsional_url).exclude(id=bkn_jabatan_fungsional.id)
        dup_count = duplicates.count()
        if dup_count:
            duplicates.delete()
            self.stdout.write(f'  ✓ Deleted duplicates: Jabatan Fungsional ({dup_count})')

        bkn_jenis_kenaikan_pangkat_url = 'manajemen_referensi_data_bkn:bkn_jenis_kenaikan_pangkat_list'
        bkn_jenis_kenaikan_pangkat_qs = MenuItem.objects.filter(parent=manajemen_bkn_group, url_name=bkn_jenis_kenaikan_pangkat_url)
        bkn_jenis_kenaikan_pangkat = bkn_jenis_kenaikan_pangkat_qs.first()
        created = False
        if not bkn_jenis_kenaikan_pangkat:
            bkn_jenis_kenaikan_pangkat = MenuItem.objects.create(
                name='Jenis Kenaikan Pangkat',
                parent=manajemen_bkn_group,
                permission_key='manajemen_referensi_data_bkn.bkn_jenis_kenaikan_pangkat.view',
                url_name=bkn_jenis_kenaikan_pangkat_url,
                icon='fas fa-level-up-alt',
                type='module',
                order=7,
                category=1,
                is_active=True,
            )
            created = True
            created_count += 1
            self.stdout.write('  ✓ Created: Jenis Kenaikan Pangkat')
        else:
            changed = False
            if bkn_jenis_kenaikan_pangkat.name != 'Jenis Kenaikan Pangkat':
                bkn_jenis_kenaikan_pangkat.name = 'Jenis Kenaikan Pangkat'; changed = True
            if bkn_jenis_kenaikan_pangkat.permission_key != 'manajemen_referensi_data_bkn.bkn_jenis_kenaikan_pangkat.view':
                bkn_jenis_kenaikan_pangkat.permission_key = 'manajemen_referensi_data_bkn.bkn_jenis_kenaikan_pangkat.view'; changed = True
            if bkn_jenis_kenaikan_pangkat.icon != 'fas fa-level-up-alt':
                bkn_jenis_kenaikan_pangkat.icon = 'fas fa-level-up-alt'; changed = True
            if bkn_jenis_kenaikan_pangkat.type != 'module':
                bkn_jenis_kenaikan_pangkat.type = 'module'; changed = True
            if (bkn_jenis_kenaikan_pangkat.order or 0) != 7:
                bkn_jenis_kenaikan_pangkat.order = 7; changed = True
            if (bkn_jenis_kenaikan_pangkat.category or 0) != 1:
                bkn_jenis_kenaikan_pangkat.category = 1; changed = True
            if bkn_jenis_kenaikan_pangkat.parent_id != manajemen_bkn_group.id:
                bkn_jenis_kenaikan_pangkat.parent = manajemen_bkn_group; changed = True
            if not bkn_jenis_kenaikan_pangkat.is_active:
                bkn_jenis_kenaikan_pangkat.is_active = True; changed = True
            if changed:
                bkn_jenis_kenaikan_pangkat.save()
                self.stdout.write('  ✓ Updated: Jenis Kenaikan Pangkat')

        duplicates = MenuItem.objects.filter(parent=manajemen_bkn_group, url_name=bkn_jenis_kenaikan_pangkat_url).exclude(id=bkn_jenis_kenaikan_pangkat.id)
        dup_count = duplicates.count()
        if dup_count:
            duplicates.delete()
            self.stdout.write(f'  ✓ Deleted duplicates: Jenis Kenaikan Pangkat ({dup_count})')

        bkn_jenis_diklat_url = 'manajemen_referensi_data_bkn:bkn_jenis_diklat_list'
        bkn_jenis_diklat_qs = MenuItem.objects.filter(parent=manajemen_bkn_group, url_name=bkn_jenis_diklat_url)
        bkn_jenis_diklat = bkn_jenis_diklat_qs.first()
        if not bkn_jenis_diklat:
            bkn_jenis_diklat = MenuItem.objects.create(
                name='Jenis Diklat',
                parent=manajemen_bkn_group,
                permission_key='manajemen_referensi_data_bkn.bkn_jenis_diklat.view',
                url_name=bkn_jenis_diklat_url,
                icon='fas fa-chalkboard-teacher',
                type='module',
                order=8,
                category=1,
                is_active=True,
            )
            created_count += 1
            self.stdout.write('  ✓ Created: Jenis Diklat')
        else:
            changed = False
            if bkn_jenis_diklat.name != 'Jenis Diklat':
                bkn_jenis_diklat.name = 'Jenis Diklat'; changed = True
            if bkn_jenis_diklat.permission_key != 'manajemen_referensi_data_bkn.bkn_jenis_diklat.view':
                bkn_jenis_diklat.permission_key = 'manajemen_referensi_data_bkn.bkn_jenis_diklat.view'; changed = True
            if bkn_jenis_diklat.icon != 'fas fa-chalkboard-teacher':
                bkn_jenis_diklat.icon = 'fas fa-chalkboard-teacher'; changed = True
            if bkn_jenis_diklat.type != 'module':
                bkn_jenis_diklat.type = 'module'; changed = True
            if (bkn_jenis_diklat.order or 0) != 8:
                bkn_jenis_diklat.order = 8; changed = True
            if (bkn_jenis_diklat.category or 0) != 1:
                bkn_jenis_diklat.category = 1; changed = True
            if bkn_jenis_diklat.parent_id != manajemen_bkn_group.id:
                bkn_jenis_diklat.parent = manajemen_bkn_group; changed = True
            if not bkn_jenis_diklat.is_active:
                bkn_jenis_diklat.is_active = True; changed = True
            if changed:
                bkn_jenis_diklat.save()
                self.stdout.write('  ✓ Updated: Jenis Diklat')

        duplicates = MenuItem.objects.filter(parent=manajemen_bkn_group, url_name=bkn_jenis_diklat_url).exclude(id=bkn_jenis_diklat.id)
        dup_count = duplicates.count()
        if dup_count:
            duplicates.delete()
            self.stdout.write(f'  ✓ Deleted duplicates: Jenis Diklat ({dup_count})')

        bkn_daftar_kppn_url = 'manajemen_referensi_data_bkn:bkn_daftar_kppn_list'
        bkn_daftar_kppn_qs = MenuItem.objects.filter(parent=manajemen_bkn_group, url_name=bkn_daftar_kppn_url)
        bkn_daftar_kppn = bkn_daftar_kppn_qs.first()
        if not bkn_daftar_kppn:
            bkn_daftar_kppn = MenuItem.objects.create(
                name='Daftar KPPN',
                parent=manajemen_bkn_group,
                permission_key='manajemen_referensi_data_bkn.bkn_daftar_kppn.view',
                url_name=bkn_daftar_kppn_url,
                icon='fas fa-list',
                type='module',
                order=9,
                category=1,
                is_active=True,
            )
            created_count += 1
            self.stdout.write('  ✓ Created: Daftar KPPN')
        else:
            changed = False
            if bkn_daftar_kppn.name != 'Daftar KPPN':
                bkn_daftar_kppn.name = 'Daftar KPPN'; changed = True
            if bkn_daftar_kppn.permission_key != 'manajemen_referensi_data_bkn.bkn_daftar_kppn.view':
                bkn_daftar_kppn.permission_key = 'manajemen_referensi_data_bkn.bkn_daftar_kppn.view'; changed = True
            if bkn_daftar_kppn.icon != 'fas fa-list':
                bkn_daftar_kppn.icon = 'fas fa-list'; changed = True
            if bkn_daftar_kppn.type != 'module':
                bkn_daftar_kppn.type = 'module'; changed = True
            if (bkn_daftar_kppn.order or 0) != 9:
                bkn_daftar_kppn.order = 9; changed = True
            if (bkn_daftar_kppn.category or 0) != 1:
                bkn_daftar_kppn.category = 1; changed = True
            if bkn_daftar_kppn.parent_id != manajemen_bkn_group.id:
                bkn_daftar_kppn.parent = manajemen_bkn_group; changed = True
            if not bkn_daftar_kppn.is_active:
                bkn_daftar_kppn.is_active = True; changed = True
            if changed:
                bkn_daftar_kppn.save()
                self.stdout.write('  ✓ Updated: Daftar KPPN')

        duplicates = MenuItem.objects.filter(parent=manajemen_bkn_group, url_name=bkn_daftar_kppn_url).exclude(id=bkn_daftar_kppn.id)
        dup_count = duplicates.count()
        if dup_count:
            duplicates.delete()
            self.stdout.write(f'  ✓ Deleted duplicates: Daftar KPPN ({dup_count})')

        bkn_jenis_penghargaan_url = 'manajemen_referensi_data_bkn:bkn_jenis_penghargaan_list'
        bkn_jenis_penghargaan_qs = MenuItem.objects.filter(parent=manajemen_bkn_group, url_name=bkn_jenis_penghargaan_url)
        bkn_jenis_penghargaan = bkn_jenis_penghargaan_qs.first()
        if not bkn_jenis_penghargaan:
            bkn_jenis_penghargaan = MenuItem.objects.create(
                name='Jenis Penghargaan',
                parent=manajemen_bkn_group,
                permission_key='manajemen_referensi_data_bkn.bkn_jenis_penghargaan.view',
                url_name=bkn_jenis_penghargaan_url,
                icon='fas fa-award',
                type='module',
                order=10,
                category=1,
                is_active=True,
            )
            created_count += 1
            self.stdout.write('  ✓ Created: Jenis Penghargaan')
        else:
            changed = False
            if bkn_jenis_penghargaan.name != 'Jenis Penghargaan':
                bkn_jenis_penghargaan.name = 'Jenis Penghargaan'; changed = True
            if bkn_jenis_penghargaan.permission_key != 'manajemen_referensi_data_bkn.bkn_jenis_penghargaan.view':
                bkn_jenis_penghargaan.permission_key = 'manajemen_referensi_data_bkn.bkn_jenis_penghargaan.view'; changed = True
            if bkn_jenis_penghargaan.icon != 'fas fa-award':
                bkn_jenis_penghargaan.icon = 'fas fa-award'; changed = True
            if bkn_jenis_penghargaan.type != 'module':
                bkn_jenis_penghargaan.type = 'module'; changed = True
            if (bkn_jenis_penghargaan.order or 0) != 10:
                bkn_jenis_penghargaan.order = 10; changed = True
            if (bkn_jenis_penghargaan.category or 0) != 1:
                bkn_jenis_penghargaan.category = 1; changed = True
            if bkn_jenis_penghargaan.parent_id != manajemen_bkn_group.id:
                bkn_jenis_penghargaan.parent = manajemen_bkn_group; changed = True
            if not bkn_jenis_penghargaan.is_active:
                bkn_jenis_penghargaan.is_active = True; changed = True
            if changed:
                bkn_jenis_penghargaan.save()
                self.stdout.write('  ✓ Updated: Jenis Penghargaan')

        duplicates = MenuItem.objects.filter(parent=manajemen_bkn_group, url_name=bkn_jenis_penghargaan_url).exclude(id=bkn_jenis_penghargaan.id)
        dup_count = duplicates.count()
        if dup_count:
            duplicates.delete()
            self.stdout.write(f'  ✓ Deleted duplicates: Jenis Penghargaan ({dup_count})')

        bkn_jenis_mutasi_url = 'manajemen_referensi_data_bkn:bkn_jenis_mutasi_list'
        bkn_jenis_mutasi_qs = MenuItem.objects.filter(parent=manajemen_bkn_group, url_name=bkn_jenis_mutasi_url)
        bkn_jenis_mutasi = bkn_jenis_mutasi_qs.first()
        if not bkn_jenis_mutasi:
            bkn_jenis_mutasi = MenuItem.objects.create(
                name='Jenis Mutasi',
                parent=manajemen_bkn_group,
                permission_key='manajemen_referensi_data_bkn.bkn_jenis_mutasi.view',
                url_name=bkn_jenis_mutasi_url,
                icon='fas fa-exchange-alt',
                type='module',
                order=11,
                category=1,
                is_active=True,
            )
            created_count += 1
            self.stdout.write('  ✓ Created: Jenis Mutasi')
        else:
            changed = False
            if bkn_jenis_mutasi.name != 'Jenis Mutasi':
                bkn_jenis_mutasi.name = 'Jenis Mutasi'; changed = True
            if bkn_jenis_mutasi.permission_key != 'manajemen_referensi_data_bkn.bkn_jenis_mutasi.view':
                bkn_jenis_mutasi.permission_key = 'manajemen_referensi_data_bkn.bkn_jenis_mutasi.view'; changed = True
            if bkn_jenis_mutasi.icon != 'fas fa-exchange-alt':
                bkn_jenis_mutasi.icon = 'fas fa-exchange-alt'; changed = True
            if bkn_jenis_mutasi.type != 'module':
                bkn_jenis_mutasi.type = 'module'; changed = True
            if (bkn_jenis_mutasi.order or 0) != 11:
                bkn_jenis_mutasi.order = 11; changed = True
            if (bkn_jenis_mutasi.category or 0) != 1:
                bkn_jenis_mutasi.category = 1; changed = True
            if bkn_jenis_mutasi.parent_id != manajemen_bkn_group.id:
                bkn_jenis_mutasi.parent = manajemen_bkn_group; changed = True
            if not bkn_jenis_mutasi.is_active:
                bkn_jenis_mutasi.is_active = True; changed = True
            if changed:
                bkn_jenis_mutasi.save()
                self.stdout.write('  ✓ Updated: Jenis Mutasi')

        duplicates = MenuItem.objects.filter(parent=manajemen_bkn_group, url_name=bkn_jenis_mutasi_url).exclude(id=bkn_jenis_mutasi.id)
        dup_count = duplicates.count()
        if dup_count:
            duplicates.delete()
            self.stdout.write(f'  ✓ Deleted duplicates: Jenis Mutasi ({dup_count})')

        bkn_jenis_penugasan_url = 'manajemen_referensi_data_bkn:bkn_jenis_penugasan_list'
        bkn_jenis_penugasan_qs = MenuItem.objects.filter(parent=manajemen_bkn_group, url_name=bkn_jenis_penugasan_url)
        bkn_jenis_penugasan = bkn_jenis_penugasan_qs.first()
        if not bkn_jenis_penugasan:
            bkn_jenis_penugasan = MenuItem.objects.create(
                name='Jenis Penugasan',
                parent=manajemen_bkn_group,
                permission_key='manajemen_referensi_data_bkn.bkn_jenis_penugasan.view',
                url_name=bkn_jenis_penugasan_url,
                icon='fas fa-briefcase',
                type='module',
                order=12,
                category=1,
                is_active=True,
            )
            created_count += 1
            self.stdout.write('  ✓ Created: Jenis Penugasan')
        else:
            changed = False
            if bkn_jenis_penugasan.name != 'Jenis Penugasan':
                bkn_jenis_penugasan.name = 'Jenis Penugasan'; changed = True
            if bkn_jenis_penugasan.permission_key != 'manajemen_referensi_data_bkn.bkn_jenis_penugasan.view':
                bkn_jenis_penugasan.permission_key = 'manajemen_referensi_data_bkn.bkn_jenis_penugasan.view'; changed = True
            if bkn_jenis_penugasan.icon != 'fas fa-briefcase':
                bkn_jenis_penugasan.icon = 'fas fa-briefcase'; changed = True
            if bkn_jenis_penugasan.type != 'module':
                bkn_jenis_penugasan.type = 'module'; changed = True
            if (bkn_jenis_penugasan.order or 0) != 12:
                bkn_jenis_penugasan.order = 12; changed = True
            if (bkn_jenis_penugasan.category or 0) != 1:
                bkn_jenis_penugasan.category = 1; changed = True
            if bkn_jenis_penugasan.parent_id != manajemen_bkn_group.id:
                bkn_jenis_penugasan.parent = manajemen_bkn_group; changed = True
            if not bkn_jenis_penugasan.is_active:
                bkn_jenis_penugasan.is_active = True; changed = True
            if changed:
                bkn_jenis_penugasan.save()
                self.stdout.write('  ✓ Updated: Jenis Penugasan')

        duplicates = MenuItem.objects.filter(parent=manajemen_bkn_group, url_name=bkn_jenis_penugasan_url).exclude(id=bkn_jenis_penugasan.id)
        dup_count = duplicates.count()
        if dup_count:
            duplicates.delete()
            self.stdout.write(f'  ✓ Deleted duplicates: Jenis Penugasan ({dup_count})')

        bkn_sub_jabatan_url = 'manajemen_referensi_data_bkn:bkn_sub_jabatan_list'
        bkn_sub_jabatan_qs = MenuItem.objects.filter(parent=manajemen_bkn_group, url_name=bkn_sub_jabatan_url)
        bkn_sub_jabatan = bkn_sub_jabatan_qs.first()
        if not bkn_sub_jabatan:
            bkn_sub_jabatan = MenuItem.objects.create(
                name='Sub Jabatan',
                parent=manajemen_bkn_group,
                permission_key='manajemen_referensi_data_bkn.bkn_sub_jabatan.view',
                url_name=bkn_sub_jabatan_url,
                icon='fas fa-sitemap',
                type='module',
                order=13,
                category=1,
                is_active=True,
            )
            created_count += 1
            self.stdout.write('  ✓ Created: Sub Jabatan')
        else:
            changed = False
            if bkn_sub_jabatan.name != 'Sub Jabatan':
                bkn_sub_jabatan.name = 'Sub Jabatan'; changed = True
            if bkn_sub_jabatan.permission_key != 'manajemen_referensi_data_bkn.bkn_sub_jabatan.view':
                bkn_sub_jabatan.permission_key = 'manajemen_referensi_data_bkn.bkn_sub_jabatan.view'; changed = True
            if bkn_sub_jabatan.icon != 'fas fa-sitemap':
                bkn_sub_jabatan.icon = 'fas fa-sitemap'; changed = True
            if bkn_sub_jabatan.type != 'module':
                bkn_sub_jabatan.type = 'module'; changed = True
            if (bkn_sub_jabatan.order or 0) != 13:
                bkn_sub_jabatan.order = 13; changed = True
            if (bkn_sub_jabatan.category or 0) != 1:
                bkn_sub_jabatan.category = 1; changed = True
            if bkn_sub_jabatan.parent_id != manajemen_bkn_group.id:
                bkn_sub_jabatan.parent = manajemen_bkn_group; changed = True
            if not bkn_sub_jabatan.is_active:
                bkn_sub_jabatan.is_active = True; changed = True
            if changed:
                bkn_sub_jabatan.save()
                self.stdout.write('  ✓ Updated: Sub Jabatan')

        duplicates = MenuItem.objects.filter(parent=manajemen_bkn_group, url_name=bkn_sub_jabatan_url).exclude(id=bkn_sub_jabatan.id)
        dup_count = duplicates.count()
        if dup_count:
            duplicates.delete()
            self.stdout.write(f'  ✓ Deleted duplicates: Sub Jabatan ({dup_count})')

        ma_an_satuan_kerja, created = MenuItem.objects.get_or_create(
            name='Satuan Kerja (Anjab)',
            parent=manajemen_anjab_group,
            defaults={
                'permission_key': 'manajemen_analisis_jabatan.ma_an_satuan_kerja.view',
                'url_name': 'manajemen_analisis_jabatan:satuan_kerja_list',
                'icon': 'fas fa-list',
                'type': 'module',
                'order': 1,
                'category': 1,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Satuan Kerja (Anjab)')
        else:
            changed = False
            if ma_an_satuan_kerja.permission_key != 'manajemen_analisis_jabatan.ma_an_satuan_kerja.view':
                ma_an_satuan_kerja.permission_key = 'manajemen_analisis_jabatan.ma_an_satuan_kerja.view'; changed = True
            if ma_an_satuan_kerja.url_name != 'manajemen_analisis_jabatan:satuan_kerja_list':
                ma_an_satuan_kerja.url_name = 'manajemen_analisis_jabatan:satuan_kerja_list'; changed = True
            if ma_an_satuan_kerja.icon != 'fas fa-list':
                ma_an_satuan_kerja.icon = 'fas fa-list'; changed = True
            if ma_an_satuan_kerja.type != 'module':
                ma_an_satuan_kerja.type = 'module'; changed = True
            if (ma_an_satuan_kerja.order or 0) != 1:
                ma_an_satuan_kerja.order = 1; changed = True
            if (ma_an_satuan_kerja.category or 0) != 1:
                ma_an_satuan_kerja.category = 1; changed = True
            if ma_an_satuan_kerja.parent_id != manajemen_anjab_group.id:
                ma_an_satuan_kerja.parent = manajemen_anjab_group; changed = True
            if not ma_an_satuan_kerja.is_active:
                ma_an_satuan_kerja.is_active = True; changed = True
            if changed:
                ma_an_satuan_kerja.save()
                self.stdout.write('  ✓ Updated: Satuan Kerja (Anjab)')

        ma_an_sj_bakat, created = MenuItem.objects.get_or_create(
            name='Syarat Jabatan - Bakat',
            parent=manajemen_anjab_group,
            defaults={
                'permission_key': 'manajemen_analisis_jabatan.ma_an_sj_bakat.view',
                'url_name': 'manajemen_analisis_jabatan:sj_bakat_list',
                'icon': 'fas fa-brain',
                'type': 'module',
                'order': 2,
                'category': 1,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Syarat Jabatan - Bakat')
        else:
            changed = False
            if ma_an_sj_bakat.permission_key != 'manajemen_analisis_jabatan.ma_an_sj_bakat.view':
                ma_an_sj_bakat.permission_key = 'manajemen_analisis_jabatan.ma_an_sj_bakat.view'; changed = True
            if ma_an_sj_bakat.url_name != 'manajemen_analisis_jabatan:sj_bakat_list':
                ma_an_sj_bakat.url_name = 'manajemen_analisis_jabatan:sj_bakat_list'; changed = True
            if ma_an_sj_bakat.icon != 'fas fa-brain':
                ma_an_sj_bakat.icon = 'fas fa-brain'; changed = True
            if ma_an_sj_bakat.type != 'module':
                ma_an_sj_bakat.type = 'module'; changed = True
            if (ma_an_sj_bakat.order or 0) != 2:
                ma_an_sj_bakat.order = 2; changed = True
            if (ma_an_sj_bakat.category or 0) != 1:
                ma_an_sj_bakat.category = 1; changed = True
            if ma_an_sj_bakat.parent_id != manajemen_anjab_group.id:
                ma_an_sj_bakat.parent = manajemen_anjab_group; changed = True
            if not ma_an_sj_bakat.is_active:
                ma_an_sj_bakat.is_active = True; changed = True
            if changed:
                ma_an_sj_bakat.save()
                self.stdout.write('  ✓ Updated: Syarat Jabatan - Bakat')

        ma_an_sj_temperamen, created = MenuItem.objects.get_or_create(
            name='Syarat Jabatan - Temperamen Kerja',
            parent=manajemen_anjab_group,
            defaults={
                'permission_key': 'manajemen_analisis_jabatan.ma_an_sj_temperamen_kerja.view',
                'url_name': 'manajemen_analisis_jabatan:sj_temperamen_kerja_list',
                'icon': 'fas fa-user-cog',
                'type': 'module',
                'order': 3,
                'category': 1,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Syarat Jabatan - Temperamen Kerja')
        else:
            changed = False
            if ma_an_sj_temperamen.permission_key != 'manajemen_analisis_jabatan.ma_an_sj_temperamen_kerja.view':
                ma_an_sj_temperamen.permission_key = 'manajemen_analisis_jabatan.ma_an_sj_temperamen_kerja.view'; changed = True
            if ma_an_sj_temperamen.url_name != 'manajemen_analisis_jabatan:sj_temperamen_kerja_list':
                ma_an_sj_temperamen.url_name = 'manajemen_analisis_jabatan:sj_temperamen_kerja_list'; changed = True
            if ma_an_sj_temperamen.icon != 'fas fa-user-cog':
                ma_an_sj_temperamen.icon = 'fas fa-user-cog'; changed = True
            if ma_an_sj_temperamen.type != 'module':
                ma_an_sj_temperamen.type = 'module'; changed = True
            if (ma_an_sj_temperamen.order or 0) != 3:
                ma_an_sj_temperamen.order = 3; changed = True
            if (ma_an_sj_temperamen.category or 0) != 1:
                ma_an_sj_temperamen.category = 1; changed = True
            if ma_an_sj_temperamen.parent_id != manajemen_anjab_group.id:
                ma_an_sj_temperamen.parent = manajemen_anjab_group; changed = True
            if not ma_an_sj_temperamen.is_active:
                ma_an_sj_temperamen.is_active = True; changed = True
            if changed:
                ma_an_sj_temperamen.save()
                self.stdout.write('  ✓ Updated: Syarat Jabatan - Temperamen Kerja')

        ma_an_sj_minat, created = MenuItem.objects.get_or_create(
            name='Syarat Jabatan - Minat Kerja',
            parent=manajemen_anjab_group,
            defaults={
                'permission_key': 'manajemen_analisis_jabatan.ma_an_sj_minat_kerja.view',
                'url_name': 'manajemen_analisis_jabatan:sj_minat_kerja_list',
                'icon': 'fas fa-heart',
                'type': 'module',
                'order': 4,
                'category': 1,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Syarat Jabatan - Minat Kerja')
        else:
            changed = False
            if ma_an_sj_minat.permission_key != 'manajemen_analisis_jabatan.ma_an_sj_minat_kerja.view':
                ma_an_sj_minat.permission_key = 'manajemen_analisis_jabatan.ma_an_sj_minat_kerja.view'; changed = True
            if ma_an_sj_minat.url_name != 'manajemen_analisis_jabatan:sj_minat_kerja_list':
                ma_an_sj_minat.url_name = 'manajemen_analisis_jabatan:sj_minat_kerja_list'; changed = True
            if ma_an_sj_minat.icon != 'fas fa-heart':
                ma_an_sj_minat.icon = 'fas fa-heart'; changed = True
            if ma_an_sj_minat.type != 'module':
                ma_an_sj_minat.type = 'module'; changed = True
            if (ma_an_sj_minat.order or 0) != 4:
                ma_an_sj_minat.order = 4; changed = True
            if (ma_an_sj_minat.category or 0) != 1:
                ma_an_sj_minat.category = 1; changed = True
            if ma_an_sj_minat.parent_id != manajemen_anjab_group.id:
                ma_an_sj_minat.parent = manajemen_anjab_group; changed = True
            if not ma_an_sj_minat.is_active:
                ma_an_sj_minat.is_active = True; changed = True
            if changed:
                ma_an_sj_minat.save()
                self.stdout.write('  ✓ Updated: Syarat Jabatan - Minat Kerja')

        ma_an_sj_jabatan_data, created = MenuItem.objects.get_or_create(
            name='Syarat Jabatan - Jabatan Data',
            parent=manajemen_anjab_group,
            defaults={
                'permission_key': 'manajemen_analisis_jabatan.ma_an_sj_jabatan_data.view',
                'url_name': 'manajemen_analisis_jabatan:sj_jabatan_data_list',
                'icon': 'fas fa-database',
                'type': 'module',
                'order': 5,
                'category': 1,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Syarat Jabatan - Jabatan Data')
        else:
            changed = False
            if ma_an_sj_jabatan_data.permission_key != 'manajemen_analisis_jabatan.ma_an_sj_jabatan_data.view':
                ma_an_sj_jabatan_data.permission_key = 'manajemen_analisis_jabatan.ma_an_sj_jabatan_data.view'; changed = True
            if ma_an_sj_jabatan_data.url_name != 'manajemen_analisis_jabatan:sj_jabatan_data_list':
                ma_an_sj_jabatan_data.url_name = 'manajemen_analisis_jabatan:sj_jabatan_data_list'; changed = True
            if ma_an_sj_jabatan_data.icon != 'fas fa-database':
                ma_an_sj_jabatan_data.icon = 'fas fa-database'; changed = True
            if ma_an_sj_jabatan_data.type != 'module':
                ma_an_sj_jabatan_data.type = 'module'; changed = True
            if (ma_an_sj_jabatan_data.order or 0) != 5:
                ma_an_sj_jabatan_data.order = 5; changed = True
            if (ma_an_sj_jabatan_data.category or 0) != 1:
                ma_an_sj_jabatan_data.category = 1; changed = True
            if ma_an_sj_jabatan_data.parent_id != manajemen_anjab_group.id:
                ma_an_sj_jabatan_data.parent = manajemen_anjab_group; changed = True
            if not ma_an_sj_jabatan_data.is_active:
                ma_an_sj_jabatan_data.is_active = True; changed = True
            if changed:
                ma_an_sj_jabatan_data.save()
                self.stdout.write('  ✓ Updated: Syarat Jabatan - Jabatan Data')

        ma_an_sj_jabatan_orang, created = MenuItem.objects.get_or_create(
            name='Syarat Jabatan - Jabatan Orang',
            parent=manajemen_anjab_group,
            defaults={
                'permission_key': 'manajemen_analisis_jabatan.ma_an_sj_jabatan_orang.view',
                'url_name': 'manajemen_analisis_jabatan:sj_jabatan_orang_list',
                'icon': 'fas fa-users',
                'type': 'module',
                'order': 6,
                'category': 1,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Syarat Jabatan - Jabatan Orang')
        else:
            changed = False
            if ma_an_sj_jabatan_orang.permission_key != 'manajemen_analisis_jabatan.ma_an_sj_jabatan_orang.view':
                ma_an_sj_jabatan_orang.permission_key = 'manajemen_analisis_jabatan.ma_an_sj_jabatan_orang.view'; changed = True
            if ma_an_sj_jabatan_orang.url_name != 'manajemen_analisis_jabatan:sj_jabatan_orang_list':
                ma_an_sj_jabatan_orang.url_name = 'manajemen_analisis_jabatan:sj_jabatan_orang_list'; changed = True
            if ma_an_sj_jabatan_orang.icon != 'fas fa-users':
                ma_an_sj_jabatan_orang.icon = 'fas fa-users'; changed = True
            if ma_an_sj_jabatan_orang.type != 'module':
                ma_an_sj_jabatan_orang.type = 'module'; changed = True
            if (ma_an_sj_jabatan_orang.order or 0) != 6:
                ma_an_sj_jabatan_orang.order = 6; changed = True
            if (ma_an_sj_jabatan_orang.category or 0) != 1:
                ma_an_sj_jabatan_orang.category = 1; changed = True
            if ma_an_sj_jabatan_orang.parent_id != manajemen_anjab_group.id:
                ma_an_sj_jabatan_orang.parent = manajemen_anjab_group; changed = True
            if not ma_an_sj_jabatan_orang.is_active:
                ma_an_sj_jabatan_orang.is_active = True; changed = True
            if changed:
                ma_an_sj_jabatan_orang.save()
                self.stdout.write('  ✓ Updated: Syarat Jabatan - Jabatan Orang')

        ma_an_sj_jabatan_benda, created = MenuItem.objects.get_or_create(
            name='Syarat Jabatan - Jabatan Benda',
            parent=manajemen_anjab_group,
            defaults={
                'permission_key': 'manajemen_analisis_jabatan.ma_an_sj_jabatan_benda.view',
                'url_name': 'manajemen_analisis_jabatan:sj_jabatan_benda_list',
                'icon': 'fas fa-cogs',
                'type': 'module',
                'order': 7,
                'category': 1,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Syarat Jabatan - Jabatan Benda')
        else:
            changed = False
            if ma_an_sj_jabatan_benda.permission_key != 'manajemen_analisis_jabatan.ma_an_sj_jabatan_benda.view':
                ma_an_sj_jabatan_benda.permission_key = 'manajemen_analisis_jabatan.ma_an_sj_jabatan_benda.view'; changed = True
            if ma_an_sj_jabatan_benda.url_name != 'manajemen_analisis_jabatan:sj_jabatan_benda_list':
                ma_an_sj_jabatan_benda.url_name = 'manajemen_analisis_jabatan:sj_jabatan_benda_list'; changed = True
            if ma_an_sj_jabatan_benda.icon != 'fas fa-cogs':
                ma_an_sj_jabatan_benda.icon = 'fas fa-cogs'; changed = True
            if ma_an_sj_jabatan_benda.type != 'module':
                ma_an_sj_jabatan_benda.type = 'module'; changed = True
            if (ma_an_sj_jabatan_benda.order or 0) != 7:
                ma_an_sj_jabatan_benda.order = 7; changed = True
            if (ma_an_sj_jabatan_benda.category or 0) != 1:
                ma_an_sj_jabatan_benda.category = 1; changed = True
            if ma_an_sj_jabatan_benda.parent_id != manajemen_anjab_group.id:
                ma_an_sj_jabatan_benda.parent = manajemen_anjab_group; changed = True
            if not ma_an_sj_jabatan_benda.is_active:
                ma_an_sj_jabatan_benda.is_active = True; changed = True
            if changed:
                ma_an_sj_jabatan_benda.save()
                self.stdout.write('  ✓ Updated: Syarat Jabatan - Jabatan Benda')

        ma_an_sj_upaya_fisik, created = MenuItem.objects.get_or_create(
            name='Syarat Jabatan - Upaya Fisik',
            parent=manajemen_anjab_group,
            defaults={
                'permission_key': 'manajemen_analisis_jabatan.ma_an_sj_upaya_fisik.view',
                'url_name': 'manajemen_analisis_jabatan:sj_upaya_fisik_list',
                'icon': 'fas fa-running',
                'type': 'module',
                'order': 8,
                'category': 1,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Syarat Jabatan - Upaya Fisik')
        else:
            changed = False
            if ma_an_sj_upaya_fisik.permission_key != 'manajemen_analisis_jabatan.ma_an_sj_upaya_fisik.view':
                ma_an_sj_upaya_fisik.permission_key = 'manajemen_analisis_jabatan.ma_an_sj_upaya_fisik.view'; changed = True
            if ma_an_sj_upaya_fisik.url_name != 'manajemen_analisis_jabatan:sj_upaya_fisik_list':
                ma_an_sj_upaya_fisik.url_name = 'manajemen_analisis_jabatan:sj_upaya_fisik_list'; changed = True
            if ma_an_sj_upaya_fisik.icon != 'fas fa-running':
                ma_an_sj_upaya_fisik.icon = 'fas fa-running'; changed = True
            if ma_an_sj_upaya_fisik.type != 'module':
                ma_an_sj_upaya_fisik.type = 'module'; changed = True
            if (ma_an_sj_upaya_fisik.order or 0) != 8:
                ma_an_sj_upaya_fisik.order = 8; changed = True
            if (ma_an_sj_upaya_fisik.category or 0) != 1:
                ma_an_sj_upaya_fisik.category = 1; changed = True
            if ma_an_sj_upaya_fisik.parent_id != manajemen_anjab_group.id:
                ma_an_sj_upaya_fisik.parent = manajemen_anjab_group; changed = True
            if not ma_an_sj_upaya_fisik.is_active:
                ma_an_sj_upaya_fisik.is_active = True; changed = True
            if changed:
                ma_an_sj_upaya_fisik.save()
                self.stdout.write('  ✓ Updated: Syarat Jabatan - Upaya Fisik')

        ma_an_sj_pengetahuan_kerja, created = MenuItem.objects.get_or_create(
            name='Syarat Jabatan - Pengetahuan Kerja',
            parent=manajemen_anjab_group,
            defaults={
                'permission_key': 'manajemen_analisis_jabatan.ma_an_sj_pengetahuan_kerja.view',
                'url_name': 'manajemen_analisis_jabatan:sj_pengetahuan_kerja_list',
                'icon': 'fas fa-book',
                'type': 'module',
                'order': 9,
                'category': 1,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Syarat Jabatan - Pengetahuan Kerja')
        else:
            changed = False
            if ma_an_sj_pengetahuan_kerja.permission_key != 'manajemen_analisis_jabatan.ma_an_sj_pengetahuan_kerja.view':
                ma_an_sj_pengetahuan_kerja.permission_key = 'manajemen_analisis_jabatan.ma_an_sj_pengetahuan_kerja.view'; changed = True
            if ma_an_sj_pengetahuan_kerja.url_name != 'manajemen_analisis_jabatan:sj_pengetahuan_kerja_list':
                ma_an_sj_pengetahuan_kerja.url_name = 'manajemen_analisis_jabatan:sj_pengetahuan_kerja_list'; changed = True
            if ma_an_sj_pengetahuan_kerja.icon != 'fas fa-book':
                ma_an_sj_pengetahuan_kerja.icon = 'fas fa-book'; changed = True
            if ma_an_sj_pengetahuan_kerja.type != 'module':
                ma_an_sj_pengetahuan_kerja.type = 'module'; changed = True
            if (ma_an_sj_pengetahuan_kerja.order or 0) != 9:
                ma_an_sj_pengetahuan_kerja.order = 9; changed = True
            if (ma_an_sj_pengetahuan_kerja.category or 0) != 1:
                ma_an_sj_pengetahuan_kerja.category = 1; changed = True
            if ma_an_sj_pengetahuan_kerja.parent_id != manajemen_anjab_group.id:
                ma_an_sj_pengetahuan_kerja.parent = manajemen_anjab_group; changed = True
            if not ma_an_sj_pengetahuan_kerja.is_active:
                ma_an_sj_pengetahuan_kerja.is_active = True; changed = True
            if changed:
                ma_an_sj_pengetahuan_kerja.save()
                self.stdout.write('  ✓ Updated: Syarat Jabatan - Pengetahuan Kerja')

        ma_an_sj_keterampilan_kerja, created = MenuItem.objects.get_or_create(
            name='Syarat Jabatan - Keterampilan Kerja',
            parent=manajemen_anjab_group,
            defaults={
                'permission_key': 'manajemen_analisis_jabatan.ma_an_sj_keterampilan_kerja.view',
                'url_name': 'manajemen_analisis_jabatan:sj_keterampilan_kerja_list',
                'icon': 'fas fa-tools',
                'type': 'module',
                'order': 10,
                'category': 1,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Syarat Jabatan - Keterampilan Kerja')
        else:
            changed = False
            if ma_an_sj_keterampilan_kerja.permission_key != 'manajemen_analisis_jabatan.ma_an_sj_keterampilan_kerja.view':
                ma_an_sj_keterampilan_kerja.permission_key = 'manajemen_analisis_jabatan.ma_an_sj_keterampilan_kerja.view'; changed = True
            if ma_an_sj_keterampilan_kerja.url_name != 'manajemen_analisis_jabatan:sj_keterampilan_kerja_list':
                ma_an_sj_keterampilan_kerja.url_name = 'manajemen_analisis_jabatan:sj_keterampilan_kerja_list'; changed = True
            if ma_an_sj_keterampilan_kerja.icon != 'fas fa-tools':
                ma_an_sj_keterampilan_kerja.icon = 'fas fa-tools'; changed = True
            if ma_an_sj_keterampilan_kerja.type != 'module':
                ma_an_sj_keterampilan_kerja.type = 'module'; changed = True
            if (ma_an_sj_keterampilan_kerja.order or 0) != 10:
                ma_an_sj_keterampilan_kerja.order = 10; changed = True
            if (ma_an_sj_keterampilan_kerja.category or 0) != 1:
                ma_an_sj_keterampilan_kerja.category = 1; changed = True
            if ma_an_sj_keterampilan_kerja.parent_id != manajemen_anjab_group.id:
                ma_an_sj_keterampilan_kerja.parent = manajemen_anjab_group; changed = True
            if not ma_an_sj_keterampilan_kerja.is_active:
                ma_an_sj_keterampilan_kerja.is_active = True; changed = True
            if changed:
                ma_an_sj_keterampilan_kerja.save()
                self.stdout.write('  ✓ Updated: Syarat Jabatan - Keterampilan Kerja')

        ma_an_sj_pelatihan_fungsional, created = MenuItem.objects.get_or_create(
            name='Syarat Jabatan - Pelatihan Fungsional',
            parent=manajemen_anjab_group,
            defaults={
                'permission_key': 'manajemen_analisis_jabatan.ma_an_sj_pelatihan_fungsional.view',
                'url_name': 'manajemen_analisis_jabatan:sj_pelatihan_fungsional_list',
                'icon': 'fas fa-chalkboard-teacher',
                'type': 'module',
                'order': 11,
                'category': 1,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Syarat Jabatan - Pelatihan Fungsional')
        else:
            changed = False
            if ma_an_sj_pelatihan_fungsional.permission_key != 'manajemen_analisis_jabatan.ma_an_sj_pelatihan_fungsional.view':
                ma_an_sj_pelatihan_fungsional.permission_key = 'manajemen_analisis_jabatan.ma_an_sj_pelatihan_fungsional.view'; changed = True
            if ma_an_sj_pelatihan_fungsional.url_name != 'manajemen_analisis_jabatan:sj_pelatihan_fungsional_list':
                ma_an_sj_pelatihan_fungsional.url_name = 'manajemen_analisis_jabatan:sj_pelatihan_fungsional_list'; changed = True
            if ma_an_sj_pelatihan_fungsional.icon != 'fas fa-chalkboard-teacher':
                ma_an_sj_pelatihan_fungsional.icon = 'fas fa-chalkboard-teacher'; changed = True
            if ma_an_sj_pelatihan_fungsional.type != 'module':
                ma_an_sj_pelatihan_fungsional.type = 'module'; changed = True
            if (ma_an_sj_pelatihan_fungsional.order or 0) != 11:
                ma_an_sj_pelatihan_fungsional.order = 11; changed = True
            if (ma_an_sj_pelatihan_fungsional.category or 0) != 1:
                ma_an_sj_pelatihan_fungsional.category = 1; changed = True
            if ma_an_sj_pelatihan_fungsional.parent_id != manajemen_anjab_group.id:
                ma_an_sj_pelatihan_fungsional.parent = manajemen_anjab_group; changed = True
            if not ma_an_sj_pelatihan_fungsional.is_active:
                ma_an_sj_pelatihan_fungsional.is_active = True; changed = True
            if changed:
                ma_an_sj_pelatihan_fungsional.save()
                self.stdout.write('  ✓ Updated: Syarat Jabatan - Pelatihan Fungsional')

        ma_an_sj_jenis_kelamin, created = MenuItem.objects.get_or_create(
            name='Syarat Jabatan - Jenis Kelamin',
            parent=manajemen_anjab_group,
            defaults={
                'permission_key': 'manajemen_analisis_jabatan.ma_an_sj_jenis_kelamin.view',
                'url_name': 'manajemen_analisis_jabatan:sj_jenis_kelamin_list',
                'icon': 'fas fa-venus-mars',
                'type': 'module',
                'order': 12,
                'category': 1,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Syarat Jabatan - Jenis Kelamin')
        else:
            changed = False
            if ma_an_sj_jenis_kelamin.permission_key != 'manajemen_analisis_jabatan.ma_an_sj_jenis_kelamin.view':
                ma_an_sj_jenis_kelamin.permission_key = 'manajemen_analisis_jabatan.ma_an_sj_jenis_kelamin.view'; changed = True
            if ma_an_sj_jenis_kelamin.url_name != 'manajemen_analisis_jabatan:sj_jenis_kelamin_list':
                ma_an_sj_jenis_kelamin.url_name = 'manajemen_analisis_jabatan:sj_jenis_kelamin_list'; changed = True
            if ma_an_sj_jenis_kelamin.icon != 'fas fa-venus-mars':
                ma_an_sj_jenis_kelamin.icon = 'fas fa-venus-mars'; changed = True
            if ma_an_sj_jenis_kelamin.type != 'module':
                ma_an_sj_jenis_kelamin.type = 'module'; changed = True
            if (ma_an_sj_jenis_kelamin.order or 0) != 12:
                ma_an_sj_jenis_kelamin.order = 12; changed = True
            if (ma_an_sj_jenis_kelamin.category or 0) != 1:
                ma_an_sj_jenis_kelamin.category = 1; changed = True
            if ma_an_sj_jenis_kelamin.parent_id != manajemen_anjab_group.id:
                ma_an_sj_jenis_kelamin.parent = manajemen_anjab_group; changed = True
            if not ma_an_sj_jenis_kelamin.is_active:
                ma_an_sj_jenis_kelamin.is_active = True; changed = True
            if changed:
                ma_an_sj_jenis_kelamin.save()
                self.stdout.write('  ✓ Updated: Syarat Jabatan - Jenis Kelamin')

        ma_an_sj_pelatihan_teknis, created = MenuItem.objects.get_or_create(
            name='Syarat Jabatan - Pelatihan Teknis',
            parent=manajemen_anjab_group,
            defaults={
                'permission_key': 'manajemen_analisis_jabatan.ma_an_sj_pelatihan_teknis.view',
                'url_name': 'manajemen_analisis_jabatan:sj_pelatihan_teknis_list',
                'icon': 'fas fa-graduation-cap',
                'type': 'module',
                'order': 13,
                'category': 1,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Syarat Jabatan - Pelatihan Teknis')
        else:
            changed = False
            if ma_an_sj_pelatihan_teknis.permission_key != 'manajemen_analisis_jabatan.ma_an_sj_pelatihan_teknis.view':
                ma_an_sj_pelatihan_teknis.permission_key = 'manajemen_analisis_jabatan.ma_an_sj_pelatihan_teknis.view'; changed = True
            if ma_an_sj_pelatihan_teknis.url_name != 'manajemen_analisis_jabatan:sj_pelatihan_teknis_list':
                ma_an_sj_pelatihan_teknis.url_name = 'manajemen_analisis_jabatan:sj_pelatihan_teknis_list'; changed = True
            if ma_an_sj_pelatihan_teknis.icon != 'fas fa-graduation-cap':
                ma_an_sj_pelatihan_teknis.icon = 'fas fa-graduation-cap'; changed = True
            if ma_an_sj_pelatihan_teknis.type != 'module':
                ma_an_sj_pelatihan_teknis.type = 'module'; changed = True
            if (ma_an_sj_pelatihan_teknis.order or 0) != 13:
                ma_an_sj_pelatihan_teknis.order = 13; changed = True
            if (ma_an_sj_pelatihan_teknis.category or 0) != 1:
                ma_an_sj_pelatihan_teknis.category = 1; changed = True
            if ma_an_sj_pelatihan_teknis.parent_id != manajemen_anjab_group.id:
                ma_an_sj_pelatihan_teknis.parent = manajemen_anjab_group; changed = True
            if not ma_an_sj_pelatihan_teknis.is_active:
                ma_an_sj_pelatihan_teknis.is_active = True; changed = True
            if changed:
                ma_an_sj_pelatihan_teknis.save()
                self.stdout.write('  ✓ Updated: Syarat Jabatan - Pelatihan Teknis')

        kategori_pegawai, created = MenuItem.objects.get_or_create(
            name='Kategori Pegawai',
            parent=manajemen_data_group,
            defaults={
                'permission_key': 'manajemen_data.md_kategori_pegawai.view',
                'url_name': 'manajemen_data:kategori_pegawai_list',
                'icon': 'fas fa-tags',
                'type': 'module',
                'order': 1,
                'category': 1,
                'is_active': True,
            }
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Kategori Pegawai')
        else:
            changed = False
            if kategori_pegawai.permission_key != 'manajemen_data.md_kategori_pegawai.view':
                kategori_pegawai.permission_key = 'manajemen_data.md_kategori_pegawai.view'; changed = True
            if kategori_pegawai.url_name != 'manajemen_data:kategori_pegawai_list':
                kategori_pegawai.url_name = 'manajemen_data:kategori_pegawai_list'; changed = True
            if kategori_pegawai.icon != 'fas fa-tags':
                kategori_pegawai.icon = 'fas fa-tags'; changed = True
            if kategori_pegawai.type != 'module':
                kategori_pegawai.type = 'module'; changed = True
            if (kategori_pegawai.order or 0) != 1:
                kategori_pegawai.order = 1; changed = True
            if (kategori_pegawai.category or 0) != 1:
                kategori_pegawai.category = 1; changed = True
            if kategori_pegawai.parent_id != manajemen_data_group.id:
                kategori_pegawai.parent = manajemen_data_group; changed = True
            if not kategori_pegawai.is_active:
                kategori_pegawai.is_active = True; changed = True
            if changed:
                kategori_pegawai.save()
                self.stdout.write('  ✓ Updated: Kategori Pegawai')

        agama, created = MenuItem.objects.get_or_create(
            name='Agama',
            parent=manajemen_data_group,
            defaults={
                'permission_key': 'manajemen_data.md_agama.view',
                'url_name': 'manajemen_data:agama_list',
                'icon': 'fas fa-praying-hands',
                'type': 'module',
                'order': 2,
                'category': 1,
                'is_active': True,
            }
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Agama')
        else:
            changed = False
            if agama.permission_key != 'manajemen_data.md_agama.view':
                agama.permission_key = 'manajemen_data.md_agama.view'; changed = True
            if agama.url_name != 'manajemen_data:agama_list':
                agama.url_name = 'manajemen_data:agama_list'; changed = True
            if agama.icon != 'fas fa-praying-hands':
                agama.icon = 'fas fa-praying-hands'; changed = True
            if agama.type != 'module':
                agama.type = 'module'; changed = True
            if (agama.order or 0) != 2:
                agama.order = 2; changed = True
            if (agama.category or 0) != 1:
                agama.category = 1; changed = True
            if agama.parent_id != manajemen_data_group.id:
                agama.parent = manajemen_data_group; changed = True
            if not agama.is_active:
                agama.is_active = True; changed = True
            if changed:
                agama.save()
                self.stdout.write('  ✓ Updated: Agama')

        status_perkawinan, created = MenuItem.objects.get_or_create(
            name='Status Perkawinan',
            parent=manajemen_data_group,
            defaults={
                'permission_key': 'manajemen_data.md_status_perkawinan.view',
                'url_name': 'manajemen_data:status_perkawinan_list',
                'icon': 'fas fa-ring',
                'type': 'module',
                'order': 3,
                'category': 1,
                'is_active': True,
            }
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Status Perkawinan')
        else:
            changed = False
            if status_perkawinan.permission_key != 'manajemen_data.md_status_perkawinan.view':
                status_perkawinan.permission_key = 'manajemen_data.md_status_perkawinan.view'; changed = True
            if status_perkawinan.url_name != 'manajemen_data:status_perkawinan_list':
                status_perkawinan.url_name = 'manajemen_data:status_perkawinan_list'; changed = True
            if status_perkawinan.icon != 'fas fa-ring':
                status_perkawinan.icon = 'fas fa-ring'; changed = True
            if status_perkawinan.type != 'module':
                status_perkawinan.type = 'module'; changed = True
            if (status_perkawinan.order or 0) != 3:
                status_perkawinan.order = 3; changed = True
            if (status_perkawinan.category or 0) != 1:
                status_perkawinan.category = 1; changed = True
            if status_perkawinan.parent_id != manajemen_data_group.id:
                status_perkawinan.parent = manajemen_data_group; changed = True
            if not status_perkawinan.is_active:
                status_perkawinan.is_active = True; changed = True
            if changed:
                status_perkawinan.save()
                self.stdout.write('  ✓ Updated: Status Perkawinan')

        jenjang_pendidikan, created = MenuItem.objects.get_or_create(
            name='Jenjang Pendidikan',
            parent=manajemen_data_group,
            defaults={
                'permission_key': 'manajemen_data.md_jenjang_pendidikan.view',
                'url_name': 'manajemen_data:jenjang_pendidikan_list',
                'icon': 'fas fa-graduation-cap',
                'type': 'module',
                'order': 4,
                'category': 5,
                'is_active': True,
            }
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Jenjang Pendidikan')
        else:
            changed = False
            if jenjang_pendidikan.permission_key != 'manajemen_data.md_jenjang_pendidikan.view':
                jenjang_pendidikan.permission_key = 'manajemen_data.md_jenjang_pendidikan.view'; changed = True
            if jenjang_pendidikan.url_name != 'manajemen_data:jenjang_pendidikan_list':
                jenjang_pendidikan.url_name = 'manajemen_data:jenjang_pendidikan_list'; changed = True
            if jenjang_pendidikan.icon != 'fas fa-graduation-cap':
                jenjang_pendidikan.icon = 'fas fa-graduation-cap'; changed = True
            if jenjang_pendidikan.type != 'module':
                jenjang_pendidikan.type = 'module'; changed = True
            if (jenjang_pendidikan.order or 0) != 4:
                jenjang_pendidikan.order = 4; changed = True
            if (jenjang_pendidikan.category or 0) != 5:
                jenjang_pendidikan.category = 5; changed = True
            if jenjang_pendidikan.parent_id != manajemen_data_group.id:
                jenjang_pendidikan.parent = manajemen_data_group; changed = True
            if not jenjang_pendidikan.is_active:
                jenjang_pendidikan.is_active = True; changed = True
            if changed:
                jenjang_pendidikan.save()
                self.stdout.write('  ✓ Updated: Jenjang Pendidikan')

        daftar_pendidikan, created = MenuItem.objects.get_or_create(
            name='Daftar Pendidikan',
            parent=manajemen_data_group,
            defaults={
                'permission_key': 'manajemen_data.ms_daftar_pendidikan.view',
                'url_name': 'manajemen_data:daftar_pendidikan_list',
                'icon': 'fas fa-user-graduate',
                'type': 'module',
                'order': 5,
                'category': 5,
                'is_active': True,
            }
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Daftar Pendidikan')
        else:
            changed = False
            if daftar_pendidikan.permission_key != 'manajemen_data.ms_daftar_pendidikan.view':
                daftar_pendidikan.permission_key = 'manajemen_data.ms_daftar_pendidikan.view'; changed = True
            if daftar_pendidikan.url_name != 'manajemen_data:daftar_pendidikan_list':
                daftar_pendidikan.url_name = 'manajemen_data:daftar_pendidikan_list'; changed = True
            if daftar_pendidikan.icon != 'fas fa-user-graduate':
                daftar_pendidikan.icon = 'fas fa-user-graduate'; changed = True
            if daftar_pendidikan.type != 'module':
                daftar_pendidikan.type = 'module'; changed = True
            if (daftar_pendidikan.order or 0) != 5:
                daftar_pendidikan.order = 5; changed = True
            if (daftar_pendidikan.category or 0) != 5:
                daftar_pendidikan.category = 5; changed = True
            if daftar_pendidikan.parent_id != manajemen_data_group.id:
                daftar_pendidikan.parent = manajemen_data_group; changed = True
            if not daftar_pendidikan.is_active:
                daftar_pendidikan.is_active = True; changed = True
            if changed:
                daftar_pendidikan.save()
                self.stdout.write('  ✓ Updated: Daftar Pendidikan')

        kedudukan_pegawai, created = MenuItem.objects.get_or_create(
            name='Kedudukan Pegawai',
            parent=manajemen_data_group,
            defaults={
                'permission_key': 'manajemen_data.md_kedudukan_pegawai.view',
                'url_name': 'manajemen_data:kedudukan_pegawai_list',
                'icon': 'fas fa-user-tag',
                'type': 'module',
                'order': 5,
                'category': 1,
                'is_active': True,
            }
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Kedudukan Pegawai')
        else:
            changed = False
            if kedudukan_pegawai.permission_key != 'manajemen_data.md_kedudukan_pegawai.view':
                kedudukan_pegawai.permission_key = 'manajemen_data.md_kedudukan_pegawai.view'; changed = True
            if kedudukan_pegawai.url_name != 'manajemen_data:kedudukan_pegawai_list':
                kedudukan_pegawai.url_name = 'manajemen_data:kedudukan_pegawai_list'; changed = True
            if kedudukan_pegawai.icon != 'fas fa-user-tag':
                kedudukan_pegawai.icon = 'fas fa-user-tag'; changed = True
            if kedudukan_pegawai.type != 'module':
                kedudukan_pegawai.type = 'module'; changed = True
            if (kedudukan_pegawai.order or 0) != 5:
                kedudukan_pegawai.order = 5; changed = True
            if (kedudukan_pegawai.category or 0) != 1:
                kedudukan_pegawai.category = 1; changed = True
            if kedudukan_pegawai.parent_id != manajemen_data_group.id:
                kedudukan_pegawai.parent = manajemen_data_group; changed = True
            if not kedudukan_pegawai.is_active:
                kedudukan_pegawai.is_active = True; changed = True
            if changed:
                kedudukan_pegawai.save()
                self.stdout.write('  ✓ Updated: Kedudukan Pegawai')

        jenis_jabatan, created = MenuItem.objects.get_or_create(
            name='Jenis Jabatan',
            parent=manajemen_data_group,
            defaults={
                'permission_key': 'manajemen_data.md_jenis_jabatan.view',
                'url_name': 'manajemen_data:jenis_jabatan_list',
                'icon': 'fas fa-briefcase',
                'type': 'module',
                'order': 6,
                'category': 5,
                'is_active': True,
            }
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Jenis Jabatan')
        else:
            changed = False
            if jenis_jabatan.permission_key != 'manajemen_data.md_jenis_jabatan.view':
                jenis_jabatan.permission_key = 'manajemen_data.md_jenis_jabatan.view'; changed = True
            if jenis_jabatan.url_name != 'manajemen_data:jenis_jabatan_list':
                jenis_jabatan.url_name = 'manajemen_data:jenis_jabatan_list'; changed = True
            if jenis_jabatan.icon != 'fas fa-briefcase':
                jenis_jabatan.icon = 'fas fa-briefcase'; changed = True
            if jenis_jabatan.type != 'module':
                jenis_jabatan.type = 'module'; changed = True
            if (jenis_jabatan.order or 0) != 6:
                jenis_jabatan.order = 6; changed = True
            if (jenis_jabatan.category or 0) != 5:
                jenis_jabatan.category = 5; changed = True
            if jenis_jabatan.parent_id != manajemen_data_group.id:
                jenis_jabatan.parent = manajemen_data_group; changed = True
            if not jenis_jabatan.is_active:
                jenis_jabatan.is_active = True; changed = True
            if changed:
                jenis_jabatan.save()
                self.stdout.write('  ✓ Updated: Jenis Jabatan')

        kategori_jabatan, created = MenuItem.objects.get_or_create(
            name='Kategori Jabatan',
            parent=manajemen_data_group,
            defaults={
                'permission_key': 'manajemen_data.md_kategori_jabatan.view',
                'url_name': 'manajemen_data:kategori_jabatan_list',
                'icon': 'fas fa-tags',
                'type': 'module',
                'order': 7,
                'category': 5,
                'is_active': True,
            }
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Kategori Jabatan')
        else:
            changed = False
            if kategori_jabatan.permission_key != 'manajemen_data.md_kategori_jabatan.view':
                kategori_jabatan.permission_key = 'manajemen_data.md_kategori_jabatan.view'; changed = True
            if kategori_jabatan.url_name != 'manajemen_data:kategori_jabatan_list':
                kategori_jabatan.url_name = 'manajemen_data:kategori_jabatan_list'; changed = True
            if kategori_jabatan.icon != 'fas fa-tags':
                kategori_jabatan.icon = 'fas fa-tags'; changed = True
            if kategori_jabatan.type != 'module':
                kategori_jabatan.type = 'module'; changed = True
            if (kategori_jabatan.order or 0) != 7:
                kategori_jabatan.order = 7; changed = True
            if (kategori_jabatan.category or 0) != 5:
                kategori_jabatan.category = 5; changed = True
            if kategori_jabatan.parent_id != manajemen_data_group.id:
                kategori_jabatan.parent = manajemen_data_group; changed = True
            if not kategori_jabatan.is_active:
                kategori_jabatan.is_active = True; changed = True
            if changed:
                kategori_jabatan.save()
                self.stdout.write('  ✓ Updated: Kategori Jabatan')

        pangkat, created = MenuItem.objects.get_or_create(
            name='Pangkat',
            parent=manajemen_data_group,
            defaults={
                'permission_key': 'manajemen_data.md_pangkat.view',
                'url_name': 'manajemen_data:pangkat_list',
                'icon': 'fas fa-layer-group',
                'type': 'module',
                'order': 180,
                'category': 5,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Pangkat')
        else:
            changed = False
            if pangkat.permission_key != 'manajemen_data.md_pangkat.view':
                pangkat.permission_key = 'manajemen_data.md_pangkat.view'; changed = True
            if pangkat.url_name != 'manajemen_data:pangkat_list':
                pangkat.url_name = 'manajemen_data:pangkat_list'; changed = True
            if pangkat.icon != 'fas fa-layer-group':
                pangkat.icon = 'fas fa-layer-group'; changed = True
            if pangkat.type != 'module':
                pangkat.type = 'module'; changed = True
            if pangkat.order != 180:
                pangkat.order = 180; changed = True
            if (pangkat.category or 0) != 5:
                pangkat.category = 5; changed = True
            if pangkat.parent_id != manajemen_data_group.id:
                pangkat.parent = manajemen_data_group; changed = True
            if not pangkat.is_active:
                pangkat.is_active = True; changed = True
            if changed:
                pangkat.save()
                self.stdout.write('  ✓ Updated: Pangkat')

        jenjang_jabatan, created = MenuItem.objects.get_or_create(
            name='Jenjang Jabatan',
            parent=manajemen_data_group,
            defaults={
                'permission_key': 'manajemen_data.md_jenjang_jabatan.view',
                'url_name': 'manajemen_data:jenjang_jabatan_list',
                'icon': 'fas fa-sitemap',
                'type': 'module',
                'order': 190,
                'category': 5,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Jenjang Jabatan')
        else:
            changed = False
            if jenjang_jabatan.permission_key != 'manajemen_data.md_jenjang_jabatan.view':
                jenjang_jabatan.permission_key = 'manajemen_data.md_jenjang_jabatan.view'; changed = True
            if jenjang_jabatan.url_name != 'manajemen_data:jenjang_jabatan_list':
                jenjang_jabatan.url_name = 'manajemen_data:jenjang_jabatan_list'; changed = True
            if jenjang_jabatan.icon != 'fas fa-sitemap':
                jenjang_jabatan.icon = 'fas fa-sitemap'; changed = True
            if jenjang_jabatan.type != 'module':
                jenjang_jabatan.type = 'module'; changed = True
            if jenjang_jabatan.order != 190:
                jenjang_jabatan.order = 190; changed = True
            if (jenjang_jabatan.category or 0) != 5:
                jenjang_jabatan.category = 5; changed = True
            if jenjang_jabatan.parent_id != manajemen_data_group.id:
                jenjang_jabatan.parent = manajemen_data_group; changed = True
            if not jenjang_jabatan.is_active:
                jenjang_jabatan.is_active = True; changed = True
            if changed:
                jenjang_jabatan.save()
                self.stdout.write('  ✓ Updated: Jenjang Jabatan')

        eselon, created = MenuItem.objects.get_or_create(
            name='Eselon',
            parent=manajemen_data_group,
            defaults={
                'permission_key': 'manajemen_data.md_eselon.view',
                'url_name': 'manajemen_data:eselon_list',
                'icon': 'fas fa-list-ol',
                'type': 'module',
                'order': 200,
                'category': 5,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Eselon')
        else:
            changed = False
            if eselon.permission_key != 'manajemen_data.md_eselon.view':
                eselon.permission_key = 'manajemen_data.md_eselon.view'; changed = True
            if eselon.url_name != 'manajemen_data:eselon_list':
                eselon.url_name = 'manajemen_data:eselon_list'; changed = True
            if eselon.icon != 'fas fa-list-ol':
                eselon.icon = 'fas fa-list-ol'; changed = True
            if eselon.type != 'module':
                eselon.type = 'module'; changed = True
            if eselon.order != 200:
                eselon.order = 200; changed = True
            if (eselon.category or 0) != 5:
                eselon.category = 5; changed = True
            if eselon.parent_id != manajemen_data_group.id:
                eselon.parent = manajemen_data_group; changed = True
            if not eselon.is_active:
                eselon.is_active = True; changed = True
            if changed:
                eselon.save()
                self.stdout.write('  ✓ Updated: Eselon')

        diklat_struktural, created = MenuItem.objects.get_or_create(
            name='Diklat Struktural',
            parent=manajemen_data_group,
            defaults={
                'permission_key': 'manajemen_data.md_diklat_struktural.view',
                'url_name': 'manajemen_data:diklat_struktural_list',
                'icon': 'fas fa-chalkboard-teacher',
                'type': 'module',
                'order': 210,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Diklat Struktural')
        else:
            changed = False
            if diklat_struktural.permission_key != 'manajemen_data.md_diklat_struktural.view':
                diklat_struktural.permission_key = 'manajemen_data.md_diklat_struktural.view'; changed = True
            if diklat_struktural.url_name != 'manajemen_data:diklat_struktural_list':
                diklat_struktural.url_name = 'manajemen_data:diklat_struktural_list'; changed = True
            if diklat_struktural.icon != 'fas fa-chalkboard-teacher':
                diklat_struktural.icon = 'fas fa-chalkboard-teacher'; changed = True
            if diklat_struktural.type != 'module':
                diklat_struktural.type = 'module'; changed = True
            if diklat_struktural.order != 210:
                diklat_struktural.order = 210; changed = True
            if not diklat_struktural.is_active:
                diklat_struktural.is_active = True; changed = True
            if changed:
                diklat_struktural.save()
                self.stdout.write('  ✓ Updated: Diklat Struktural')

        jenis_surat, created = MenuItem.objects.get_or_create(
            name='Jenis Surat',
            parent=manajemen_data_group,
            defaults={
                'permission_key': 'manajemen_data.md_jenis_surat.view',
                'url_name': 'manajemen_data:jenis_surat_list',
                'icon': 'fas fa-envelope-open-text',
                'type': 'module',
                'order': 220,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Jenis Surat')
        else:
            changed = False
            if jenis_surat.permission_key != 'manajemen_data.md_jenis_surat.view':
                jenis_surat.permission_key = 'manajemen_data.md_jenis_surat.view'; changed = True
            if jenis_surat.url_name != 'manajemen_data:jenis_surat_list':
                jenis_surat.url_name = 'manajemen_data:jenis_surat_list'; changed = True
            if jenis_surat.icon != 'fas fa-envelope-open-text':
                jenis_surat.icon = 'fas fa-envelope-open-text'; changed = True
            if jenis_surat.type != 'module':
                jenis_surat.type = 'module'; changed = True
            if jenis_surat.order != 220:
                jenis_surat.order = 220; changed = True
            if not jenis_surat.is_active:
                jenis_surat.is_active = True; changed = True
            if changed:
                jenis_surat.save()
                self.stdout.write('  ✓ Updated: Jenis Surat')

        pejabat_menetapkan, created = MenuItem.objects.get_or_create(
            name='Pejabat Menetapkan',
            parent=manajemen_data_group,
            defaults={
                'permission_key': 'manajemen_data.md_pejabat_menetapkan.view',
                'url_name': 'manajemen_data:pejabat_menetapkan_list',
                'icon': 'fas fa-gavel',
                'type': 'module',
                'order': 230,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Pejabat Menetapkan')
        else:
            changed = False
            if pejabat_menetapkan.permission_key != 'manajemen_data.md_pejabat_menetapkan.view':
                pejabat_menetapkan.permission_key = 'manajemen_data.md_pejabat_menetapkan.view'; changed = True
            if pejabat_menetapkan.url_name != 'manajemen_data:pejabat_menetapkan_list':
                pejabat_menetapkan.url_name = 'manajemen_data:pejabat_menetapkan_list'; changed = True
            if pejabat_menetapkan.icon != 'fas fa-gavel':
                pejabat_menetapkan.icon = 'fas fa-gavel'; changed = True
            if pejabat_menetapkan.type != 'module':
                pejabat_menetapkan.type = 'module'; changed = True
            if (pejabat_menetapkan.category or 0) != 1:
                pejabat_menetapkan.category = 1; changed = True
            if pejabat_menetapkan.parent_id != manajemen_data_group.id:
                pejabat_menetapkan.parent = manajemen_data_group; changed = True
            if pejabat_menetapkan.order != 230:
                pejabat_menetapkan.order = 230; changed = True
            if not pejabat_menetapkan.is_active:
                pejabat_menetapkan.is_active = True; changed = True
            if changed:
                pejabat_menetapkan.save()
                self.stdout.write('  ✓ Updated: Pejabat Menetapkan')

        jenis_organisasi, created = MenuItem.objects.get_or_create(
            name='Jenis Organisasi',
            parent=manajemen_data_group,
            defaults={
                'permission_key': 'manajemen_data.md_jenis_organisasi.view',
                'url_name': 'manajemen_data:jenis_organisasi_list',
                'icon': 'fas fa-building',
                'type': 'module',
                'order': 240,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Jenis Organisasi')
        else:
            changed = False
            if jenis_organisasi.permission_key != 'manajemen_data.md_jenis_organisasi.view':
                jenis_organisasi.permission_key = 'manajemen_data.md_jenis_organisasi.view'; changed = True
            if jenis_organisasi.url_name != 'manajemen_data:jenis_organisasi_list':
                jenis_organisasi.url_name = 'manajemen_data:jenis_organisasi_list'; changed = True
            if jenis_organisasi.icon != 'fas fa-building':
                jenis_organisasi.icon = 'fas fa-building'; changed = True
            if jenis_organisasi.type != 'module':
                jenis_organisasi.type = 'module'; changed = True
            if (jenis_organisasi.category or 0) != 1:
                jenis_organisasi.category = 1; changed = True
            if jenis_organisasi.parent_id != manajemen_data_group.id:
                jenis_organisasi.parent = manajemen_data_group; changed = True
            if jenis_organisasi.order != 240:
                jenis_organisasi.order = 240; changed = True
            if not jenis_organisasi.is_active:
                jenis_organisasi.is_active = True; changed = True
            if changed:
                jenis_organisasi.save()
                self.stdout.write('  ✓ Updated: Jenis Organisasi')

        kategori_pemberitahuan, created = MenuItem.objects.get_or_create(
            name='Kategori Pemberitahuan',
            parent=manajemen_data_group,
            defaults={
                'permission_key': 'manajemen_data.md_kategori_pemberitahuan.view',
                'url_name': 'manajemen_data:kategori_pemberitahuan_list',
                'icon': 'fas fa-bell',
                'type': 'module',
                'order': 250,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Kategori Pemberitahuan')
        else:
            changed = False
            if kategori_pemberitahuan.permission_key != 'manajemen_data.md_kategori_pemberitahuan.view':
                kategori_pemberitahuan.permission_key = 'manajemen_data.md_kategori_pemberitahuan.view'; changed = True
            if kategori_pemberitahuan.url_name != 'manajemen_data:kategori_pemberitahuan_list':
                kategori_pemberitahuan.url_name = 'manajemen_data:kategori_pemberitahuan_list'; changed = True
            if kategori_pemberitahuan.icon != 'fas fa-bell':
                kategori_pemberitahuan.icon = 'fas fa-bell'; changed = True
            if kategori_pemberitahuan.type != 'module':
                kategori_pemberitahuan.type = 'module'; changed = True
            if (kategori_pemberitahuan.category or 0) != 1:
                kategori_pemberitahuan.category = 1; changed = True
            if kategori_pemberitahuan.parent_id != manajemen_data_group.id:
                kategori_pemberitahuan.parent = manajemen_data_group; changed = True
            if kategori_pemberitahuan.order != 250:
                kategori_pemberitahuan.order = 250; changed = True
            if not kategori_pemberitahuan.is_active:
                kategori_pemberitahuan.is_active = True; changed = True
            if changed:
                kategori_pemberitahuan.save()
                self.stdout.write('  ✓ Updated: Kategori Pemberitahuan')

        kategori_peraturan, created = MenuItem.objects.get_or_create(
            name='Kategori Peraturan',
            parent=manajemen_data_group,
            defaults={
                'permission_key': 'manajemen_data.md_kategori_peraturan.view',
                'url_name': 'manajemen_data:kategori_peraturan_list',
                'icon': 'fas fa-balance-scale',
                'type': 'module',
                'order': 260,
                'category': 5,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Kategori Peraturan')
        else:
            changed = False
            if kategori_peraturan.permission_key != 'manajemen_data.md_kategori_peraturan.view':
                kategori_peraturan.permission_key = 'manajemen_data.md_kategori_peraturan.view'; changed = True
            if kategori_peraturan.url_name != 'manajemen_data:kategori_peraturan_list':
                kategori_peraturan.url_name = 'manajemen_data:kategori_peraturan_list'; changed = True
            if kategori_peraturan.icon != 'fas fa-balance-scale':
                kategori_peraturan.icon = 'fas fa-balance-scale'; changed = True
            if kategori_peraturan.type != 'module':
                kategori_peraturan.type = 'module'; changed = True
            if (kategori_peraturan.category or 0) != 5:
                kategori_peraturan.category = 5; changed = True
            if kategori_peraturan.parent_id != manajemen_data_group.id:
                kategori_peraturan.parent = manajemen_data_group; changed = True
            if kategori_peraturan.order != 260:
                kategori_peraturan.order = 260; changed = True
            if not kategori_peraturan.is_active:
                kategori_peraturan.is_active = True; changed = True
            if changed:
                kategori_peraturan.save()
                self.stdout.write('  ✓ Updated: Kategori Peraturan')

        peraturan, created = MenuItem.objects.get_or_create(
            name='Peraturan',
            parent=manajemen_data_group,
            defaults={
                'permission_key': 'manajemen_data.md_peraturan.view',
                'url_name': 'manajemen_data:peraturan_list',
                'icon': 'fas fa-gavel',
                'type': 'module',
                'order': 270,
                'category': 5,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Peraturan')
        else:
            changed = False
            if peraturan.permission_key != 'manajemen_data.md_peraturan.view':
                peraturan.permission_key = 'manajemen_data.md_peraturan.view'; changed = True
            if peraturan.url_name != 'manajemen_data:peraturan_list':
                peraturan.url_name = 'manajemen_data:peraturan_list'; changed = True
            if peraturan.icon != 'fas fa-gavel':
                peraturan.icon = 'fas fa-gavel'; changed = True
            if peraturan.type != 'module':
                peraturan.type = 'module'; changed = True
            if peraturan.order != 270:
                peraturan.order = 270; changed = True
            if (peraturan.category or 0) != 5:
                peraturan.category = 5; changed = True
            if peraturan.parent_id != manajemen_data_group.id:
                peraturan.parent = manajemen_data_group; changed = True
            if not peraturan.is_active:
                peraturan.is_active = True; changed = True
            if changed:
                peraturan.save()
                self.stdout.write('  ✓ Updated: Peraturan')

        tentang, created = MenuItem.objects.get_or_create(
            name='Tentang',
            parent=manajemen_data_group,
            defaults={
                'permission_key': 'manajemen_data.md_tentang.view',
                'url_name': 'manajemen_data:tentang_list',
                'icon': 'fas fa-info-circle',
                'type': 'module',
                'order': 280,
                'is_active': True,
            },
        )
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Tentang')
        else:
            changed = False
            if tentang.permission_key != 'manajemen_data.md_tentang.view':
                tentang.permission_key = 'manajemen_data.md_tentang.view'; changed = True
            if tentang.url_name != 'manajemen_data:tentang_list':
                tentang.url_name = 'manajemen_data:tentang_list'; changed = True
            if tentang.icon != 'fas fa-info-circle':
                tentang.icon = 'fas fa-info-circle'; changed = True
            if tentang.type != 'module':
                tentang.type = 'module'; changed = True
            if tentang.order != 280:
                tentang.order = 280; changed = True
            if tentang.parent_id != manajemen_data_group.id:
                tentang.parent = manajemen_data_group; changed = True
            if not tentang.is_active:
                tentang.is_active = True; changed = True
            if changed:
                tentang.save()
                self.stdout.write('  ✓ Updated: Tentang')

        self.stdout.write('')
        self.stdout.write(f"\n✅ Menu seeding completed! Created: {created_count}")

        # Enforce permanent menu removals (for minimal/baseline deployments)
        if disabled_categories:
            try:
                qs = MenuItem.objects.filter(category__in=list(disabled_categories))
                to_delete = qs.count()
                if to_delete:
                    qs.delete()
                    self.stdout.write(self.style.WARNING(
                        f"🧹 Removed disabled menu categories {sorted(disabled_categories)} (deleted items: {to_delete})"
                    ))
            except Exception:
                pass
