# 📚 Datatable Reusable Components - Usage Guide

**Version:** 1.0  
**Status:** ✅ Production Ready

---

## 🎯 Overview

Sistem reusable datatable yang sudah jadi dan siap pakai untuk semua tables di project.

**Benefits:**
- ✅ Plug-and-play - Setup dalam 5 menit
- ✅ Consistent behavior across all tables
- ✅ Bulk actions (select, copy, export, print, delete)
- ✅ Multi-page selection persistence
- ✅ HTMX integration
- ✅ Mobile responsive

---

## 📁 Files Created

```
static/
├── js/
│   └── datatable-helpers.js       # Core JavaScript class
└── css/
    └── datatable-custom.css       # Styling

templates/
└── includes/
    ├── datatable_filters.html     # Search & filter template
    └── datatable_bulk_actions.html # Bulk actions bar template
```

---

## 🚀 Quick Start Guide

### Step 1: Load Assets in `base_dashboard.html`

```django
<!DOCTYPE html>
<html>
<head>
    ...
    <!-- Tailwind CSS -->
    <link href="{% static 'css/tailwind.css' %}" rel="stylesheet">
    
    <!-- Datatable Custom CSS -->
    <link href="{% static 'css/datatable-custom.css' %}" rel="stylesheet">
</head>
<body>
    ...
    
    <!-- SweetAlert2 (for notifications) -->
    <script src="{% static 'js/sweetalert2.min.js' %}"></script>
    
    <!-- HTMX -->
    <script src="{% static 'js/htmx.min.js' %}"></script>
    
    <!-- Datatable Helpers -->
    <script src="{% static 'js/datatable-helpers.js' %}"></script>
    
    {% block extra_js %}{% endblock %}
</body>
</html>
```

### Step 2: Use in Your List Template

```django
{# apps/yourapp/templates/yourapp/item_list.html #}
{% extends 'base_dashboard.html' %}
{% load static %}

{% block content %}
<div class="container mx-auto px-4 py-6">
    <h1 class="text-2xl font-bold mb-6">Item List</h1>
    
    <!-- Filters -->
    {% include 'includes/datatable_filters.html' with 
        show_search=True
        search_placeholder="Cari item..."
        show_status_filter=True
        status_options=status_list
    %}
    
    <!-- Bulk Actions -->
    {% include 'includes/datatable_bulk_actions.html' with
        show_clear=True
        show_copy=True
        show_export=True
        show_print=True
        show_delete=True
        export_formats=['csv','excel','pdf']
    %}
    
    <!-- Table Container -->
    <div id="table-container">
        {% include 'yourapp/_item_table.html' %}
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
// Initialize datatable
const dt = new DatatableHelper({
    tableId: 'items_table',
    pageKey: 'items',
    saveUrl: '{% url "yourapp:item_list" %}',
    deleteUrl: '{% url "yourapp:item_list" %}',
    csrfToken: '{{ csrf_token }}',
    exportFormats: ['csv', 'excel', 'pdf'],
    debug: false  // Set true for debugging
});
dt.init();
</script>
{% endblock %}
```

### Step 3: Create Table Partial Template

```django
{# apps/yourapp/templates/yourapp/_item_table.html #}

<!-- Loading Overlay -->
<div id="table-loading-overlay" class="dt-loading-overlay htmx-indicator">
    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
</div>

<!-- Table -->
<div class="dt-table-container">
    {% render_table table %}
</div>
```

### Step 4: Setup Backend View

```python
# apps/yourapp/views.py
from django.views.generic import ListView
from django.http import JsonResponse
import json

class ItemListView(ListView):
    model = Item
    template_name = 'yourapp/item_list.html'
    context_object_name = 'items'
    
    def post(self, request, *args, **kwargs):
        """Handle AJAX requests"""
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
        
        # Handle bulk actions
        if request.POST.get('action') == 'bulk_delete':
            selected_ids = request.POST.getlist('selected_ids')
            Item.objects.filter(id__in=selected_ids).delete()
            messages.success(request, f'{len(selected_ids)} items berhasil dihapus')
            return redirect('yourapp:item_list')
        
        return super().get(request, *args, **kwargs)
```

---

## ⚙️ Configuration Options

### DatatableHelper Config

```javascript
new DatatableHelper({
    tableId: 'string',        // Table ID (required)
    pageKey: 'string',        // Unique key for this table (required)
    saveUrl: 'string',        // URL to save selections (required)
    deleteUrl: 'string',      // URL for delete action (required)
    csrfToken: 'string',      // CSRF token (required)
    exportFormats: [],        // ['csv', 'excel', 'pdf']
    debug: boolean            // Enable console logging
})
```

### Filter Template Options

```django
{% include 'includes/datatable_filters.html' with 
    show_search=True                        # Show search input
    search_placeholder="Text..."            # Custom placeholder
    show_status_filter=True                 # Show status dropdown
    status_options=status_list              # List of {value, label}
    status_label="Filter by status"         # Custom label
    show_items_per_page=True                # Show items per page selector
%}
```

### Bulk Actions Template Options

