"""
Authentication views
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q

User = get_user_model()


# login_view removed - menggunakan landing_page di root URL (/)
# Login logic sekarang ada di core/views.py::landing_page()

def logout_view(request):
    """Logout user and log to ms_log_data"""
    if request.user.is_authenticated:
        user_name = request.user.name
        user_to_log = request.user
        
        # Log manual logout to ms_log_data
        try:
            from core.models import MsLogData
            MsLogData.log_logout(
                user=user_to_log,
                request=request,
                via='web',
                description='Manual logout via aplikasi web'
            )
        except Exception as e:
            # Don't fail logout if logging fails
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to log logout: {e}")
        
        auth_logout(request)
        messages.info(request, f'Anda telah logout. Sampai jumpa, {user_name}!')
    return redirect('/')


@login_required
def profile_view(request):
    """Profile page: view and update basic account info."""
    from apps.manajemen.models import RoleRule
    
    if request.method == 'POST':
        email = (request.POST.get('email') or '').strip()
        if isinstance(email, str) and email.lower() in ('none', 'null', 'undefined', '-'):
            email = ''
        name = (request.POST.get('name') or '').strip()
        if not name:
            first_name = (request.POST.get('first_name') or '').strip()
            last_name = (request.POST.get('last_name') or '').strip()
            name = (f"{first_name} {last_name}".strip())

        request.user.email = email or None
        request.user.name = name or (request.user.name or request.user.username)
        request.user.save()

        is_htmx = request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if is_htmx:
            user_roles = request.user.groups.all()
            user_rules = RoleRule.objects.filter(role__in=user_roles).select_related('rule__module', 'rule__control', 'rule__function')
            context = {
                'user_roles': user_roles,
                'user_rules': user_rules,
                'total_permissions': user_rules.count(),
                'name_value': getattr(request.user, 'name', ''),
                'email_value': (request.user.email or ''),
            }
            resp = render(request, 'accounts/profile.html', context)
            try:
                import json as _json
                resp['HX-Trigger-After-Swap'] = _json.dumps({'profile-form-success': {'message': '✅ Profile berhasil diupdate!'}})
            except Exception:
                pass
            return resp

        messages.success(request, '✅ Profile berhasil diupdate!')
        return redirect('accounts:profile')

    user_roles = request.user.groups.all()
    user_rules = RoleRule.objects.filter(role__in=user_roles).select_related('rule__module', 'rule__control', 'rule__function')
    _email = (request.user.email or '')
    if isinstance(_email, str) and _email.strip().lower() in ('none', 'null', 'undefined'):
        _email = ''
    context = {
        'user_roles': user_roles,
        'user_rules': user_rules,
        'total_permissions': user_rules.count(),
        'name_value': getattr(request.user, 'name', ''),
        'email_value': _email,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def force_change_password_view(request):
    """Force change password view - required for users with default password - supports ESIMPEG API"""
    from django.http import JsonResponse
    from .services import EsimpegAPIService
    
    user = request.user
    
    # Check if user still has default password
    if not user.check_password('Pegawai@Pessel'):
        # Already changed, redirect to dashboard
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        # Check if AJAX request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validasi old password (must be default)
        if old_password != 'Pegawai@Pessel':
            error_msg = 'Password lama salah!'
            if is_ajax:
                return JsonResponse({'success': False, 'message': error_msg})
            messages.error(request, error_msg)
            return render(request, 'accounts/force_change_password.html')
        
        # Validasi new password
        if new_password != confirm_password:
            error_msg = 'Password baru dan konfirmasi tidak cocok!'
            if is_ajax:
                return JsonResponse({'success': False, 'message': error_msg})
            messages.error(request, error_msg)
            return render(request, 'accounts/force_change_password.html')
        
        if len(new_password) < 8:
            error_msg = 'Password minimal 8 karakter!'
            if is_ajax:
                return JsonResponse({'success': False, 'message': error_msg})
            messages.error(request, error_msg)
            return render(request, 'accounts/force_change_password.html')
        
        if new_password == 'Pegawai@Pessel':
            error_msg = 'Password baru tidak boleh sama dengan password default!'
            if is_ajax:
                return JsonResponse({'success': False, 'message': error_msg})
            messages.error(request, error_msg)
            return render(request, 'accounts/force_change_password.html')
        
        # Check if user logged in via API (has token in session)
        esimpeg_token = request.session.get('esimpeg_access_token')
        
        # Update password
        try:
            # If logged in via API, change password via API first
            if esimpeg_token:
                api_service = EsimpegAPIService()
                result = api_service.change_password(esimpeg_token, old_password, new_password)
                
                if not result:
                    error_msg = 'Gagal mengubah password via API ESIMPEG.'
                    if is_ajax:
                        return JsonResponse({'success': False, 'message': error_msg})
                    messages.error(request, error_msg)
                    return render(request, 'accounts/force_change_password.html')
            
            # Update local database password
            user.set_password(new_password)
            
            # Ensure date_joined is set (fix for users migrated from Laravel)
            if not user.date_joined:
                from django.utils import timezone
                user.date_joined = timezone.now()
            
            user.save()
            
            # DO NOT update session auth hash - force logout after password change
            # update_session_auth_hash(request, user)  # REMOVED
            
            # Log password change SUCCESS to ms_log_data
            try:
                from core.models import MsLogData
                MsLogData.objects.create(
                    user_id=user.id,
                    action='password_change',
                    table_name='users',
                    record_id=user.id,
                    old_data={'note': 'Password changed from default (forced)'},
                    new_data={'success': True, 'via': 'api' if esimpeg_token else 'web'},
                    ip_address=request.META.get('REMOTE_ADDR', ''),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
            except Exception as log_err:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to log password change: {log_err}")
            
            # Logout user (force re-login with new password)
            from django.contrib.auth import logout as auth_logout
            auth_logout(request)
                
        except Exception as e:
            # Log password change ERROR to ms_log_data
            import traceback
            error_traceback = traceback.format_exc()
            
            try:
                from core.models import MsLogData
                MsLogData.log_error(
                    user=user,
                    action='password_change',
                    error_message=str(e),
                    error_details={
                        'error_type': type(e).__name__,
                        'traceback': error_traceback,
                        'username': user.username,
                        'has_date_joined': bool(user.date_joined)
                    },
                    request=request,
                    via='web'
                )
            except:
                pass  # Ignore error logging failure
            
            # Return error response
            error_msg = f'Gagal mengubah password: {str(e)}'
            if is_ajax:
                return JsonResponse({'success': False, 'message': error_msg})
            messages.error(request, error_msg)
            return render(request, 'accounts/force_change_password.html')
        
        success_msg = 'Password berhasil diubah! Silakan login kembali dengan password baru.'
        
        if is_ajax:
            return JsonResponse({
                'success': True,
                'message': success_msg,
                'redirect_url': '/',  # Redirect to login page
                'username': user.username,
                'full_name': user.get_full_name() or user.username
            })
        
        messages.success(request, success_msg)
        return redirect('/')  # Redirect to login page
    
    return render(request, 'accounts/force_change_password.html')


@login_required
def change_password_view(request):
    """Change password view (AJAX/HTMX supported) - supports both local DB and ESIMPEG API."""
    from django.http import HttpResponse
    from .services import EsimpegAPIService
    
    if request.method == 'POST':
        is_htmx = request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        old_password = (request.POST.get('old_password') or '').strip()
        new_password1 = (request.POST.get('new_password1') or '').strip()
        new_password2 = (request.POST.get('new_password2') or '').strip()
        errors_list = []
        field_errors = {}

        # Basic validation
        if not old_password:
            msg = 'Password lama harus diisi.'
            field_errors.setdefault('old_password', []).append(msg)
            errors_list.append(msg)
        if not new_password1:
            msg = 'Password baru harus diisi.'
            field_errors.setdefault('new_password1', []).append(msg)
            errors_list.append(msg)
        if not new_password2:
            msg = 'Konfirmasi password baru harus diisi.'
            field_errors.setdefault('new_password2', []).append(msg)
            errors_list.append(msg)
        
        if not errors_list:
            if new_password1 != new_password2:
                msg = 'Password baru tidak cocok!'
                field_errors.setdefault('new_password2', []).append(msg)
                errors_list.append(msg)
            elif len(new_password1) < 8:
                msg = 'Password minimal 8 karakter!'
                field_errors.setdefault('new_password1', []).append(msg)
                errors_list.append(msg)

        if errors_list:
            if is_htmx:
                ctx = {'field_errors': field_errors}
                resp = render(request, 'accounts/change_password.html', ctx)
                try:
                    import json as _json
                    resp['HX-Trigger-After-Swap'] = _json.dumps({'change-password-form-invalid': {'errors': errors_list, 'fieldErrors': field_errors}})
                except Exception:
                    pass
                return resp
            else:
                for e in errors_list:
                    messages.error(request, e)
                return render(request, 'accounts/change_password.html', {'errors_list': errors_list, 'field_errors': field_errors})

        # Check if user logged in via API (has token in session)
        esimpeg_token = request.session.get('esimpeg_access_token')
        
        if esimpeg_token:
            # Change password via ESIMPEG API
            api_service = EsimpegAPIService()
            result = api_service.change_password(esimpeg_token, old_password, new_password1)
            
            if result:
                # Also update local database password
                request.user.set_password(new_password1)
                request.user.save()
                
                # DO NOT update session auth hash - force logout
                # update_session_auth_hash(request, request.user)  # REMOVED
                
                # Log password change SUCCESS
                try:
                    from core.models import MsLogData
                    MsLogData.objects.create(
                        user_id=request.user.id,
                        action='password_change',
                        table_name='users',
                        record_id=request.user.id,
                        old_data={'note': 'Password changed via ESIMPEG API'},
                        new_data={'success': True, 'via': 'api'},
                        ip_address=request.META.get('REMOTE_ADDR', ''),
                        user_agent=request.META.get('HTTP_USER_AGENT', '')
                    )
                except Exception:
                    pass
                
                # Logout user (force re-login with new password)
                from django.contrib.auth import logout as auth_logout
                auth_logout(request)
                
                success_msg = '✅ Password berhasil diubah! Silakan login kembali dengan password baru.'
                if is_htmx:
                    resp = HttpResponse(status=204)
                    try:
                        import json as _json
                        resp['HX-Trigger'] = _json.dumps({'change-password-form-success': {'message': success_msg, 'redirect': '/'}})
                    except Exception:
                        pass
                    return resp
                messages.success(request, success_msg)
                return redirect('/')
            else:
                msg = 'Gagal mengubah password via API. Password lama mungkin salah.'
                field_errors.setdefault('old_password', []).append(msg)
                errors_list.append(msg)
                
                if is_htmx:
                    ctx = {'field_errors': field_errors}
                    resp = render(request, 'accounts/change_password.html', ctx)
                    try:
                        import json as _json
                        resp['HX-Trigger-After-Swap'] = _json.dumps({'change-password-form-invalid': {'errors': errors_list, 'fieldErrors': field_errors}})
                    except Exception:
                        pass
                    return resp
                else:
                    messages.error(request, msg)
                    return render(request, 'accounts/change_password.html', {'errors_list': errors_list, 'field_errors': field_errors})
        else:
            # Change password locally (database only)
            if not request.user.check_password(old_password):
                msg = 'Password lama salah!'
                field_errors.setdefault('old_password', []).append(msg)
                errors_list.append(msg)
                
                if is_htmx:
                    ctx = {'field_errors': field_errors}
                    resp = render(request, 'accounts/change_password.html', ctx)
                    try:
                        import json as _json
                        resp['HX-Trigger-After-Swap'] = _json.dumps({'change-password-form-invalid': {'errors': errors_list, 'fieldErrors': field_errors}})
                    except Exception:
                        pass
                    return resp
                else:
                    messages.error(request, msg)
                    return render(request, 'accounts/change_password.html', {'errors_list': errors_list, 'field_errors': field_errors})
            
            # Update password locally
            request.user.set_password(new_password1)
            request.user.save()
            
            # DO NOT update session auth hash - force logout
            # update_session_auth_hash(request, request.user)  # REMOVED
            
            # Log password change SUCCESS
            try:
                from core.models import MsLogData
                MsLogData.objects.create(
                    user_id=request.user.id,
                    action='password_change',
                    table_name='users',
                    record_id=request.user.id,
                    old_data={'note': 'Password changed locally'},
                    new_data={'success': True, 'via': 'web'},
                    ip_address=request.META.get('REMOTE_ADDR', ''),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
            except Exception:
                pass
            
            # Logout user (force re-login with new password)
            from django.contrib.auth import logout as auth_logout
            auth_logout(request)
            
            success_msg = '✅ Password berhasil diubah! Silakan login kembali dengan password baru.'
            if is_htmx:
                resp = HttpResponse(status=204)
                try:
                    import json as _json
                    resp['HX-Trigger'] = _json.dumps({'change-password-form-success': {'message': success_msg, 'redirect': '/'}})
                except Exception:
                    pass
                return resp
            messages.success(request, success_msg)
            return redirect('/')

    return render(request, 'accounts/change_password.html')
