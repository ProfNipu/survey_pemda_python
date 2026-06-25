# DataTable Filter Clear Utility

Utility JavaScript reusable untuk **auto-clear checkbox selections** ketika search box atau filter combo box berubah pada DataTable.

## 📋 Masalah yang Diselesaikan

Ketika user melakukan:
- ✅ Mark checkbox di DataTable (selections tersimpan)
- ✅ Lakukan search atau ubah filter
- ❌ Checkbox hilang secara visual TAPI tetap terhitung di bulk actions
- ❌ Saat paging berubah, checkbox muncul lagi

**Solusi:** Auto-clear selections ketika search/filter berubah, tapi TIDAK saat pagination berubah.

---

## 🚀 Quick Start

### 1. Include Script

```django
{% block extra_js %}
{% load static %}
<script src="{% static 'js/datatable-filter-clear.js' %}"></script>
<script>
  // Your DataTable code here...
</script>
{% endblock %}
```

### 2. Setup Handler

Panggil `setupFilterClearHandlers()` setelah inisialisasi DataTable variables:

```javascript
// Setup variabel DataTable terlebih dahulu
const PAGE_KEY = 'your_page_key';
let currentSelections = [];
let allPagesDataCache = {};

// ... functions saveSelectionsToDB, getStoredSelections, dll ...

// PANGGIL setupFilterClearHandlers
setupFilterClearHandlers({
    searchInputId: 'search-input',        // ID search input
    filterIds: ['status-filter'],         // Array IDs filter elements
    clearCallback: function() {
        // Clear logic spesifik untuk page ini
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
| `searchInputId` | `string` | ID dari search input element |
| `filterIds` | `Array<string>` | Array berisi ID dari filter elements (combo box, select, dll) |
| `clearCallback` | `Function` | Callback function yang dipanggil saat clearing selections |

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `hideBulkBar` | `boolean` | `true` | Auto-hide bulk actions bar |
| `bulkBarId` | `string` | `'bulk-actions-bar'` | ID bulk actions bar element |
| `countSpanId` | `string` | `'selected-count'` | ID selected count span |
| `selectAllTopId` | `string` | `'select-all-top'` | ID select-all checkbox (top) |
| `selectAllBottomId` | `string` | `'select-all-bottom'` | ID select-all checkbox (bottom) |
| `rowCheckboxClass` | `string` | `'.row-checkbox'` | CSS class untuk row checkboxes |

---

## 💡 Examples

### Example 1: Basic Usage (User List)

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

### Example 2: Multiple Filters (Advanced)

```javascript
setupFilterClearHandlers({
    searchInputId: 'search-input',
    filterIds: ['status-filter', 'category-filter', 'department-filter'],
    clearCallback: function() {
        currentSelections = [];
        saveSelectionsToDB([]);
        allPagesDataCache = {};
        console.log('[Custom] Cleared all selections');
    }
});
```

### Example 3: Custom Element IDs

```javascript
setupFilterClearHandlers({
    searchInputId: 'main-search',
    filterIds: ['filter-status', 'filter-role'],
    bulkBarId: 'my-bulk-bar',
    countSpanId: 'my-count',
    selectAllTopId: 'select-all-header',
    selectAllBottomId: 'select-all-footer',
    rowCheckboxClass: '.item-checkbox',
    clearCallback: function() {
        // Custom clear logic
        myCustomClearFunction();
    }
});
```

---

## 🎯 Behavior

### ✅ Clear Selections Terjadi Ketika:
- User mengetik di search box
- User mengubah filter combo box/select
- User mengklik tombol "Clear Search"

### ❌ TIDAK Clear Selections Ketika:
- User berpindah halaman (pagination)
- User mengklik refresh tanpa filter berubah
- User melakukan sort column

---

## 🔍 Debugging

Utility ini menggunakan console logging dengan prefix `[Filter Clear]`:

```javascript
console.log('[Filter Clear] Setting up handlers...');
console.log('[Filter Clear] Attached handler to: search-input');
console.log('[Filter Clear] Search changed, clearing selections');
```

Enable console untuk debugging:
```javascript
// Di browser console
localStorage.debug = 'filter-clear';
```

---

## 📦 Files Implemented

1. ✅ `user_list.html` - User management page
2. ✅ `role_list.html` - Role management page
3. 📝 **Your template here** - Copy pattern dari files di atas

---

## 🛠️ Troubleshooting

### Problem: Handler tidak jalan

**Check:**
1. Script sudah di-include?
   ```django
   <script src="{% static 'js/datatable-filter-clear.js' %}"></script>
   ```

2. Element IDs benar?
   ```javascript
   console.log(document.getElementById('search-input')); // Harus ada
   ```

3. setupFilterClearHandlers dipanggil setelah DOM ready?
   ```javascript
   // Jangan panggil sebelum variables dideklarasi
   ```

### Problem: Selections tidak ter-clear

**Check clearCallback:**
```javascript
clearCallback: function() {
    console.log('[DEBUG] Clear callback called');
    // Pastikan logic clear ada di sini
    currentSelections = [];
    saveSelectionsToDB([]);
}
```

---

## 📝 Notes

- Utility ini menggunakan **HTMX `htmx:beforeRequest` event**
- Handler hanya attach sekali (prevent duplicates)
- Compatible dengan HTMX-powered DataTables
- Tidak mempengaruhi pagination behavior

---

## 🤝 Contributing

Jika ada bug atau improvement, edit file:
- `/static/js/datatable-filter-clear.js`

Test di minimal 2 pages:
1. User List (`user_list.html`)
2. Role List (`role_list.html`)

---

## 📄 License

Internal project utility - ESIMPEG-Python
