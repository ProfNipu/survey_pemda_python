# 📊 DataTable Filter Clear - Reusable Implementation Summary

## 🎯 Problem Solved

**Masalah:**
- User mencentang checkbox di DataTable (selections tersimpan di database)
- User melakukan search atau filter
- Checkbox hilang dari tampilan tapi tetap terhitung di bulk actions
- Saat paging berubah, checkbox yang sudah di-clear muncul lagi

**Solusi:**
- Auto-clear selections ketika **search box** atau **filter combo box** berubah
- Selections tetap **PERSIST** saat **pagination** (tidak di-clear)
- Implementasi **REUSABLE** untuk semua DataTable pages

---

## 📦 Files Created

### 1. **Reusable Utility Script**
```
/static/js/datatable-filter-clear.js
```
- Core utility untuk filter clear functionality
- Setup sekali, pakai di banyak pages
- Configurable via options object

### 2. **Documentation**
```
/static/js/README-DATATABLE-FILTER-CLEAR.md
```
- Complete usage guide
- Configuration options
- Examples & troubleshooting

### 3. **Template Example**
```
/static/js/TEMPLATE-EXAMPLE.html
```
- Ready-to-use template
- Copy-paste untuk page baru
- Sudah include semua setup

---

## ✅ Implemented Pages

### 1. User List (`user_list.html`)
**Location:** `/apps/permissions/templates/permissions/granular/user_list.html`

**Changes:**
```django
{% load static %}
<script src="{% static 'js/datatable-filter-clear.js' %}"></script>
<script>
  setupFilterClearHandlers({
      searchInputId: 'search-input',
      filterIds: ['status-filter'],
      clearCallback: function() {
          currentSelections = [];
          saveSelectionsToDB([]);
          allPagesDataCache = {};
      }
  });
</script>
```

### 2. Role List (`role_list.html`)
**Location:** `/apps/permissions/templates/permissions/granular/role_list.html`

**Changes:**
```django
{% load static %}
<script src="{% static 'js/datatable-filter-clear.js' %}"></script>
<script>
  setupFilterClearHandlers({
      searchInputId: 'search-input',
      filterIds: ['status-filter'],
      clearCallback: function() {
          currentSelections = [];
          saveSelectionsToDB([]);
          allPagesDataCache = {};
      }
  });
</script>
```

---

## 🚀 How to Use on New Pages

### Step 1: Include Script
```django
{% block extra_js %}
{% load static %}
<script src="{% static 'js/datatable-filter-clear.js' %}"></script>
<script>
  // Your page script here
</script>
{% endblock %}
```

### Step 2: Setup Variables
```javascript
const PAGE_KEY = 'your_unique_page_key';
let currentSelections = [];
let allPagesDataCache = {};
```

### Step 3: Call setupFilterClearHandlers
```javascript
setupFilterClearHandlers({
    searchInputId: 'search-input',
    filterIds: ['status-filter', 'category-filter'], // Add all filter IDs
    clearCallback: function() {
        currentSelections = [];
        saveSelectionsToDB([]);
        allPagesDataCache = {};
    }
});
```

---

## ⚙️ Configuration Options

### Required Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `searchInputId` | String | ID of search input element |
| `filterIds` | Array | Array of filter element IDs |
| `clearCallback` | Function | Function to call when clearing |

### Optional Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `hideBulkBar` | Boolean | `true` | Hide bulk actions bar |
| `bulkBarId` | String | `'bulk-actions-bar'` | Bulk bar element ID |
| `countSpanId` | String | `'selected-count'` | Count span ID |
| `selectAllTopId` | String | `'select-all-top'` | Top select-all ID |
| `selectAllBottomId` | String | `'select-all-bottom'` | Bottom select-all ID |
| `rowCheckboxClass` | String | `'.row-checkbox'` | Row checkbox class |

---

## 🎬 Behavior

### ✅ Clear Terjadi Ketika:
- User ketik di search box
- User ubah combo box filter (status, category, dll)
- User klik tombol "Clear Search"

### ❌ TIDAK Clear Ketika:
- User pindah halaman (pagination)
- User refresh page tanpa filter berubah
- User sort column

---

## 📝 Example Implementations

### Basic (1 Filter)
```javascript
setupFilterClearHandlers({
    searchInputId: 'search-input',
    filterIds: ['status-filter'],
    clearCallback: function() {
        currentSelections = [];
        saveSelectionsToDB([]);
        allPagesDataCache = {};
    }
});
```

### Advanced (Multiple Filters)
```javascript
setupFilterClearHandlers({
    searchInputId: 'main-search-box',
    filterIds: [
        'status-filter',
        'category-filter',
        'department-filter',
        'year-filter'
    ],
    clearCallback: function() {
        // Custom clear logic
        currentSelections = [];
        saveSelectionsToDB([]);
        allPagesDataCache = {};
        
        // Additional custom logic
        console.log('[Custom] Selections cleared');
        updateCustomUI();
    }
});
```

### Custom Element IDs
```javascript
setupFilterClearHandlers({
    searchInputId: 'my-search',
    filterIds: ['my-filter-1', 'my-filter-2'],
    bulkBarId: 'my-bulk-actions',
    countSpanId: 'my-counter',
    selectAllTopId: 'select-all-header',
    selectAllBottomId: 'select-all-footer',
    rowCheckboxClass: '.my-checkbox',
    clearCallback: function() {
        myCustomClearFunction();
    }
});
```

