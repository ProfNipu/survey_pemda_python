"""
Audit Logger Utility for CRUD Operations
Easy to use wrapper for ms_log_data logging

Usage:
    from core.audit_logger import audit_create, audit_update, audit_delete
    
    # In your view
    audit_create(request.user, pegawai, request)
    audit_update(request.user, pegawai, old_values, request)
    audit_delete(request.user, pegawai, request)
"""
from typing import Dict, Any, Optional
from django.http import HttpRequest
from django.db import models
from core.models import MsLogData


def get_model_data(instance: models.Model, fields: Optional[list] = None) -> Dict[str, Any]:
    """
    Extract model instance data as dictionary
    
    Args:
        instance: Django model instance
        fields: List of field names to include (None = all fields)
    
    Returns:
        Dictionary of field values
    """
    if fields is None:
        # Get all fields except auto-generated ones
        fields = [f.name for f in instance._meta.fields 
                 if f.name not in ['id', 'created_at', 'updated_at', 'deleted_at']]
    
    data = {}
    for field_name in fields:
        try:
            value = getattr(instance, field_name)
            # Convert to serializable format
            if isinstance(value, models.Model):
                data[field_name] = value.pk
            elif hasattr(value, 'isoformat'):  # datetime, date
                data[field_name] = value.isoformat()
            else:
                data[field_name] = str(value) if value is not None else None
        except AttributeError:
            pass
    
    return data


def get_changed_fields(instance: models.Model, old_values: Dict[str, Any]) -> tuple:
    """
    Get only changed fields between old and new values
    
    Args:
        instance: Current model instance (new values)
        old_values: Dictionary of old values
    
    Returns:
        Tuple of (old_data, new_data) with only changed fields
    """
    old_data = {}
    new_data = {}
    
    current_values = get_model_data(instance)
    
    for field, old_value in old_values.items():
        new_value = current_values.get(field)
        if old_value != new_value:
            old_data[field] = old_value
            new_data[field] = new_value
    
    return old_data, new_data


def audit_create(
    user,
    instance: models.Model,
    request: Optional[HttpRequest] = None,
    description: Optional[str] = None,
    fields: Optional[list] = None
):
    """
    Log data creation
    
    Args:
        user: User who created the record
        instance: Created model instance
        request: Django request object (optional)
        description: Custom description (optional)
        fields: List of fields to log (None = all)
    
    Example:
        # After creating pegawai
        pegawai = Pegawai.objects.create(nama='John', nip='123')
        audit_create(request.user, pegawai, request)
        
        # With custom description
        audit_create(
            request.user, 
            pegawai, 
            request,
            description='Tambah pegawai baru via import'
        )
    """
    table_name = instance._meta.db_table
    record_id = instance.pk
    data = get_model_data(instance, fields)
    
    return MsLogData.log_create(
        user=user,
        table_name=table_name,
        record_id=record_id,
        data=data,
        request=request,
        description=description or f'Create {instance._meta.verbose_name}'
    )


def audit_update(
    user,
    instance: models.Model,
    old_values: Dict[str, Any],
    request: Optional[HttpRequest] = None,
    description: Optional[str] = None,
    only_changed: bool = True
):
    """
    Log data update
    
    Args:
        user: User who updated the record
        instance: Updated model instance (with new values)
        old_values: Dictionary of old values
        request: Django request object (optional)
        description: Custom description (optional)
        only_changed: Log only changed fields (default: True)
    
    Example:
        # Before update
        old_values = {'jabatan': pegawai.jabatan}
        
        # Do update
        pegawai.jabatan = 'Kepala Bagian'
        pegawai.save()
        
        # Log update
        audit_update(request.user, pegawai, old_values, request)
    """
    table_name = instance._meta.db_table
    record_id = instance.pk
    
    if only_changed:
        old_data, new_data = get_changed_fields(instance, old_values)
    else:
        old_data = old_values
        new_data = get_model_data(instance)
    
    # Don't log if nothing changed
    if not old_data:
        return None
    
    return MsLogData.log_update(
        user=user,
        table_name=table_name,
        record_id=record_id,
        old_data=old_data,
        new_data=new_data,
        request=request,
        description=description or f'Update {instance._meta.verbose_name}'
    )


def audit_delete(
    user,
    instance: models.Model,
    request: Optional[HttpRequest] = None,
    description: Optional[str] = None,
    fields: Optional[list] = None
):
    """
    Log data deletion
    
    Args:
        user: User who deleted the record
        instance: Model instance being deleted
        request: Django request object (optional)
        description: Custom description (optional)
        fields: List of fields to log (None = all)
    
    Example:
        # Before delete
        audit_delete(request.user, pegawai, request)
        
        # Then delete
        pegawai.delete()
    """
    table_name = instance._meta.db_table
    record_id = instance.pk
    data = get_model_data(instance, fields)
    
    return MsLogData.log_delete(
        user=user,
        table_name=table_name,
        record_id=record_id,
        data=data,
        request=request,
        description=description or f'Delete {instance._meta.verbose_name}'
    )


def audit_bulk_create(
    user,
    model_class: type,
    instances: list,
    request: Optional[HttpRequest] = None,
    description: Optional[str] = None
):
    """
    Log bulk creation
    
    Args:
        user: User who created the records
        model_class: Model class
        instances: List of created instances
        request: Django request object (optional)
        description: Custom description (optional)
    
    Example:
        pegawai_list = Pegawai.objects.bulk_create([...])
        audit_bulk_create(request.user, Pegawai, pegawai_list, request)
    """
    table_name = model_class._meta.db_table
    count = len(instances)
    
    return MsLogData.log_create(
        user=user,
        table_name=table_name,
        record_id=None,
        data={
            'count': count,
            'records': [inst.pk for inst in instances if inst.pk]
        },
        request=request,
        description=description or f'Bulk create {count} {model_class._meta.verbose_name_plural}'
    )


def audit_bulk_update(
    user,
    model_class: type,
    count: int,
    fields: list,
    request: Optional[HttpRequest] = None,
    description: Optional[str] = None
):
    """
    Log bulk update
    
    Args:
        user: User who updated the records
        model_class: Model class
        count: Number of updated records
        fields: List of updated field names
        request: Django request object (optional)
        description: Custom description (optional)
    
    Example:
        updated = Pegawai.objects.filter(...).update(status='active')
        audit_bulk_update(request.user, Pegawai, updated, ['status'], request)
    """
    table_name = model_class._meta.db_table
    
    return MsLogData.log_update(
        user=user,
        table_name=table_name,
        record_id=None,
        old_data={'count': count, 'fields': fields},
        new_data={'count': count, 'fields': fields},
        request=request,
        description=description or f'Bulk update {count} {model_class._meta.verbose_name_plural}'
    )


def audit_bulk_delete(
    user,
    model_class: type,
    count: int,
    request: Optional[HttpRequest] = None,
    description: Optional[str] = None
):
    """
    Log bulk deletion
    
    Args:
        user: User who deleted the records
        model_class: Model class
        count: Number of deleted records
        request: Django request object (optional)
        description: Custom description (optional)
    
    Example:
        deleted, _ = Pegawai.objects.filter(...).delete()
        audit_bulk_delete(request.user, Pegawai, deleted, request)
    """
    table_name = model_class._meta.db_table
    
    return MsLogData.log_delete(
        user=user,
        table_name=table_name,
        record_id=None,
        data={'count': count},
        request=request,
        description=description or f'Bulk delete {count} {model_class._meta.verbose_name_plural}'
    )
