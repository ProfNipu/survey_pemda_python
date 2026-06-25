# Reusable Datatable Implementation Playbook

Panduan singkat dari awal–akhir untuk mengintegrasikan sistem datatable reusable ke halaman baru (mis. Controls, Modules, dsb).

## Prasyarat
- Base template sudah memuat:
  - `static/css/tailwind.css`
  - `static/js/htmx.min.js`
  - `static/js/datatable-helpers.js`
- Komponen reusable:
  - `templates/includes/datatable_filters.html`
  - `templates/includes/datatable_bulk_actions.html`
  - `templates/includes/datatable_loading.html`
  - `templates/django_tables2/tailwind.html`

## Langkah Backend (Views, Tables, URLs)
### 1) Table class (django-tables2)
Buat `XTable` di `apps/permissions/tables.py`.

- Kolom wajib: `selection` (CheckBoxColumn), `row_number` (No), kolom inti entity, kolom hitungan (mis. `rule_count`), `actions`.
- Atur `attrs` dan `fields` sesuai urutan final kolom.

Contoh skeleton:
```python
class XTable(tables.Table):
    selection = tables.CheckBoxColumn(accessor='pk', orderable=False, attrs={...})
    row_number = tables.Column(empty_values=(), verbose_name='No', orderable=False, attrs={...})
    # kolom inti...
    actions = tables.Column(empty_values=(), orderable=False, attrs={...})

    class Meta:
        model = ModelX
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection','row_number','id','field_a','field_b','count_field','actions')
        attrs = { 'class': 'w-full table-fixed border-collapse border border-gray-300', ... }

    def render_row_number(self, record, table):
        page_number = getattr(table.page, 'number', 1)
        per_page = getattr(table.paginator, 'per_page', 10)
        if not hasattr(self, '_row_counter'):
            self._row_counter = (page_number - 1) * per_page
        self._row_counter += 1
        return self._row_counter

    def render_actions(self, record):
        # return tombol edit/delete sesuai kebutuhan
        ...
```

### 2) List view (HTMX + persistence)
Tambahkan `@ensure_csrf_cookie` dan pola berikut:

- `POST export_all` → export CSV/Excel/PDF untuk seluruh data terfilter.
- `POST XHR JSON` → `save_selection` / `load_selection` via `UserTableSelection`.
- `POST action` (bulk) → `export_csv|export_excel|export_pdf` dan `bulk_delete`.
- `GET` → filter `search`, anotasi hitungan (mis. `rule_count`), buat `XTable`, `RequestConfig` (pagination).
- Jika HTMX, render partial `_<entity>_table.html`; jika tidak, render full `<entity>_list.html`.

Skeleton ringkas:
```python
@ensure_csrf_cookie
@staff_member_required
def x_list(request):
    # ---- EXPORT ALL ----
    if request.method == 'POST' and 'export_all' in request.POST:
        search_query = request.POST.get('search','').strip()
        qs = ModelX.objects.annotate(count_field=Count('...'))
        if search_query:
            qs = qs.filter(Q(field_a__icontains=search_query) | Q(field_b__icontains=search_query))
        qs = qs.order_by('field_a')
        if request.POST['export_all'] == 'excel':
            return export_x_excel(qs)
        elif request.POST['export_all'] == 'pdf':
            return export_x_pdf(qs)

    # ---- AJAX SAVE/LOAD SELECTION ----
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = json.loads(request.body)
        if data.get('action') == 'save_selection':
            UserTableSelection.objects.update_or_create(
                user=request.user, page_key=data.get('page_key','x_list'),
                defaults={'selected_ids': data.get('selected_ids', [])}
            )
            return JsonResponse({'success': True})
        if data.get('action') == 'load_selection':
            try:
                sel = UserTableSelection.objects.get(user=request.user, page_key=data.get('page_key','x_list'))
                return JsonResponse({'success': True, 'selected_ids': sel.selected_ids})
            except UserTableSelection.DoesNotExist:
                return JsonResponse({'success': True, 'selected_ids': []})

    # ---- BULK ACTIONS ----
    if request.method == 'POST' and 'action' in request.POST:
        action = request.POST['action']
        ids = request.POST.getlist('selected_ids')
        qs = ModelX.objects.filter(id__in=ids).annotate(count_field=Count('...'))
        if action == 'export_csv': return export_x_csv(qs)
        if action == 'export_excel': return export_x_excel(qs)
        if action == 'export_pdf': return export_x_pdf(qs)
        if action == 'bulk_delete':
            qs.delete()
            UserTableSelection.objects.filter(user=request.user, page_key='x_list').delete()
            messages.success(request, f"{len(ids)} item dihapus")
            return redirect('permissions:x_list')

    # ---- REGULAR GET ----
    qs = ModelX.objects.annotate(count_field=Count('...'))
    search = request.GET.get('search','').strip()
    if search:
        qs = qs.filter(Q(field_a__icontains=search)|Q(field_b__icontains=search))
    qs = qs.order_by('field_a')

    table = XTable(qs)
    per_page = int(request.GET.get('per_page','10') or 10)
    RequestConfig(request, paginate={'per_page': per_page}).configure(table)

    ctx = {'table': table,'total': qs.count(),'search_query': search}
    is_htmx = request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_htmx:
        return render(request, 'permissions/granular/_x_table.html', ctx)
    return render(request, 'permissions/granular/x_list.html', ctx)
```

