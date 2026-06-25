# 🚀 Implementasi Datatable Reusable - Panduan Cepat

**Status:** ✅ PRODUCTION READY  
**Updated:** November 14, 2025

## 📋 Overview

Panduan cepat untuk mengimplementasikan tabel baru menggunakan sistem reusable datatable yang sudah ada. Sistem ini mengurangi **95% kode** dibandingkan implementasi manual dan menjamin konsistensi UX di seluruh aplikasi.

## 🎯 Keuntungan

- ✅ **3-5 menit** setup untuk tabel baru (vs 1-2 jam manual)
- ✅ **~10 baris** JS (vs 500+ baris sebelumnya)
- ✅ Feature lengkap: search, filter, bulk actions, export
- ✅ Consistent UX di semua tabel
- ✅ Central maintenance (bug fix sekali = fix semua tabel)

---

## 📊 Panduan Step-by-Step

### Step 1: Buat Template Utama

```django
{% extends 'base_dashboard.html' %}
{% load render_table from django_tables2 %}

{% block page_title %}Judul Halaman{% endblock %}

{% block content %}
{# ===== HEADER ===== #}
<div class="flex justify-between items-center mb-8">
    <div>
        <h2 class="text-2xl font-semibold text-gray-800 mb-2">
            <i class="fas fa-users mr-2"></i> Manajemen Items
        </h2>
        <p class="text-gray-500">Kelola data dengan mudah</p>
    </div>
    <div>
        <a href="{% url 'app:create' %}" class="bg-green-500 hover:bg-green-600 text-white font-medium py-2 px-4 rounded-lg transition-colors">
            <i class="fas fa-plus mr-2"></i> Tambah Baru
        </a>
    </div>
</div>

<div class="bg-white rounded-xl p-6 shadow-lg">
    {# ===== 1. FILTERS REUSABLE ===== #}
    {% include 'includes/datatable_filters.html' with 
        show_search=True
        search_placeholder="Cari berdasarkan nama..."
        show_status_filter=True
        status_options=status_list
    %}
    
    {# ===== 2. BULK ACTIONS REUSABLE ===== #}
    {% include 'includes/datatable_bulk_actions.html' with
        show_clear=True
        show_copy=True
        show_export=True
        show_print=True
        show_delete=True
        export_formats=['csv','excel','pdf']
    %}
    
    {# ===== 3. TABLE CONTAINER ===== #}
    <div id="table-container">
        {% include 'app/_item_table.html' %}
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
// ===== 4. INITIALIZE DATATABLE (8 LINES ONLY!) =====
document.addEventListener('DOMContentLoaded', function() {
    const dt = new DatatableHelper({
        tableId: 'items_table',             // Table ID in HTML
        pageKey: 'item_list',               // Unique key untuk storage
        saveUrl: '{% url "app:list" %}',    // Endpoint untuk save selections
        deleteUrl: '{% url "app:list" %}',  // Endpoint untuk bulk delete
        exportFormats: ['csv', 'excel', 'pdf'],
        debug: false                         // Set true untuk debugging
    });
    dt.init();
});
</script>
{% endblock %}
```

### Step 2: Buat Partial Table Template

```django
{# File: app/_item_table.html #}

{# ===== GUNAKAN REUSABLE COMPONENT ===== #}
{% include 'includes/datatable_content.html' with 
    entity_name="Items"
    total=total
    active_count=active_count
    search_query=search_query
    table=table
%}
```

### Step 3: Set Up View

```python
# views.py
from django_tables2 import SingleTableView
from .models import Item
from .tables import ItemTable

class ItemListView(SingleTableView):
    model = Item
    table_class = ItemTable
    template_name = 'app/item_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add extra context
        items = self.get_queryset()
        context['total'] = items.count()
        context['active_count'] = items.filter(is_active=True).count()
        context['search_query'] = self.request.GET.get('search', '')
        
        # Status options for filter (optional)
        context['status_list'] = [
            {'value': 'all', 'label': 'Semua Status'},
            {'value': 'active', 'label': 'Aktif'},
            {'value': 'inactive', 'label': 'Non-aktif'},
        ]
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle AJAX and bulk actions"""
        # Handle selections save/load
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                data = json.loads(request.body)
                action = data.get('action')
                
                # Save selection
                if action == 'save_selection':
                    page_key = data.get('page_key')
                    selected_ids = data.get('selected_ids', [])
                    request.session[f'datatable_selection_{page_key}'] = selected_ids
                    return JsonResponse({'success': True})
                
                # Load selection
                elif action == 'load_selection':
                    page_key = data.get('page_key')
                    selected_ids = request.session.get(f'datatable_selection_{page_key}', [])
                    return JsonResponse({'success': True, 'selected_ids': selected_ids})
                    
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
        
        # Handle bulk delete
        if request.POST.get('action') == 'bulk_delete':
            selected_ids = request.POST.getlist('selected_ids')
            if selected_ids:
                Item.objects.filter(id__in=selected_ids).delete()
                messages.success(request, f'{len(selected_ids)} item berhasil dihapus!')
        
        return self.get(request, *args, **kwargs)
```

### Step 4: Define Table Class

