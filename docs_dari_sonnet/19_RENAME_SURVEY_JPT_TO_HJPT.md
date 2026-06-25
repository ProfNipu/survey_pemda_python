# Rename Survey JPT to Survey HJPT

## Overview
Renamed the template folder from `survey_jpt` to `survey_hjpt` as requested by the user. This change affects the template organization for Penilaian JPT functionality.

## Changes Made

### 1. Template Folder Structure
**Before:**
```
apps/survey/templates/
├── master_survey/
│   ├── jenis_survey/
│   ├── pertanyaan_survey/
│   ├── responden_survey/
│   ├── jawaban_survey/
│   └── periode_survey/
└── survey_jpt/                 # ❌ Old name
    └── penilaian_jpt/
        ├── list.html
        ├── form.html
        ├── detail.html
        ├── delete.html
        ├── report.html
        └── partials/
            └── _table.html
```

**After:**
```
apps/survey/templates/
├── master_survey/
│   ├── jenis_survey/
│   ├── pertanyaan_survey/
│   ├── responden_survey/
│   ├── jawaban_survey/
│   └── periode_survey/
└── survey_hjpt/                # ✅ New name
    └── penilaian_jpt/
        ├── list.html
        ├── form.html
        ├── detail.html
        ├── delete.html
        ├── report.html
        └── partials/
            └── _table.html
```

### 2. Template Path Updates
Updated all template references in `views.py`:
- `survey_jpt/penilaian_jpt/` → `survey_hjpt/penilaian_jpt/`

### 3. Template Include Updates
Updated template includes within the templates:
- `survey_jpt/penilaian_jpt/partials/_table.html` → `survey_hjpt/penilaian_jpt/partials/_table.html`

## Operations Performed

### 1. Create New Folder
```bash
mkdir -p projects/survey_pemda_python/apps/survey/templates/survey_hjpt
```

### 2. Move All Contents
```bash
mv projects/survey_pemda_python/apps/survey/templates/survey_jpt/* \
   projects/survey_pemda_python/apps/survey/templates/survey_hjpt/
```

### 3. Remove Old Folder
```bash
rmdir projects/survey_pemda_python/apps/survey/templates/survey_jpt
```

### 4. Update Template References
```bash
sed -i 's|survey_jpt/penilaian_jpt/|survey_hjpt/penilaian_jpt/|g' \
    projects/survey_pemda_python/apps/survey/views.py
```

### 5. Update Template Includes
Updated include paths in `list.html` template.

## Files Affected

### Moved Files:
1. `survey_hjpt/penilaian_jpt/list.html` - Main listing page
2. `survey_hjpt/penilaian_jpt/form.html` - Create/edit form
3. `survey_hjpt/penilaian_jpt/detail.html` - Detail view with star ratings
4. `survey_hjpt/penilaian_jpt/delete.html` - Delete confirmation
5. `survey_hjpt/penilaian_jpt/report.html` - Analytics dashboard
6. `survey_hjpt/penilaian_jpt/partials/_table.html` - Table partial for HTMX

### Modified Files:
1. **views.py** - Updated all template paths from `survey_jpt/` to `survey_hjpt/`
2. **list.html** - Updated include path for table partial

## Verification

### ✅ Folder Structure
- Old folder `survey_jpt/` successfully removed
- New folder `survey_hjpt/` created with all contents
- All files properly moved with correct structure

### ✅ Template References
- All views.py template paths updated to `survey_hjpt/penilaian_jpt/`
- No remaining references to `survey_jpt` found
- Template includes updated correctly

### ✅ System Check
- Django system check passes with no issues
- No broken template references
- All functionality preserved

## Final Structure
```
apps/survey/templates/
├── master_survey/              # Master data templates
│   ├── jenis_survey/
│   ├── pertanyaan_survey/
│   ├── responden_survey/
│   ├── jawaban_survey/
│   └── periode_survey/
└── survey_hjpt/               # JPT survey templates
    └── penilaian_jpt/
        ├── list.html
        ├── form.html
        ├── detail.html
        ├── delete.html
        ├── report.html
        └── partials/
            └── _table.html
```

## Impact
- **No functional changes** - all features work exactly the same
- **Clean folder structure** - `survey_hjpt` name as requested
- **Consistent organization** - maintains separation between master data and JPT surveys
- **All references updated** - no broken links or missing templates

The Penilaian JPT system now uses the `survey_hjpt` folder structure as requested while maintaining full functionality.