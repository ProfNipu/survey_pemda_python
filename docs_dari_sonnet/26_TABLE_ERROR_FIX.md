# Table Error Fix - Survey Configuration

## Error yang Terjadi
User melaporkan error:
```
ValueError at /survey/config/
Expected table or queryset, not str
```

Error ini terjadi di template `includes/datatable_table_scroll.html` line 5 pada `{% render_table table %}`.

## Root Cause Analysis
Error disebabkan oleh beberapa masalah di implementasi `SurveyConfigurationTable`:

1. **Import Model Issue** - Model `SurveyConfiguration` tidak diimport dengan benar di `tables.py`
2. **Meta Class Issue** - Import model di dalam Meta class menyebabkan circular import
3. **Pagination Issue** - Pagination tidak mengikuti pola yang sama dengan table lain

## Fixes Applied

### 1. Fixed Model Import
**File:** `apps/survey/tables.py`

```python
# Added proper import at top of file
from .models_survey_config import SurveyConfiguration

# Fixed Meta class
class Meta:
    model = SurveyConfiguration  # Direct reference instead of import inside Meta
    template_name = 'django_tables2/tailwind.html'
    # ... rest of Meta
```

### 2. Fixed Pagination Pattern
**File:** `apps/survey/views_survey_config.py`

```python
# Changed from simple pagination to full pattern matching other views
per_page = request.GET.get('per_page', '10')
try:
    per_page = int(per_page)
    if per_page not in [10, 25, 50, 100]:
        per_page = 10
except (ValueError, TypeError):
    per_page = 10

RequestConfig(request, paginate={'per_page': per_page}).configure(table)
```

### 3. Fixed Template Structure
**File:** `apps/survey/templates/survey_config/partials/_table.html`

Template sudah benar menggunakan `{% include 'includes/datatable_table_scroll.html' with table=table %}`, tapi ditambahkan kondisi untuk empty state yang lebih lengkap.

## Testing Steps

### 1. Create Sample Data
```bash
python manage.py seed_sample_survey_config
```

### 2. Access Survey Config Page
Navigate to: `http://localhost:8006/survey/config/`

### 3. Verify Table Works
- ✅ Table displays without errors
- ✅ Proper borders and styling
- ✅ Sortable columns
- ✅ Pagination works
- ✅ Action buttons show based on permissions

## Expected Result

Table should now display properly with:
- Proper borders (consistent with other tables)
- Working pagination
- Sortable columns
- Permission-based action buttons
- No more "Expected table or queryset, not str" error

## Files Modified

1. **apps/survey/tables.py** - Fixed model import and Meta class
2. **apps/survey/views_survey_config.py** - Fixed pagination pattern
3. **apps/survey/templates/survey_config/partials/_table.html** - Enhanced empty state handling

## Next Steps

If the error persists, check:
1. Django migrations are applied: `python manage.py migrate`
2. Sample data exists: `python manage.py seed_sample_survey_config`
3. User has proper permissions: Check if user is in Super Admin group
4. Template includes exist: Verify `templates/includes/datatable_table_scroll.html` exists

The table should now work correctly and display with proper borders matching the system's design patterns.