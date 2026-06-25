from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from apps.manajemen.models import PermissionModule, PermissionControl, PermissionFunction, PermissionRule, RoleRule


class Command(BaseCommand):
    help = 'Seed permissions for Responden Survey and Jawaban Survey'

    def handle(self, *args, **options):
        self.stdout.write('Creating permissions for Responden Survey and Jawaban Survey...')
        
        # Get the survey module
        try:
            survey_module = PermissionModule.objects.get(nama_module='survey')
        except PermissionModule.DoesNotExist:
            self.stdout.write(self.style.ERROR('Survey module not found!'))
            return
        
        # Create or get controls
        responden_control, created = PermissionControl.objects.get_or_create(
            nama_kontrol='responden_survey',
            defaults={
                'label_kontrol': 'Responden Survey',
                'deskripsi_kontrol': 'Manajemen data responden yang melakukan penilaian survey'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Created control: responden_survey'))
        
        jawaban_control, created = PermissionControl.objects.get_or_create(
            nama_kontrol='jawaban_survey',
            defaults={
                'label_kontrol': 'Jawaban Survey',
                'deskripsi_kontrol': 'Manajemen jawaban survey dari responden'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Created control: jawaban_survey'))
        
        periode_control, created = PermissionControl.objects.get_or_create(
            nama_kontrol='periode_survey',
            defaults={
                'label_kontrol': 'Periode Survey',
                'deskripsi_kontrol': 'Manajemen periode waktu survey dapat diakses'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Created control: periode_survey'))
        
        # Get functions
        functions_needed = ['view', 'create', 'edit', 'delete', 'export', 'bulk_delete']
        functions = {}
        for func_name in functions_needed:
            try:
                functions[func_name] = PermissionFunction.objects.get(nama_fungsi=func_name)
            except PermissionFunction.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Function {func_name} not found!'))
                return
        
        # Create permission rules
        controls = [
            ('responden_survey', responden_control),
            ('jawaban_survey', jawaban_control),
            ('periode_survey', periode_control)
        ]
        
        created_count = 0
        for control_name, control_obj in controls:
            for func_name, func_obj in functions.items():
                rule, created = PermissionRule.objects.get_or_create(
                    module=survey_module,
                    control=control_obj,
                    function=func_obj,
                    defaults={'is_active': True}
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Created rule: survey.{control_name}.{func_name}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'- Exists rule: survey.{control_name}.{func_name}')
                    )
        
        # Grant all permissions to Super Admin group
        try:
            super_admin_group = Group.objects.get(name='Super Admin')
            
            # Get all rules for the new controls
            responden_rules = PermissionRule.objects.filter(
                module=survey_module,
                control=responden_control
            )
            jawaban_rules = PermissionRule.objects.filter(
                module=survey_module,
                control=jawaban_control
            )
            periode_rules = PermissionRule.objects.filter(
                module=survey_module,
                control=periode_control
            )
            
            all_rules = list(responden_rules) + list(jawaban_rules) + list(periode_rules)
            
            # Add rules to Super Admin group
            for rule in all_rules:
                role_rule, created = RoleRule.objects.get_or_create(
                    role=super_admin_group,
                    rule=rule
                )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Granted: {rule.permission_string} to Super Admin')
                    )
            
        except Group.DoesNotExist:
            self.stdout.write(
                self.style.WARNING('⚠ Super Admin group not found, skipping permission assignment')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Successfully created {created_count} new permission rules!')
        )
        self.stdout.write('📋 Summary:')
        self.stdout.write(f'   • Responden Survey: {len(functions_needed)} permissions')
        self.stdout.write(f'   • Jawaban Survey: {len(functions_needed)} permissions')
        self.stdout.write(f'   • Periode Survey: {len(functions_needed)} permissions')
        self.stdout.write(f'   • Total: {len(functions_needed) * 3} permissions')