### 3) Export helpers
Tambahkan `export_x_csv`, `export_x_excel`, `export_x_pdf` meniru fungsi export lain (Users/Roles/Functions).

### 4) URLs
Tambahkan route list:
```python
path('x/', views_granular.x_list, name='x_list')
```

## Langkah Templates
### Partial table `_<entity>_table.html`
```html
{% load render_table from django_tables2 %}
<div id="table-content" class="relative">
  {% include 'includes/datatable_loading.html' %}
  <!-- Info bar: total + chip search (opsional) -->
  {% render_table table %}
</div>
```

### Halaman list `<entity>_list.html`
```html
{% include 'includes/datatable_filters.html' with show_search=True search_placeholder="Cari ..." show_status_filter=False %}
{% include 'includes/datatable_bulk_actions.html' with show_clear=True show_copy=True show_export=True show_print=True show_delete=True export_formats="csv,excel,pdf" %}
<div id="table-container">
  {% include 'permissions/granular/_<entity>_table.html' %}
</div>
```

### Inisialisasi DatatableHelper
```html
<script>
document.addEventListener('DOMContentLoaded', function() {
  if (window.xIntegratedDT) return;
  const csrf = document.querySelector('[name=csrfmiddlewaretoken]')?.value
             || document.querySelector('meta[name=csrf-token]')?.content || '';
  window.xIntegratedDT = new DatatableHelper({
    tableId: '<entity>_table',
    pageKey: '<entity>_list',
    saveUrl: '{% url "permissions:<entity>_list" %}',
    deleteUrl: '{% url "permissions:<entity>_list" %}',
    csrfToken: csrf,
    exportFormats: ['csv','excel','pdf'],
    entity: '<entity>',
    useToast: true, debug: true
  });
  window.xIntegratedDT.init();
});
</script>
```

## Integrasi JS (DatatableHelper)
Jika entity baru, sesuaikan mapping di `static/js/datatable-helpers.js`:
- `cacheCurrentPageData()` → baca nilai kolom berdasarkan indeks sesuai urutan `fields` di `XTable`.
- `copyToClipboard()` dan `printSelected()` → set header/kolom yang dicopy/cetak.

Contoh patokan indeks (sesuaikan):
- `selection(0), row_number(1), id(2), colA(3), colB(4), count(5/6), actions(7)`.

## HTMX & Filters
- `templates/includes/datatable_filters.html` sudah mengirim `search` via HTMX:
  - `hx-get="{{ request.path }}"`, `hx-trigger="keyup changed delay:500ms"`, `hx-target="#table-container"`, `hx-indicator="#table-loading-overlay"`.
- Pastikan view memproses `request.GET['search']`.

## Bulk Actions
- Tombol menggunakan `data-action` (clear/copy/export-*/print/delete).
- View handle:
  - `action=export_csv|export_excel|export_pdf` (berdasarkan `selected_ids`).
  - `action=bulk_delete` → hapus dan clear `UserTableSelection`.

## Download ALL Data
- Tombol ada di `templates/django_tables2/tailwind.html`: “Download Excel/PDF”.
- View list handle `POST export_all` + `search` dari POST agar terfilter sama.

## Test Checklist
- Search HTMX (tanpa full reload)
- Sorting header
- Pagination: tombol & “Loncat ke halaman”
- Show entries (10/25/50/100)
- Selection persistence (pindah halaman / reload)
- Bulk actions: Copy, Export CSV/Excel/PDF, Print, Delete
- Download ALL sesuai filter
- Loader hanya aktif saat request (tidak blok klik saat idle)

## Troubleshooting
- Overlay blok klik → pastikan CSS:
  ```css
  .htmx-indicator { opacity:0; visibility:hidden; pointer-events:none; }
  .htmx-request .htmx-indicator { opacity:1; visibility:visible; pointer-events:auto; }
  ```
- 403 CSRF saat save/load → gunakan `@ensure_csrf_cookie`, sertakan header `X-CSRFToken`.
- Kolom count selalu 0 → lupa `annotate(...)` di queryset.
- Export ALL tidak terfilter → pastikan `search` dari POST diterapkan.
- Data copy/print salah → sesuaikan indeks `cells[n]` dengan urutan kolom di `XTable`.

## Rekomendasi Penamaan
- `pageKey`: `<entity>_list`
- `tableId`: `<entity>_table`
- Partial: `_<entity>_table.html`
- URL name: `<entity>_list`

## Contoh Minimal Files Yang Dibutuhkan
- `tables.py`: `XTable`
- `views_granular.py`: `x_list` + `export_x_csv/excel/pdf`
- `urls.py`: route `path('x/', x_list, name='x_list')`
- `templates`:
  - `permissions/granular/_x_table.html`
  - `permissions/granular/x_list.html`