```python
# tables.py
import django_tables2 as tables
from .models import Item

class ItemTable(tables.Table):
    selection = tables.CheckBoxColumn(
        accessor='pk',
        attrs={
            'th__input': {'class': 'dt-checkbox-header'},
            'td__input': {'class': 'dt-checkbox row-checkbox'},
        },
        orderable=False,
        exclude_from_export=True
    )
    
    actions = tables.TemplateColumn(
        template_name='app/item_actions.html',
        orderable=False,
        exclude_from_export=True,
        verbose_name='Aksi'
    )
    
    name = tables.Column(verbose_name='Nama')
    status = tables.Column(verbose_name='Status')
    
    class Meta:
        model = Item
        template_name = 'django_tables2/tailwind.html'  # Tailwind CSS version
        fields = ('selection', 'id', 'name', 'status', 'actions')
        attrs = {
            'class': 'min-w-full divide-y divide-gray-200',
            'id': 'items_table'  # HARUS SAMA dengan tableId di DatatableHelper
        }
```

### Step 5: Buat Template untuk Actions Column

```django
{# File: app/item_actions.html #}
<div class="flex space-x-1">
    <a href="{% url 'app:detail' record.id %}" class="text-blue-600 hover:text-blue-800" title="Detail">
        <i class="fas fa-eye"></i>
    </a>
    <a href="{% url 'app:edit' record.id %}" class="text-green-600 hover:text-green-800" title="Edit">
        <i class="fas fa-edit"></i>
    </a>
    <a href="{% url 'app:delete' record.id %}" class="text-red-600 hover:text-red-800" title="Delete">
        <i class="fas fa-trash"></i>
    </a>
</div>
```

---

## 🛠️ Fitur DatatableHelper

Semua fitur ini **otomatis tersedia** tanpa menulis kode tambahan:

| Fitur | Deskripsi |
|-------|-----------|
| **Checkbox Selection** | Pilih satu/multiple items |
| **Cross-page Selection** | Pilihan tetap tersimpan saat ganti halaman |
| **Search** | Pencarian debounced (500ms) |
| **Status Filter** | Filter by status |
| **Bulk Actions** | Clear, Copy, Export (CSV, Excel, PDF), Print, Delete |
| **SweetAlert** | Konfirmasi delete dengan SweetAlert |
| **HTMX Integration** | Partial updates untuk filter & pagination |
| **Toast Notifications** | Notifikasi success/error |
| **Loading Indicators** | Smooth loading animation |
| **Export Estimation** | Estimasi waktu export berdasarkan jumlah records |

---

## 📝 Opsi Konfigurasi DatatableHelper

```javascript
const dt = new DatatableHelper({
    // REQUIRED OPTIONS
    tableId: 'items_table',            // ID dari table element
    pageKey: 'item_list',              // Key untuk menyimpan selections di session
    saveUrl: '{% url "app:list" %}',   // URL untuk AJAX save selections
    
    // OPTIONAL SETTINGS
    deleteUrl: '{% url "app:list" %}', // URL untuk bulk delete (jika berbeda)
    csrfToken: '{{ csrf_token }}',     // Auto-detected if not provided
    
    // FEATURE FLAGS (default: true)
    enableSelection: true,             // Enable checkboxes & selection
    enableBulkActions: true,           // Show bulk actions bar
    enableExport: true,                // Enable export functionality
    
    // EXPORT OPTIONS
    exportFormats: ['csv', 'excel', 'pdf'], // Available export formats
    
    // TIMING CONFIG (per record in seconds)
    timing: {
        bulkExport: 0.1,               // 100ms per record (bulk)
        excelExport: 0.000175,         // 0.175ms per record (excel)
        pdfExport: 0.00115             // 1.15ms per record (pdf)
    },
    
    // DEBUGGING
    debug: false                       // Enable console logging
});
```

---

## 💡 Tips Implementasi

1. **Table ID Harus Sama**
   - `id="items_table"` di Django Table harus sama dengan `tableId: 'items_table'`

2. **URL Mapping**
   - Pastikan view dapat handle AJAX POST untuk save/load selections

3. **Bulk Delete**
   - Perlu handle `action=bulk_delete` di view POST method

4. **Column Selection**
   - Selalu tambahkan `CheckBoxColumn` sebagai kolom pertama

5. **CSRF Token**
   - Auto-detected, tapi bisa juga diberikan langsung: `csrfToken: '{{ csrf_token }}'`

---

## 🔍 Debugging & Troubleshooting

```javascript
// Enable debug mode untuk melihat log di console
const dt = new DatatableHelper({
    tableId: 'items_table',
    pageKey: 'item_list',
    saveUrl: '{% url "app:list" %}',
    debug: true  // Enable debugging
});
```

### Common Issues:

1. **Selections Not Persisting**
   - Check `pageKey` unique dan sama dengan yang digunakan di backend

2. **Bulk Actions Not Showing**
   - Pastikan `CheckBoxColumn` ada di table definition
   - Pastikan `datatable_bulk_actions.html` di-include

3. **Export Not Working**
   - Verify URL di `saveUrl` bisa menerima POST requests
   - Check browser console untuk errors

---

## 🏆 Conclusion

Dengan mengikuti guide ini, implementasi tabel baru hanya membutuhkan waktu 3-5 menit dengan fitur yang lengkap. Pendekatan reusable ini menjamin konsistensi UX dan mempercepat development secara signifikan.

**Happy coding! 🚀**
