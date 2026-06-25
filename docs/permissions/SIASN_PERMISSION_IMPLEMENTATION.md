# 🔐 SIASN PERMISSION SYSTEM - IMPLEMENTATION GUIDE

## Struktur Database (5 Tables)

```
1. siasn_modules           - Grouping (View Data, Fetch Data, etc)
2. siasn_controllers       - Sub-group (Cache Management, Token Management)
3. siasn_fungsi            - Permissions (siasn.view_data, siasn.fetch_data)
4. siasn_rules             - Mapping: Module > Controller > Fungsi
5. siasn_role_permissions  - Mapping: Role > Rules
```

## Files Yang Perlu Dibuat

### Migrations (5 files)
- `2025_01_01_000001_create_siasn_modules_table.php`
- `2025_01_01_000002_create_siasn_controllers_table.php`
- `2025_01_01_000003_create_siasn_fungsi_table.php`
- `2025_01_01_000004_create_siasn_rules_table.php`
- `2025_01_01_000005_create_siasn_role_permissions_table.php`

### Models (5 files)
- `app/Models/Siasn_module.php`
- `app/Models/Siasn_controller.php`
- `app/Models/Siasn_fungsi.php`
- `app/Models/Siasn_rules.php`
- `app/Models/Siasn_role_permission.php`

### Controllers (1 file utama)
- `app/Http/Controllers/Siasn_privilegesController.php`

### Views (1 file)
- `resources/views/siasn/privileges.blade.php`

### Seeders (1 file)
- `database/seeders/SiasnPermissionSeeder.php`

## Default Permissions (15 permissions)

### View Data (4):
- siasn.view_data
- siasn.view_dashboard
- siasn.view_logs
- siasn.view_progress

### Fetch Data (3):
- siasn.fetch_data
- siasn.fetch_minimal
- siasn.sync_data

### Download Files (2):
- siasn.download_foto
- siasn.download_dokumen

### Management (6):
- siasn.delete_cache
- siasn.view_token
- siasn.manage_token
- siasn.configure
- siasn.admin

## Routes

```php
Route::group(['prefix' => 'siasn', 'middleware' => ['auth']], function () {
    // Show privileges form
    Route::get('/privileges/{role}', [Siasn_privilegesController::class, 'show'])
        ->name('siasn_privileges');
    
    // Update privileges
    Route::post('/privileges/update', [Siasn_privilegesController::class, 'update'])
        ->name('siasn_privileges.update');
});
```

## Usage

### Check Permission
```php
// In controller
if (Siasn_privilegesController::userHasPermission(auth()->id(), 'siasn.fetch_data')) {
    // User can fetch data
}

// In Blade
@can('siasn.fetch_data')
    <button>Fetch Data</button>
@endcan
```

### Assign Permission to Role
1. Go to: `/siasn/privileges/{role_id}`
2. Check permissions
3. Click Submit

