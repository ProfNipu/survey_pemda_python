# 🚀 Quick Reference - DataTable Filter Clear

## 📋 Copy-Paste Setup (5 Minutes)

### 1. Include Script (Add to template)
```django
{% block extra_js %}
{% load static %}
<script src="{% static 'js/datatable-filter-clear.js' %}"></script>
```

### 2. Add Setup Code (Add after your DataTable init)
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

### 3. Done! ✅

---

## 🎯 Common Use Cases

### Single Filter
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

### Multiple Filters
```javascript
setupFilterClearHandlers({
    searchInputId: 'search-input',
    filterIds: ['status-filter', 'category-filter', 'year-filter'],
    clearCallback: function() {
        currentSelections = [];
        saveSelectionsToDB([]);
        allPagesDataCache = {};
    }
});
```

### No Search Box (Only Filters)
```javascript
setupFilterClearHandlers({
    searchInputId: null, // or omit this line
    filterIds: ['status-filter', 'type-filter'],
    clearCallback: function() {
        currentSelections = [];
        saveSelectionsToDB([]);
        allPagesDataCache = {};
    }
});
```

---

## 🔧 Configuration Quick Reference

| Parameter | Type | Required | Default | Example |
|-----------|------|----------|---------|---------|
| `searchInputId` | String | Yes | - | `'search-input'` |
| `filterIds` | Array | Yes | - | `['status-filter']` |
| `clearCallback` | Function | Yes | - | See examples above |
| `bulkBarId` | String | No | `'bulk-actions-bar'` | `'my-bulk-bar'` |
| `countSpanId` | String | No | `'selected-count'` | `'my-count'` |
| `hideBulkBar` | Boolean | No | `true` | `false` |

---

## ✅ What Gets Cleared?

When user searches or filters:
- ✅ Checkbox selections
- ✅ Stored selections in database
- ✅ Cached page data
- ✅ Bulk actions bar (hidden)
- ✅ Selection count (reset to 0)

When user navigates pages:
- ❌ Nothing cleared (selections persist!)

---

## 🐛 Quick Troubleshooting

### Not Working?
```javascript
// Check console
console.log(document.getElementById('search-input')); // Must exist
console.log(document.getElementById('status-filter')); // Must exist

// Check script loaded
console.log(typeof setupFilterClearHandlers); // Should be 'function'
```

### Selections Not Clearing?
```javascript
// Add debug log
clearCallback: function() {
    console.log('[DEBUG] Clear callback called');
    currentSelections = [];
    saveSelectionsToDB([]);
    allPagesDataCache = {};
}
```

---

## 📱 Contact & Support

- **Full Docs:** `/static/js/README-DATATABLE-FILTER-CLEAR.md`
- **Template:** `/static/js/TEMPLATE-EXAMPLE.html`
- **Examples:** `user_list.html`, `role_list.html`

---

## 💡 Pro Tips

1. **Always test with:**
   - Search box typing
   - Filter dropdown change
   - Pagination (should NOT clear)

2. **Element IDs must match:**
   ```html
   <!-- HTML -->
   <input id="search-input" ...>
   <select id="status-filter" ...>
   
   <!-- JavaScript -->
   searchInputId: 'search-input',  // Match!
   filterIds: ['status-filter'],   // Match!
   ```

3. **Add all filters:**
   If you have multiple filters, add them ALL:
   ```javascript
   filterIds: ['status-filter', 'category-filter', 'department-filter']
   ```

---

**Need help?** Check `/static/js/README-DATATABLE-FILTER-CLEAR.md` untuk complete guide.
