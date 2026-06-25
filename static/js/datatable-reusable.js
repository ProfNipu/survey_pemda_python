/**
 * 🚀 REUSABLE DATATABLE SYSTEM
 * Version: 2.0 - Complete Reusable Solution
 * 
 * Usage:
 * const dt = new DatatableReusable({
 *     entityName: 'roles',
 *     pageKey: 'role_list',
 *     exportUrl: '/permissions/roles/',
 *     debug: true
 * });
 * dt.init();
 */

class DatatableReusable {
    constructor(config) {
        // Configuration with intelligent defaults
        this.config = {
            entityName: config.entityName || 'items',           // roles, users, functions
            pageKey: config.pageKey || 'default_list',          // role_list, user_list
            exportUrl: config.exportUrl || window.location.href, // Export endpoint URL
            csrfToken: config.csrfToken || this.getCSRFToken(), // Auto-detect CSRF
            debug: config.debug || false,                       // Debug logging
            
            // Features flags
            enableBulkActions: config.enableBulkActions !== false,
            enableSelection: config.enableSelection !== false,
            enableExport: config.enableExport !== false,
            
            // Export formats
            exportFormats: config.exportFormats || ['csv', 'excel', 'pdf'],
            
            // Timing configuration (in seconds)
            timing: {
                bulkExport: config.timing?.bulkExport || 0.1,     // 100ms per record
                excelExport: config.timing?.excelExport || 0.000175, // 0.175ms per record
                pdfExport: config.timing?.pdfExport || 0.00115      // 1.15ms per record
            }
        };
        
        // State management
        this.state = {
            currentSelections: [],
            allPagesDataCache: {},
            isInitialized: false,
            initCheckboxesRunning: false
        };
        
        // Bind methods to preserve context
        this.updateBulkActions = this.updateBulkActions.bind(this);
        this.exportSelected = this.exportSelected.bind(this);
        this.deleteSelected = this.deleteSelected.bind(this);
        
        this.log('DatatableReusable initialized', this.config);
    }
    
