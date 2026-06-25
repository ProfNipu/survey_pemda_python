/**
 * DataTable Filter Clear Utility
 * 
 * Reusable utility to automatically clear checkbox selections when
 * search box or filter dropdowns change in DataTable implementations.
 * 
 * Usage:
 * 1. Include this script in your template
 * 2. Call setupFilterClearHandlers() passing required parameters
 * 
 * Example:
 * <script src="{% static 'js/datatable-filter-clear.js' %}"></script>
 * <script>
 *   setupFilterClearHandlers({
 *     searchInputId: 'search-input',
 *     filterIds: ['status-filter', 'category-filter'],
 *     clearCallback: function() {
 *       // Custom clear logic here
 *       currentSelections = [];
 *       saveSelectionsToDB([]);
 *       allPagesDataCache = {};
 *     }
 *   });
 * </script>
 */

(function(window) {
    'use strict';
    
    /**
     * Setup filter clear handlers
     * @param {Object} config Configuration object
     * @param {string} config.searchInputId - ID of search input element
     * @param {Array<string>} config.filterIds - Array of filter element IDs (combo boxes, selects, etc)
     * @param {Function} config.clearCallback - Callback function to execute when clearing selections
     * @param {boolean} config.hideBulkBar - Whether to hide bulk actions bar (default: true)
     * @param {string} config.bulkBarId - ID of bulk actions bar element (default: 'bulk-actions-bar')
     * @param {string} config.countSpanId - ID of selected count span (default: 'selected-count')
     */
    window.setupFilterClearHandlers = function(config) {
        // Validate config
        if (!config || typeof config !== 'object') {
            console.error('[Filter Clear] Config object is required');
            return;
        }
        
        if (!config.clearCallback || typeof config.clearCallback !== 'function') {
            console.error('[Filter Clear] clearCallback function is required');
            return;
        }
        
        // Default values
        const defaults = {
            searchInputId: 'search-input',
            filterIds: [],
            hideBulkBar: true,
            bulkBarId: 'bulk-actions-bar',
            countSpanId: 'selected-count',
            selectAllTopId: 'select-all-top',
            selectAllBottomId: 'select-all-bottom',
            rowCheckboxClass: '.row-checkbox'
        };
        
        // Merge config with defaults
        const settings = Object.assign({}, defaults, config);
        
        // Prevent multiple attachments
        const handlerKey = '_filterClearHandler_' + (settings.searchInputId || 'default');
        if (window[handlerKey]) {
            console.log('[Filter Clear] Handler already attached for:', settings.searchInputId);
            return;
        }
        
        console.log('[Filter Clear] Setting up handlers with config:', settings);
        
        /**
         * Clear selections and UI elements
         */
        function clearSelectionsAndUI() {
            console.log('[Filter Clear] Clearing selections and UI...');
            
            try {
                // Call custom clear callback
                if (settings.clearCallback) {
                    settings.clearCallback();
                }
                
                // Uncheck all checkboxes
                document.querySelectorAll(settings.rowCheckboxClass).forEach(cb => cb.checked = false);
                
                // Uncheck select-all checkboxes
                const selectAllTop = document.getElementById(settings.selectAllTopId);
                const selectAllBottom = document.getElementById(settings.selectAllBottomId);
                if (selectAllTop) selectAllTop.checked = false;
                if (selectAllBottom) selectAllBottom.checked = false;
                
                // Hide bulk actions bar
                if (settings.hideBulkBar) {
                    const bulkBar = document.getElementById(settings.bulkBarId);
                    if (bulkBar) {
                        bulkBar.classList.add('hidden');
                    }
                }
                
                // Reset count
                const countSpan = document.getElementById(settings.countSpanId);
                if (countSpan) {
                    countSpan.textContent = '0';
                }
                
                console.log('[Filter Clear] Successfully cleared selections');
            } catch (error) {
                console.error('[Filter Clear] Error during clear:', error);
            }
        }
        
        /**
         * Attach handler to an element
         */
        function attachHandler(elementId, eventType, label) {
            const element = document.getElementById(elementId);
            if (element) {
                element.addEventListener(eventType, function(evt) {
                    console.log('[Filter Clear]', label, 'changed, clearing selections');
                    clearSelectionsAndUI();
                });
                console.log('[Filter Clear] Attached handler to:', elementId, 'event:', eventType);
                return true;
            } else {
                console.warn('[Filter Clear] Element not found:', elementId);
                return false;
            }
        }
        
        // Attach to search input
        let attachedCount = 0;
        if (settings.searchInputId) {
            if (attachHandler(settings.searchInputId, 'htmx:beforeRequest', 'Search')) {
                attachedCount++;
            }
        }
        
        // Attach to filter elements
        if (Array.isArray(settings.filterIds)) {
            settings.filterIds.forEach(function(filterId) {
                if (attachHandler(filterId, 'htmx:beforeRequest', 'Filter[' + filterId + ']')) {
                    attachedCount++;
                }
            });
        }
        
        // Mark as attached
        window[handlerKey] = true;
        
        console.log('[Filter Clear] Setup complete. Handlers attached:', attachedCount);
        
        return {
            success: true,
            attachedCount: attachedCount,
            clearManually: clearSelectionsAndUI
        };
    };
    
    console.log('[Filter Clear Utility] Loaded successfully');
    
})(window);
