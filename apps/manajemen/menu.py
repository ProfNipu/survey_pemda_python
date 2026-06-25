from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse
import json
from django.db.models import Q
from django_tables2 import RequestConfig

from apps.manajemen.decorators import permission_required_403
from apps.manajemen.models import MenuItem
from apps.manajemen.forms import MenuItemForm
from apps.manajemen.tables import MenuItemTable


@ensure_csrf_cookie
@permission_required_403('pengaturan', 'manajemen_menu', 'view')
def menu_list(request):
    qs = MenuItem.objects.select_related('parent').all()
    search_query = request.GET.get('search', '').strip()
    category_filter = request.GET.get('category', '').strip()
    if search_query:
        qs = qs.filter(
            Q(name__icontains=search_query) |
            Q(permission_key__icontains=search_query) |
            Q(url_name__icontains=search_query) |
            Q(external_url__icontains=search_query)
        )
    if category_filter != '':
        try:
            qs = qs.filter(category=int(category_filter))
        except ValueError:
            pass
    qs = qs.order_by('category', 'parent_id', 'order', 'name')

    total = qs.count()
    table = MenuItemTable(qs)
    per_page = request.GET.get('per_page', '10')
    try:
        per_page = int(per_page)
        if per_page not in [10, 25, 50, 100]:
            per_page = 10
    except (ValueError, TypeError):
        per_page = 10
    RequestConfig(request, paginate={'per_page': per_page}).configure(table)

    context = {
        'table': table,
        'total': total,
        'search_query': search_query,
    }
    is_htmx = request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_htmx:
        return render(request, 'manajemen_aplikasi/access/ma_ap_menu/partials/_table.html', context)
    return render(request, 'manajemen_aplikasi/access/ma_ap_menu/list.html', context)


@permission_required_403('pengaturan', 'manajemen_menu', 'create')
def menu_create(request):
    if request.method == 'POST':
        form = MenuItemForm(request.POST)
        is_htmx = request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if form.is_valid():
            form.save()
            if is_htmx:
                resp = HttpResponse(status=204)
                resp['HX-Trigger'] = json.dumps({'menu-form-success': {'message': 'Menu berhasil dibuat', 'redirect': reverse('manajemen_aplikasi:menu_list')}})
                return resp
            messages.success(request, 'Menu berhasil dibuat')
            return redirect('manajemen_aplikasi:menu_list')
        # invalid
        if is_htmx:
            errors = []
            field_errors = {}
            try:
                for field, errs in form.errors.items():
                    field_errors[field] = [str(er) for er in errs]
                    for er in errs:
                        errors.append(str(er))
            except Exception:
                errors = ['Periksa kembali input Anda.']
            # Do NOT pass errors_list in HTMX path; JS will render summary to avoid duplicates
            resp = render(request, 'manajemen_aplikasi/access/ma_ap_menu/form.html', {'form': form})
            resp['HX-Trigger-After-Swap'] = json.dumps({'menu-form-invalid': {'errors': errors, 'fieldErrors': field_errors}})
            return resp
        else:
            for field, errs in form.errors.items():
                for er in errs:
                    messages.error(request, er)
            # Do not pass errors_list here to avoid duplicate summary with Django messages
            return render(request, 'manajemen_aplikasi/access/ma_ap_menu/form.html', {'form': form})
    else:
        form = MenuItemForm()
    return render(request, 'manajemen_aplikasi/access/ma_ap_menu/form.html', {'form': form})


@permission_required_403('pengaturan', 'manajemen_menu', 'edit')
def menu_edit(request, menu_id):
    obj = get_object_or_404(MenuItem, id=menu_id)
    if request.method == 'POST':
        form = MenuItemForm(request.POST, instance=obj)
        is_htmx = request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if form.is_valid():
            # prevent selecting itself as parent
            parent = form.cleaned_data.get('parent')
            if parent and parent.id == obj.id:
                form.add_error('parent', 'Parent tidak boleh dirinya sendiri')
            else:
                form.save()
                if is_htmx:
                    resp = HttpResponse(status=204)
                    resp['HX-Trigger'] = json.dumps({'menu-form-success': {'message': 'Menu berhasil diupdate', 'redirect': reverse('manajemen_aplikasi:menu_list')}})
                    return resp
                messages.success(request, 'Menu berhasil diupdate')
                return redirect('manajemen_aplikasi:menu_list')
        # invalid
        if is_htmx:
            errors = []
            field_errors = {}
            try:
                for field, errs in form.errors.items():
                    field_errors[field] = [str(er) for er in errs]
                    for er in errs:
                        errors.append(str(er))
            except Exception:
                errors = ['Periksa kembali input Anda.']
            # Do NOT pass errors_list in HTMX path; JS will render summary to avoid duplicates
            resp = render(request, 'manajemen_aplikasi/access/ma_ap_menu/form.html', {'form': form, 'edit_mode': True, 'menu_item': obj})
            resp['HX-Trigger-After-Swap'] = json.dumps({'menu-form-invalid': {'errors': errors, 'fieldErrors': field_errors}})
            return resp
        else:
            for field, errs in form.errors.items():
                for er in errs:
                    messages.error(request, er)
            return render(request, 'manajemen_aplikasi/access/ma_ap_menu/form.html', {'form': form, 'edit_mode': True, 'menu_item': obj})
    else:
        form = MenuItemForm(instance=obj)
    return render(request, 'manajemen_aplikasi/access/ma_ap_menu/form.html', {'form': form, 'edit_mode': True, 'menu_item': obj})


@permission_required_403('pengaturan', 'manajemen_menu', 'delete')
def menu_delete(request, menu_id):
    obj = get_object_or_404(MenuItem, id=menu_id)
    if request.method == 'POST':
        name = obj.name
        obj.delete()
        messages.success(request, f'Menu "{name}" berhasil dihapus')
        return redirect('manajemen_aplikasi:menu_list')
    children = MenuItem.objects.filter(parent=obj).count()
    return render(request, 'manajemen_aplikasi/access/ma_ap_menu/delete.html', {'menu_item': obj, 'child_count': children})
