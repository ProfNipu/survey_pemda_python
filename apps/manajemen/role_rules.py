from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied

from apps.manajemen.decorators import permission_required_403
from apps.manajemen.models import PermissionRule, RoleRule


@permission_required_403('pengaturan', 'permission_role_rule', 'view')
def role_rule_manage(request, role_id):
    """Manage rules for a specific role"""
    role = get_object_or_404(Group, id=role_id)

    if request.method == 'POST':
        try:
            from apps.manajemen.helpers import check_permission
            if not check_permission(request.user, 'pengaturan', 'permission_role_rule', 'edit'):
                raise PermissionDenied
        except PermissionDenied:
            raise
        except Exception:
            raise PermissionDenied

        rule_ids = request.POST.getlist('rules')

        # Clear existing assignments
        RoleRule.objects.filter(role=role).delete()

        # Create new assignments
        if rule_ids:
            rules = PermissionRule.objects.filter(id__in=rule_ids)
            for rule in rules:
                RoleRule.objects.create(role=role, rule=rule)

        success_message = f'✅ Rules untuk role "{role.name}" berhasil diupdate!'
        
        # AJAX Response
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': success_message})

        messages.success(request, success_message)
        # Redirect to granular dashboard (canonical name)
        return redirect('manajemen_aplikasi:dashboard')

    # Get all rules grouped by module
    all_rules = PermissionRule.objects.select_related(
        'module', 'control', 'function'
    ).filter(is_active=True).order_by('module__order', 'control__nama_kontrol', 'function__nama_fungsi')

    # Get current role rules
    current_rule_ids = set(RoleRule.objects.filter(role=role).values_list('rule_id', flat=True))

    # Group by module
    rules_by_module = {}
    for rule in all_rules:
        module_name = rule.module.label_module
        if module_name not in rules_by_module:
            rules_by_module[module_name] = []

        rule.is_selected = rule.id in current_rule_ids
        rules_by_module[module_name].append(rule)

    context = {
        'role': role,
        'rules_by_module': rules_by_module,
        'selected_count': len(current_rule_ids),
    }

    return render(request, 'manajemen_aplikasi/access/ma_ap_roles/role_rule_manage.html', context)
