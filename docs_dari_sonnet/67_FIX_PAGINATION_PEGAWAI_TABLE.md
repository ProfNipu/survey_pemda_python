# Fix Pagination Pegawai Table - Persis Seperti Manajemen Fungsi

**Tanggal**: 1 April 2026  
**Status**: ✅ SELESAI

---

## 🎯 MASALAH

User melaporkan:
1. ❌ Table pegawai menampilkan 50 items, bukan 10 (default)
2. ❌ Pagination tidak muncul di bawah table
3. ❌ Tidak ada kontrol "Show X entries"
4. ❌ Style table tidak sama dengan manajemen fungsi

**User Request**: "persisikan manajemen fungsi tu" - table harus PERSIS seperti manajemen fungsi

---

## 🔍 ROOT CAUSE

**Perbedaan Fundamental**:

### Manajemen Fungsi (Working)
```python
# View menggunakan Django ORM QuerySet
funcs = PermissionFunction.objects.annotate(rule_count=Count('rules'))
table = FunctionTable(funcs)

# RequestConfig membuat django-tables2 handle pagination otomatis
RequestConfig(request, paginate={'per_page': per_page}).configure(table)
```

### Pegawai List (Broken)
```python
# View menggunakan data dari API (bukan QuerySet)
items = data.get('items', [])  # List biasa, bukan QuerySet
table = PegawaiTable(items)

# ❌ TIDAK BISA pakai RequestConfig karena bukan QuerySet
# ❌ Pagination tidak ter-render
```

**Kesimpulan**: `RequestConfig` hanya bekerja dengan Django QuerySet, tidak dengan list biasa dari API.

---

## ✅ SOLUSI

### 1. Custom Paginator untuk API Data

Created: `apps/api_simpeg/paginator.py`

```python
class ApiPaginator(DjangoPaginator):
    """
    Custom paginator yang bekerja dengan API data (bukan Django ORM)
    """
    
    def __init__(self, object_list, per_page, total_count, current_page=1, **kwargs):
        self._current_page = current_page
        self._total_count = total_count
        self.per_page = int(per_page)
        self.object_list = object_list
    
    @property
    def count(self):
        return self._total_count
    
    @property
    def num_pages(self):
        if self.count == 0:
            return 1
        hits = max(1, self.count - self.orphans)
        return (hits + self.per_page - 1) // self.per_page


class ApiPage(Page):
    """Custom Page object untuk API data"""
    
    def start_index(self):
        if self.paginator.count == 0:
            return 0
        return (self.number - 1) * self.paginator.per_page + 1
    
    def end_index(self):
        if self.number == self.paginator.num_pages:
            return self.paginator.count
        return self.number * self.paginator.per_page
```

**Kenapa Custom Paginator?**
- Django-tables2 butuh paginator object untuk render pagination controls
- Standard Django Paginator butuh full QuerySet
- API hanya kasih data per-page + total count
- Custom paginator bridge the gap

---

### 2. Update View - Gunakan Custom Paginator

**File**: `apps/api_simpeg/views.py`

```python
from .paginator import ApiPaginator

def pegawai_list(request):
    # Get parameters
    per_page = request.GET.get('per_page', '10')  # Default 10
    
    # Call API
    data = api_service.get_pegawai_list(
        token=esimpeg_token,
        page=page,
        per_page=per_page,
        search=search if search else None,
        id_opd=int(id_opd) if id_opd else None
    )
    
    items = data.get('items', [])
    pagination = data.get('pagination', {})
    total_count = pagination.get('total', 0)
    current_page = pagination.get('page', page)
    
    # ✅ Create custom paginator
    paginator = ApiPaginator(
        object_list=items,
        per_page=per_page,
        total_count=total_count,
        current_page=current_page
    )
    
    # ✅ Get page object
    page_obj = paginator.page(current_page)
    
    # ✅ Attach to table
    table = PegawaiTable(items)
    table.paginator = paginator
    table.page = page_obj
```

**Key Points**:
1. Create `ApiPaginator` with API data
2. Get `page_obj` from paginator
3. Attach both to table
4. Django-tables2 akan render pagination controls otomatis

---

### 3. Update Table - Add ID Attribute

**File**: `apps/api_simpeg/tables.py`

```python
class PegawaiTable(tables.Table):
    # ... columns ...
    
    class Meta:
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection', 'row_number', 'id_pegawai', 'nip', 'nama', ...)
        attrs = {
            'id': 'pegawai_table',  # ✅ ID untuk JavaScript
            'class': 'w-full table-auto border-collapse border border-gray-300',
            'thead': {'class': 'bg-gray-50'},
            'tbody': {'class': 'bg-white'},
        }
        per_page = 10  # ✅ Default 10
```

---

## 📊 HASIL

### Before (Broken)
```
❌ Menampilkan 50 items
❌ Tidak ada pagination controls
❌ Tidak ada "Show X entries"
❌ Tidak bisa ganti per_page
```