    /**
     * 🔍 Get CSRF Token automatically
     */
    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                     document.querySelector('meta[name=csrf-token]')?.getAttribute('content') || '';
        return token;
    }
    
    /**
     * 📝 Debug logging
     */
    log(...args) {
        if (this.config.debug) {
            console.log(`[DatatableReusable:${this.config.entityName}]`, ...args);
        }
    }
    
    /**
     * ⚡ Initialize the datatable system
     */
    init() {
        if (this.state.isInitialized) {
            this.log('Already initialized, skipping');
            return;
        }
        
        this.log('Initializing...');
        
        // Setup global functions
        this.setupGlobalFunctions();
        
        // Init selection system
        if (this.config.enableSelection) {
            this.initSelectionSystem();
        }
        
        // Setup HTMX listeners
        this.setupHtmxListeners();
        
        // Setup event handlers
        this.setupEventHandlers();
        
        this.state.isInitialized = true;
        this.log('Initialization complete');
    }
    
    /**
     * 🌐 Setup global functions for template access
     */
    setupGlobalFunctions() {
        // Clear search function
        window.clearSearch = () => {
            const searchInput = document.getElementById('search-input');
            if (searchInput) {
                searchInput.value = '';
                htmx.trigger(searchInput, 'keyup');
            }
        };
        
        // Export functions
        window.exportSelected = this.exportSelected;
        window.deleteSelected = this.deleteSelected;
        window.clearAllSelections = () => this.clearAllSelections();
        window.copySelectedToClipboard = () => this.copySelectedToClipboard();
        window.printSelected = () => this.printSelected();
    }
    
    /**
     * ✅ Initialize selection system
     */
    initSelectionSystem() {
        this.log('Initializing selection system...');
        
        // Load selections from database
        this.loadSelectionsFromDB().then(selectedIds => {
            this.state.currentSelections = selectedIds || [];
            this.setupCheckboxListeners();
            this.updateBulkActions();
            this.cacheCurrentPageData();
        });
    }
    
    /**
     * 💾 Load selections from database
     */
    async loadSelectionsFromDB() {
        try {
            const response = await fetch(this.config.exportUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.config.csrfToken
                },
                body: JSON.stringify({
                    action: 'load_selection',
                    page_key: this.config.pageKey
                })
            });
            
            const data = await response.json();
            return data.success ? data.selected_ids : [];
        } catch (error) {
            this.log('Error loading selections:', error);
            return [];
        }
    }
    
    /**
     * 💾 Save selections to database
     */
    async saveSelectionsToDB(ids) {
        try {
            const response = await fetch(this.config.exportUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.config.csrfToken
                },
                body: JSON.stringify({
                    action: 'save_selection',
                    page_key: this.config.pageKey,
                    selected_ids: ids
                })
            });
            
            const data = await response.json();
            this.log('Saved selections:', data.count, 'items');
        } catch (error) {
            this.log('Error saving selections:', error);
        }
    }
    
    /**
     * 🔲 Setup checkbox listeners
     */
    setupCheckboxListeners() {
        // Individual checkboxes
        document.querySelectorAll('.row-checkbox').forEach(checkbox => {
            checkbox.checked = this.state.currentSelections.includes(checkbox.value);
            checkbox.addEventListener('change', this.updateBulkActions);
        });
        
        // Select all checkboxes
        const selectAllTop = document.getElementById('select-all-top');
        const selectAllBottom = document.getElementById('select-all-bottom');
        
        if (selectAllTop) {
            selectAllTop.addEventListener('change', (e) => {
                document.querySelectorAll('.row-checkbox').forEach(cb => cb.checked = e.target.checked);
                if (selectAllBottom) {
                    selectAllBottom.checked = e.target.checked;
                    selectAllBottom.indeterminate = false;
                }
                selectAllTop.indeterminate = false;
                this.updateBulkActions();
            });
        }
        
        if (selectAllBottom) {
            selectAllBottom.addEventListener('change', (e) => {
                document.querySelectorAll('.row-checkbox').forEach(cb => cb.checked = e.target.checked);
                if (selectAllTop) {
                    selectAllTop.checked = e.target.checked;
                    selectAllTop.indeterminate = false;
                }
                selectAllBottom.indeterminate = false;
                this.updateBulkActions();
            });
        }
    }
    
    /**
     * 🔄 Update bulk actions visibility and count
     */
    updateBulkActions() {
        const allBoxes = document.querySelectorAll('.row-checkbox');
        const checkedBoxes = document.querySelectorAll('.row-checkbox:checked');
        const bulkActionsBar = document.getElementById('bulk-actions-bar');
        const selectedCountSpan = document.getElementById('selected-count');
        
        // Update stored selections
        const currentPageIds = Array.from(allBoxes).map(cb => cb.value);
        const filteredIds = this.state.currentSelections.filter(id => !currentPageIds.includes(id));
        
        checkedBoxes.forEach(cb => {
            if (!filteredIds.includes(cb.value)) {
                filteredIds.push(cb.value);
            }
        });
        
        // Sync master select-all (top & bottom)
        const total = allBoxes.length;
        const selected = checkedBoxes.length;
        const selectAllTop = document.getElementById('select-all-top');
        const selectAllBottom = document.getElementById('select-all-bottom');
        const setMaster = (el) => {
            if (!el) return;
            if (selected === 0 || total === 0) {
                el.checked = false;
                el.indeterminate = false;
            } else if (selected === total) {
                el.checked = true;
                el.indeterminate = false;
            } else {
                el.checked = false;
                el.indeterminate = true;
            }
        };
        setMaster(selectAllTop);
        setMaster(selectAllBottom);

        this.state.currentSelections = filteredIds;
        this.saveSelectionsToDB(filteredIds);
        
        // Update UI
        const totalCount = filteredIds.length;
        if (selectedCountSpan) selectedCountSpan.textContent = totalCount;
        
        if (bulkActionsBar) {
            if (totalCount > 0) {
                bulkActionsBar.classList.remove('hidden');
            } else {
                bulkActionsBar.classList.add('hidden');
            }
        }
        
        this.log('Updated selections:', totalCount, 'items');
    }
    
    /**
     * 📤 Export selected items
     */
    exportSelected(format) {
        const ids = this.state.currentSelections;
        this.log('Export', format, 'for', ids.length, 'items');
        
        if (ids.length === 0) {
            Swal.fire({
                icon: 'warning',
                title: 'Tidak Ada Item Terpilih',
                text: 'Pilih minimal 1 item untuk export',
                confirmButtonText: 'OK'
            });
            return;
        }
        
        // Create form
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = this.config.exportUrl;
        
        // CSRF token
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = this.config.csrfToken;
        form.appendChild(csrfInput);
        
        // Action
        const actionInput = document.createElement('input');
        actionInput.type = 'hidden';
        actionInput.name = 'action';
        actionInput.value = 'export_' + format;
        form.appendChild(actionInput);
        
        // Selected IDs
        ids.forEach(id => {
            const idInput = document.createElement('input');
            idInput.type = 'hidden';
            idInput.name = 'selected_ids';
            idInput.value = id;
            form.appendChild(idInput);
        });
        
        // Show loading
        const loadingTime = ids.length * this.config.timing.bulkExport * 1000;
        const loadingSeconds = (loadingTime / 1000).toFixed(1);
        
        Swal.fire({
            title: `Memproses Export ${format.toUpperCase()}`,
            html: `
                <div style="margin: 20px 0;">
                    <p style="margin-bottom: 10px;"><b>${ids.length} records</b></p>
                    <p style="margin-bottom: 15px;">Estimasi: ~${loadingSeconds} detik</p>
                </div>
            `,
            allowOutsideClick: false,
            allowEscapeKey: false,
            didOpen: () => Swal.showLoading()
        });
        
        // Submit form
        document.body.appendChild(form);
        form.submit();
        
        // Show success message
        setTimeout(() => {
            Swal.close();
            Swal.fire({
                icon: 'success',
                title: 'Berhasil!',
                text: `File ${format.toUpperCase()} dengan ${ids.length} item berhasil didownload`,
                confirmButtonText: 'OK',
                confirmButtonColor: '#3085d6'
            });
            document.body.removeChild(form);
        }, loadingTime);
    }
    
    /**
     * 🗑️ Delete selected items
     */
    deleteSelected() {
        const ids = this.state.currentSelections;
        this.log('Delete requested for', ids.length, 'items');
        
        if (ids.length === 0) {
            Swal.fire({
                icon: 'warning',
                title: 'Tidak Ada Item Terpilih',
                text: 'Pilih minimal 1 item untuk dihapus',
                confirmButtonText: 'OK'
            });
            return;
        }
        
        Swal.fire({
            title: 'Konfirmasi Hapus',
            html: `Yakin ingin menghapus <b>${ids.length} ${this.config.entityName}</b> terpilih?<br><br><small style="color:#dc2626">⚠️ Tindakan ini tidak dapat dibatalkan!</small>`,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Ya, Hapus!',
            cancelButtonText: 'Batal',
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6'
        }).then((result) => {
            if (result.isConfirmed) {
                this.performDelete(ids);
            }
        });
    }
    
    /**
     * 🗑️ Perform actual deletion
     */
    performDelete(ids) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = this.config.exportUrl;
        
        // CSRF token
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = this.config.csrfToken;
        form.appendChild(csrfInput);
        
        // Action
        const actionInput = document.createElement('input');
        actionInput.type = 'hidden';
        actionInput.name = 'action';
        actionInput.value = 'bulk_delete';
        form.appendChild(actionInput);
        
        // Selected IDs
        ids.forEach(id => {
            const idInput = document.createElement('input');
            idInput.type = 'hidden';
            idInput.name = 'selected_ids';
            idInput.value = id;
            form.appendChild(idInput);
        });
        
        document.body.appendChild(form);
        form.submit();
    }
    
    /**
     * 🧹 Clear all selections
     */
    clearAllSelections() {
        this.state.currentSelections = [];
        this.saveSelectionsToDB([]);
        
        document.querySelectorAll('.row-checkbox').forEach(cb => cb.checked = false);
        const selectAllTop = document.getElementById('select-all-top');
        const selectAllBottom = document.getElementById('select-all-bottom');
        if (selectAllTop) selectAllTop.checked = false;
        if (selectAllBottom) selectAllBottom.checked = false;
        
        this.updateBulkActions();
    }
    
    /**
     * 📋 Copy selected to clipboard
     */
    copySelectedToClipboard() {
        // Implementation for copy functionality
        this.log('Copy to clipboard requested');
        // TODO: Implement copy logic
    }
    
    /**
     * 🖨️ Print selected items
     */
    printSelected() {
        // Implementation for print functionality
        this.log('Print requested');
        // TODO: Implement print logic
    }
    
    /**
     * 💾 Cache current page data
     */
    cacheCurrentPageData() {
        const table = document.querySelector('table');
        if (!table) return;
        
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            const checkbox = row.querySelector('.row-checkbox');
            if (checkbox) {
                const id = checkbox.value;
                const cells = row.querySelectorAll('td');
                const rowData = [];
                cells.forEach(cell => {
                    if (!cell.querySelector('input[type="checkbox"]')) {
                        rowData.push(cell.innerText.trim());
                    }
                });
                this.state.allPagesDataCache[id] = rowData;
            }
        });
        
        this.log('Cached data for', Object.keys(this.state.allPagesDataCache).length, 'items');
    }
    
    /**
     * 🔄 Setup HTMX listeners
     */
    setupHtmxListeners() {
        if (!window.datatableHtmxHandlerAttached) {
            document.body.addEventListener('htmx:afterSwap', (evt) => {
                const targetId = evt.detail.target.id;
                if (targetId === 'table-container' || targetId === 'table-content') {
                    this.log('HTMX swap detected, re-initializing...');
                    setTimeout(() => {
                        this.setupCheckboxListeners();
                        this.cacheCurrentPageData();
                        this.updateBulkActions();
                    }, 100);
                }
            });
            window.datatableHtmxHandlerAttached = true;
        }
    }
    
    /**
     * 🎯 Setup event handlers
     */
    setupEventHandlers() {
        if (!window.datatableBulkActionsAttached) {
            document.addEventListener('click', (e) => {
                const target = e.target.closest('[data-action]');
                if (!target) return;
                
                e.preventDefault();
                e.stopPropagation();
                
                const action = target.dataset.action;
                this.log('Bulk action clicked:', action);
                
                switch (action) {
                    case 'clear':
                        this.clearAllSelections();
                        break;
                    case 'copy':
                        this.copySelectedToClipboard();
                        break;
                    case 'export-csv':
                        this.exportSelected('csv');
                        break;
                    case 'export-excel':
                        this.exportSelected('excel');
                        break;
                    case 'export-pdf':
                        this.exportSelected('pdf');
                        break;
                    case 'print':
                        this.printSelected();
                        break;
                    case 'delete':
                        this.deleteSelected();
                        break;
                }
            }, true);
            window.datatableBulkActionsAttached = true;
        }
    }
}

// Export for global use
window.DatatableReusable = DatatableReusable;