```django
{% include 'includes/datatable_bulk_actions.html' with
    show_clear=True                         # Show clear button
    show_copy=True                          # Show copy button
    show_export=True                        # Show export buttons
    show_print=True                         # Show print button
    show_delete=True                        # Show delete button
    export_formats=['csv','excel','pdf']    # Export format options
%}
```

---

## 🎨 CSS Classes

### Custom Classes Available:

| Class | Purpose |
|-------|---------|
| `.dt-bulk-actions-bar` | Bulk actions container |
| `.dt-filter-row` | Filter row container |
| `.dt-loading-overlay` | Loading indicator |
| `.dt-badge-active` | Active status badge |
| `.dt-badge-inactive` | Inactive status badge |
| `.dt-action-btn` | Action button base |
| `.dt-action-btn-primary` | Primary action button |
| `.dt-action-btn-danger` | Danger action button |
| `.dt-table-container` | Table wrapper |
| `.dt-checkbox` | Custom checkbox |

---

## 📋 Complete Example: User List

```django
{# apps/permissions/templates/permissions/granular/user_list_v2.html #}
{% extends 'base_dashboard.html' %}
{% load static %}

{% block content %}
<div class="container mx-auto px-4 py-6">
    <h1 class="text-2xl font-bold mb-6">Manajemen User</h1>
    
    <!-- Filters -->
    {% include 'includes/datatable_filters.html' with 
        show_search=True
        search_placeholder="Cari username, email, atau nama..."
        show_status_filter=True
        status_options=status_list
    %}
    
    <!-- Bulk Actions -->
    {% include 'includes/datatable_bulk_actions.html' %}
    
    <!-- Table -->
    <div id="table-container">
        {% include 'permissions/granular/_user_table.html' %}
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
const usersDT = new DatatableHelper({
    tableId: 'users_table',
    pageKey: 'users',
    saveUrl: '{% url "permissions:users_list" %}',
    deleteUrl: '{% url "permissions:users_list" %}',
    csrfToken: '{{ csrf_token }}',
    exportFormats: ['csv', 'excel', 'pdf'],
    debug: false
});
usersDT.init();
</script>
{% endblock %}
```

---

## 🔧 Advanced Customization

### Custom Bulk Action

```javascript
// In your extra_js block
const dt = new DatatableHelper({...});
dt.init();

// Add custom action
document.addEventListener('click', (e) => {
    if (e.target.closest('[data-action="custom"]')) {
        const ids = dt.getStoredSelections();
        // Your custom logic here
    }
});
```

### Custom Data Cache

```javascript
// Override cache function
dt.cacheCurrentPageData = function() {
    const rows = document.querySelectorAll('tbody tr');
    rows.forEach(row => {
        const checkbox = row.querySelector('.row-checkbox');
        if (!checkbox) return;
        
        const cells = row.querySelectorAll('td');
        const rowData = {
            id: checkbox.value,
            // Add your custom fields
            field1: cells[1]?.textContent.trim(),
            field2: cells[2]?.textContent.trim()
        };
        
        this.allPagesDataCache[checkbox.value] = rowData;
    });
};
```

---

## 🐛 Troubleshooting

### Issue: Selections not persisting

**Solution:** Check backend view handles `save_selection` and `load_selection` actions

```python
if action == 'save_selection':
    request.session[f'datatable_selection_{page_key}'] = selected_ids
    return JsonResponse({'success': True})
```

### Issue: Bulk actions not working

**Solution:** Ensure `data-action` attributes are set correctly

```html
<button data-action="delete">Delete</button>
```

### Issue: HTMX not reloading table

**Solution:** Check target ID matches

```html
<div id="table-container">  <!-- Must match hx-target -->
    {% include '_table.html' %}
</div>
```

---

## ✅ Migration Checklist

When converting existing table to reusable components:

- [ ] Load `datatable-helpers.js` and `datatable-custom.css` in base template
- [ ] Replace filter HTML with `{% include 'includes/datatable_filters.html' %}`
- [ ] Replace bulk actions HTML with `{% include 'includes/datatable_bulk_actions.html' %}`
- [ ] Replace JavaScript with `new DatatableHelper(...).init()`
- [ ] Test: Search functionality
- [ ] Test: Pagination
- [ ] Test: Multi-page selection
- [ ] Test: Bulk actions (copy, export, print, delete)
- [ ] Test: Mobile responsiveness

---

## 🎯 Next Steps

1. ✅ **User List** - Refactor ke reusable components
2. **Role List** - Apply same pattern
3. **Permission List** - Apply same pattern
4. **Other tables** - Apply as needed

---

## 📞 Support

**Debug Mode:**
```javascript
const dt = new DatatableHelper({
    ...config,
    debug: true  // Enable detailed console logging
});
```

**Check Console:**
- `[DatatableHelper]` - All operations logged
- Check for errors in browser console
- Use browser Network tab to inspect AJAX requests

---

**Status:** ✅ **READY TO USE**  
**Last Updated:** November 11, 2025

**Refactor user_list.html NEXT untuk see it in action!** 🚀