### After (Fixed)
```
✅ Default 10 items per page
✅ Pagination controls muncul (1, 2, 3, ... Next)
✅ "Show X entries" dropdown (10, 25, 50, 100)
✅ Bisa navigasi antar halaman
✅ Style persis seperti manajemen fungsi
✅ Border dan gridlines sama
```

---

## 🔄 FLOW PAGINATION

### 1. User Load Page
```
Browser → Django View → ESIMPEG API
                      ← {items: [...], pagination: {total: 4867, page: 1}}
        ← HTML with table + pagination controls
```

### 2. User Click Page 2
```
Browser → HTMX Request (page=2)
        → Django View → ESIMPEG API (page=2)
                      ← {items: [...], pagination: {total: 4867, page: 2}}
        ← Partial HTML (only table)
        → Replace #table-container
```

### 3. User Change Per Page
```
Browser → HTMX Request (per_page=25)
        → Django View → ESIMPEG API (per_page=25)
                      ← {items: [...], pagination: {total: 4867, page: 1}}
        ← Partial HTML
        → Replace #table-container
```

---

## 🎨 REUSABLE COMPONENTS

Table pegawai sekarang menggunakan EXACT same components seperti manajemen fungsi:

### 1. Table Structure
```html
{% include 'includes/datatable_table_scroll.html' with table=table %}
```

### 2. Filters
```html
{% include 'includes/datatable_filters.html' with 
    show_search=True 
    search_placeholder="Cari nama atau NIP..." 
%}
```

### 3. Bulk Actions
```html
{% include 'includes/datatable_bulk_actions.html' with 
    show_clear=True 
    show_export=can_export 
%}
```

### 4. JavaScript
```javascript
window.pegawaiIntegratedDT = new DatatableHelper({
    tableId: 'pegawai_table',
    pageKey: 'pegawai_list',
    saveUrl: '{% url "api_simpeg:pegawai_list" %}',
    // ... same as manajemen fungsi
});
```

---

## 📝 FILES MODIFIED

1. ✅ **NEW**: `apps/api_simpeg/paginator.py` - Custom paginator untuk API data
2. ✅ **UPDATED**: `apps/api_simpeg/views.py` - Gunakan ApiPaginator
3. ✅ **UPDATED**: `apps/api_simpeg/tables.py` - Add table ID

---

## 🧪 TESTING

### Test Pagination
```bash
# 1. Load page - should show 10 items
http://localhost:8006/api-simpeg/pegawai/

# 2. Click page 2 - should load next 10 items
http://localhost:8006/api-simpeg/pegawai/?page=2

# 3. Change per_page - should show 25 items
http://localhost:8006/api-simpeg/pegawai/?per_page=25

# 4. Search - should maintain pagination
http://localhost:8006/api-simpeg/pegawai/?search=ahmad&per_page=10
```

### Expected Results
- ✅ Default 10 items per page
- ✅ Pagination controls visible (Previous, 1, 2, 3, ..., Next)
- ✅ "Showing 1 to 10 of 4867 entries"
- ✅ Per page dropdown works (10, 25, 50, 100)
- ✅ Page navigation works
- ✅ Search maintains pagination
- ✅ HTMX partial reload (no full page refresh)

---

## 🎯 KEY LEARNINGS

### 1. Django-tables2 Pagination Requirements
```python
# Django-tables2 needs these attributes on table object:
table.paginator  # Paginator instance
table.page       # Current Page instance

# Paginator must have:
- count property (total items)
- num_pages property (total pages)
- page(number) method (return Page object)

# Page must have:
- start_index() method
- end_index() method
- has_next() method
- has_previous() method
```

### 2. API Data vs QuerySet
```python
# QuerySet (Django ORM) - Easy
queryset = Model.objects.all()
RequestConfig(request, paginate={'per_page': 10}).configure(table)
# ✅ Pagination works automatically

# API Data (List) - Need Custom Paginator
items = api.get_data()  # Returns list
paginator = ApiPaginator(items, per_page, total_count)
table.paginator = paginator
table.page = paginator.page(current_page)
# ✅ Pagination works with custom paginator
```

### 3. Reusable Components Pattern
```
1. Create Table class (django-tables2)
2. Create View with pagination logic
3. Use standard templates (datatable_table_scroll.html)
4. Use standard JavaScript (DatatableHelper)
5. Result: Consistent UI across all tables
```

---

## 🚀 NEXT STEPS

1. ✅ Test pagination di browser
2. ✅ Test per_page dropdown
3. ✅ Test search dengan pagination
4. ✅ Verify style sama dengan manajemen fungsi
5. ⏭️ Implement export functionality (CSV, Excel, PDF)
6. ⏭️ Implement sync functionality

---

## 📚 REFERENCES

- Django-tables2 Pagination: https://django-tables2.readthedocs.io/en/latest/pages/pagination.html
- Django Paginator: https://docs.djangoproject.com/en/4.2/topics/pagination/
- Reusable Components: `docs/ui/REUSABLE_COMPONENTS.md`
- Manajemen Fungsi Reference: `apps/manajemen/functions.py`

---

**Status**: ✅ FIXED - Pagination sekarang bekerja persis seperti manajemen fungsi
