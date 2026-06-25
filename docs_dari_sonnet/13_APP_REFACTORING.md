# App Refactoring - survey_jpt → survey

## Overview
Melakukan refactoring besar-besaran untuk mengubah nama app dari `survey_jpt` menjadi `survey` dan mengubah template folder dari `survey_jpt` menjadi `master_survey`.

## Changes Made

### 1. App Structure Changes
```bash
# App folder renamed
apps/survey_jpt/ → apps/survey/

# Template folder renamed  
apps/survey/templates/survey_jpt/ → apps/survey/templates/master_survey/
```

### 2. Configuration Updates

#### settings.py
```python
# Before
'apps.survey_jpt',  # Survey JPT (Dynamic Survey System)

# After  
'apps.survey',  # Survey (Dynamic Survey System)
```

#### core/urls.py
```python
# Before
path('survey/', include('apps.survey_jpt.urls')),

# After
path('survey/', include('apps.survey.urls')),
```

### 3. App Configuration Updates

#### apps.py
```python
# Before
class SurveyJptConfig(AppConfig):
    name = 'apps.survey_jpt'
    verbose_name = 'Survey JPT'

# After
class SurveyConfig(AppConfig):
    name = 'apps.survey'
    verbose_name = 'Survey'
```

#### __init__.py
```python
# Before
default_app_config = 'apps.survey_jpt.apps.SurveyJptConfig'

# After
default_app_config = 'apps.survey.apps.SurveyConfig'
```

#### urls.py
```python
# Before
app_name = 'survey_jpt'

# After
app_name = 'survey'
```

### 4. Template References Updated

All template files updated from:
```html
<!-- Before -->
{% url 'survey_jpt:jenis_survey_list' %}
'survey_jpt/jenis_survey/list.html'

<!-- After -->
{% url 'survey:jenis_survey_list' %}
'master_survey/jenis_survey/list.html'
```

### 5. Views & Tables Updated

All view and table references updated:
```python
# Before
return render(request, 'survey_jpt/jenis_survey/list.html', context)
reverse('survey_jpt:jenis_survey_edit', args=[record.id])

# After  
return render(request, 'master_survey/jenis_survey/list.html', context)
reverse('survey:jenis_survey_edit', args=[record.id])
```

### 6. Migration Updates

Fixed migration dependencies:
```python
# Before
dependencies = [('survey_jpt', '0001_initial')]
to='survey_jpt.jenissurvey'

# After
dependencies = [('survey', '0001_initial')]  
to='survey.jenissurvey'
```

### 7. Management Commands Updated

All seeder commands updated:
```python
# Before
'url_name': 'survey_jpt:jenis_survey_list'

# After
'url_name': 'survey:jenis_survey_list'
```

## Files Modified

### Core Files
- `core/settings.py` - Updated INSTALLED_APPS
- `core/urls.py` - Updated URL include path

### App Files  
- `apps/survey/apps.py` - Updated app config
- `apps/survey/__init__.py` - Updated default app config
- `apps/survey/urls.py` - Updated app_name
- `apps/survey/views.py` - Updated all template paths
- `apps/survey/tables.py` - Updated all URL references
- `apps/survey/migrations/0001_initial.py` - Fixed model references
- `apps/survey/migrations/0002_periodesurvey.py` - Fixed dependencies

### Management Commands
- `apps/survey/management/commands/seed_survey_menu.py`
- `apps/survey/management/commands/seed_survey_permissions.py`
- `apps/survey/management/commands/seed_periode_survey_permissions.py`
- `apps/survey/management/commands/seed_responden_jawaban_permissions.py`
- `apps/survey/management/commands/grant_survey_to_prakom.py`

### Template Files
All template files in `apps/survey/templates/master_survey/`:
- `jenis_survey/` - list.html, form.html, delete.html, partials/_table.html
- `pertanyaan_survey/` - list.html, form.html, delete.html, partials/_table.html  
- `responden_survey/` - list.html, form.html, delete.html, detail.html, partials/_table.html
- `jawaban_survey/` - list.html, form.html, delete.html, partials/_table.html
- `periode_survey/` - list.html, form.html, delete.html, partials/_table.html

## URL Namespace Changes

### Before (survey_jpt)
```
survey_jpt:jenis_survey_list → /survey/jenis-survey/
survey_jpt:pertanyaan_survey_list → /survey/pertanyaan-survey/
survey_jpt:responden_survey_list → /survey/responden-survey/
survey_jpt:jawaban_survey_list → /survey/jawaban-survey/
survey_jpt:periode_survey_list → /survey/periode-survey/
```

### After (survey)
```
survey:jenis_survey_list → /survey/jenis-survey/
survey:pertanyaan_survey_list → /survey/pertanyaan-survey/
survey:responden_survey_list → /survey/responden-survey/
survey:jawaban_survey_list → /survey/jawaban-survey/
survey:periode_survey_list → /survey/periode-survey/
```

## Template Path Changes

### Before
```
survey_jpt/jenis_survey/list.html
survey_jpt/pertanyaan_survey/form.html
survey_jpt/responden_survey/detail.html
survey_jpt/jawaban_survey/delete.html
survey_jpt/periode_survey/partials/_table.html
```

### After
```
master_survey/jenis_survey/list.html
master_survey/pertanyaan_survey/form.html
master_survey/responden_survey/detail.html
master_survey/jawaban_survey/delete.html
master_survey/periode_survey/partials/_table.html
```

## Migration Handling

Since tables already existed from the old app, migrations were fake-applied:
```bash
docker exec survey_pemda_python_app python manage.py migrate survey --fake
```

## Verification

### URL Resolution Test
```
✅ survey:jenis_survey_list → /survey/jenis-survey/
✅ survey:pertanyaan_survey_list → /survey/pertanyaan-survey/
✅ survey:responden_survey_list → /survey/responden-survey/
✅ survey:jawaban_survey_list → /survey/jawaban-survey/
✅ survey:periode_survey_list → /survey/periode-survey/
```

### Menu System Test
```
Survey:
  - Master Survey: #
    - Jenis Survey: /survey/jenis-survey/
    - Pertanyaan Survey: /survey/pertanyaan-survey/
    - Responden Survey: /survey/responden-survey/
    - Jawaban Survey: /survey/jawaban-survey/
    - Periode Survey: /survey/periode-survey/
```

## Status
✅ **COMPLETED** - App successfully refactored from `survey_jpt` to `survey` with template folder renamed to `master_survey`. All URLs, templates, and references updated accordingly.

## Impact
- **URL Namespace**: Changed from `survey_jpt:` to `survey:`
- **Template Path**: Changed from `survey_jpt/` to `master_survey/`
- **App Name**: Changed from `apps.survey_jpt` to `apps.survey`
- **Backward Compatibility**: None - this is a breaking change requiring full refactoring