---

## 🔍 Testing Checklist

Untuk memastikan implementation bekerja dengan benar:

### ✅ Test Cases:
1. **Search Clear Test**
   - [ ] Centang beberapa checkbox
   - [ ] Ketik di search box
   - [ ] Verify: Selections ter-clear, bulk bar hide, count = 0

2. **Filter Clear Test**
   - [ ] Centang beberapa checkbox
   - [ ] Ubah combo box filter
   - [ ] Verify: Selections ter-clear, bulk bar hide, count = 0

3. **Pagination Persist Test**
   - [ ] Centang beberapa checkbox di halaman 1
   - [ ] Pindah ke halaman 2
   - [ ] Verify: Selections TETAP ada, count tidak berubah
   - [ ] Kembali ke halaman 1
   - [ ] Verify: Checkbox tetap tercentang

4. **Clear Search Button Test**
   - [ ] Centang beberapa checkbox
   - [ ] Klik tombol Clear (X)
   - [ ] Verify: Selections ter-clear

5. **Multiple Operations Test**
   - [ ] Centang checkbox di halaman 1 & 2
   - [ ] Lakukan search
   - [ ] Verify: All selections ter-clear
   - [ ] Centang lagi
   - [ ] Pindah page
   - [ ] Verify: Selections persist

---

## 🐛 Troubleshooting

### Problem: Script tidak jalan

**Solution:**
1. Check console untuk error
2. Pastikan script di-include sebelum setupFilterClearHandlers dipanggil
3. Verify element IDs benar

### Problem: Selections tidak clear

**Solution:**
1. Check clearCallback dipanggil:
   ```javascript
   clearCallback: function() {
       console.log('[DEBUG] Callback called'); // Add this
       currentSelections = [];
       saveSelectionsToDB([]);
   }
   ```

2. Check HTMX attributes di search/filter elements:
   ```html
   hx-get="{% url 'your:list_url' %}"
   hx-trigger="keyup changed delay:500ms"  <!-- or "change" for select -->
   ```

### Problem: Duplicate handler attached

**Solution:**
Utility sudah handle ini otomatis dengan flag `_filterClearHandler_*`. 
Jika tetap terjadi, check:
```javascript
// Reset flag manually (for development)
delete window._filterClearHandler_search-input;
```

---

## 📊 Performance Notes

- Handler attach sekali per page load (no duplicates)
- Debounced save (500ms) untuk mengurangi database calls
- Efficient DOM manipulation (clone & replace vs re-query)
- Minimal console logging di production

---

## 🔄 Migration Guide

### Dari Manual Implementation ke Reusable Utility

**Before:**
```javascript
// Manual implementation (50+ lines)
if (!window.searchFilterClearHandlerAttached) {
    const searchInput = document.getElementById('search-input');
    const statusFilter = document.getElementById('status-filter');
    
    function clearSelectionsOnFilterChange() {
        currentSelections = [];
        saveSelectionsToDB([]);
        allPagesDataCache = {};
        // ... more code
    }
    
    if (searchInput) {
        searchInput.addEventListener('htmx:beforeRequest', clearSelectionsOnFilterChange);
    }
    // ... more code
}
```

**After:**
```javascript
// Reusable utility (5 lines)
setupFilterClearHandlers({
    searchInputId: 'search-input',
    filterIds: ['status-filter'],
    clearCallback: function() {
        currentSelections = [];
        saveSelectionsToDB([]);
        allPagesDataCache = {};
    }
});
```

---

## 📚 Additional Resources

- **Full Documentation:** `/static/js/README-DATATABLE-FILTER-CLEAR.md`
- **Template Example:** `/static/js/TEMPLATE-EXAMPLE.html`
- **Implementation Examples:**
  - User List: `/apps/permissions/templates/permissions/granular/user_list.html`
  - Role List: `/apps/permissions/templates/permissions/granular/role_list.html`

---

## 🎉 Benefits

✅ **Reusable** - Setup sekali, pakai di semua pages
✅ **Configurable** - Flexible options untuk berbagai use cases
✅ **Maintainable** - Single source of truth untuk logic
✅ **Testable** - Consistent behavior across pages
✅ **Documented** - Complete guide & examples
✅ **Production Ready** - Error handling & debugging built-in

---

## 👥 Team Usage

### Untuk Developer Baru:
1. Baca `/static/js/README-DATATABLE-FILTER-CLEAR.md`
2. Copy template dari `/static/js/TEMPLATE-EXAMPLE.html`
3. Adjust configuration sesuai kebutuhan page
4. Test menggunakan checklist di atas

### Untuk Maintenance:
1. Edit logic di `/static/js/datatable-filter-clear.js`
2. Test di minimal 2 pages (user_list & role_list)
3. Update documentation jika ada perubahan API

---

## 📅 Version History

**v1.0 (Nov 14, 2025)**
- ✅ Initial reusable implementation
- ✅ Implemented in user_list.html
- ✅ Implemented in role_list.html
- ✅ Complete documentation
- ✅ Template example created

---

**Status: ✅ PRODUCTION READY**

Silakan gunakan utility ini untuk semua DataTable pages yang membutuhkan filter clear functionality.
