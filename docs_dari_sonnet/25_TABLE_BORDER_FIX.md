# Table Border Fix - Survey Configuration

## Problem
The user complained that the Survey Configuration table didn't have borders and looked different from other tables in the system:
> "kenapa betnuk tabel ini beda kayak no border ni ha? daha da lu pahami doc dari sonnet lu buat senidir in ?"

## Root Cause
The table template was using manual HTML table instead of the proper `django-tables2` pattern with `{% include 'includes/datatable_table_scroll.html' with table=table %}` that provides consistent styling and borders.

## Solution

### 1. Created SurveyConfigurationTable Class
**File:** `apps/survey/tables.py`

Added proper `SurveyConfigurationTable` class with:
- Proper column definitions using `dt_col_attrs()` helpers
- Consistent styling with other tables in the system
- Permission-based action buttons
- Proper rendering methods for complex fields

```python
class SurveyConfigurationTable(tables.Table):
    """Table untuk Konfigurasi Survey"""
    
    selection = tables.CheckBoxColumn(...)
    row_number = tables.Column(...)
    nama_survey = tables.Column(...)
    tahun = tables.Column(...)
    periode = tables.Column(...)
    jumlah_aspek = tables.Column(...)
    jumlah_response = tables.Column(...)
    is_active = tables.Column(...)
    actions = tables.Column(...)
```

### 2. Updated View to Use Table
**File:** `apps/survey/views_survey_config.py`

Changed from raw queryset to proper table:
```python
# Before
context = {
    'configs': qs,
    'total': qs.count(),
    'search_query': search_query,
}

# After  
table = SurveyConfigurationTable(qs)
table.request = request
RequestConfig(request, paginate={'per_page': 10}).configure(table)

context = {
    'table': table,
    'total': qs.count(),
    'search_query': search_query,
}
```

### 3. Fixed Table Template
**File:** `apps/survey/templates/survey_config/partials/_table.html`

Replaced manual HTML table with proper include:
```django
<!-- Before: Manual HTML table -->
<div class="overflow-x-auto">
    <table class="min-w-full bg-white border border-gray-200 rounded-lg">
        <!-- Manual table structure -->
    </table>
</div>

<!-- After: Proper django-tables2 include -->
{% include 'includes/datatable_table_scroll.html' with table=table %}
```

## Benefits

### ✅ Consistent Styling
- Now uses same border/styling system as other tables
- Proper `border-collapse border border-gray-300` classes
- Consistent header and row styling

### ✅ Better Functionality  
- Sortable columns
- Proper pagination
- Bulk actions support
- Permission-based action buttons

### ✅ Maintainable Code
- Follows established patterns from documentation
- Uses reusable table helpers from `apps/common/table_attrs.py`
- Consistent with other table implementations

## Testing

### 1. Run Sample Seeder
```bash
python manage.py seed_sample_survey_config
```

### 2. Access Survey Config List
Navigate to: `http://localhost:8006/survey/config/`

### 3. Verify Table Features
- ✅ Table has proper borders
- ✅ Headers are sortable
- ✅ Pagination works
- ✅ Action buttons show based on permissions
- ✅ Consistent styling with other tables

## Files Modified

1. **apps/survey/tables.py** - Added `SurveyConfigurationTable` class
2. **apps/survey/views_survey_config.py** - Updated to use table instead of raw queryset
3. **apps/survey/templates/survey_config/partials/_table.html** - Fixed to use proper include

## Next Steps

The dynamic survey system is now complete with proper table styling. The system includes:

1. ✅ **Admin Interface** - Super Admin can create/edit survey configurations
2. ✅ **Dynamic Forms** - Forms generated based on admin configuration  
3. ✅ **Modern UI** - Survey 360° interface with sliders
4. ✅ **Proper Tables** - Consistent styling with borders
5. ✅ **Permissions** - Full permission system
6. ✅ **Menu Integration** - Added to Master Survey menu

The user can now:
- Create survey configurations as Super Admin
- Employees fill dynamic forms based on configuration
- View responses and manage data through proper tables
- All with consistent styling and proper borders