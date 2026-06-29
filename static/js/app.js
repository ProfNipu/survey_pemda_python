/**
 * aplikasi-test - Reusable JavaScript Functions Library
 * Pure JavaScript (No jQuery dependency)
 * 
 * Usage:
 * 1. Include in template: <script src="{% static 'js/app.js' %}"></script>
 * 2. Call functions: showToast('Message', 'success')
 * 
 * Available Functions:
 * - togglePassword()             - Password visibility toggle
 * - formSubmitLoading()          - Form loading state
 * - autoFocusInput()             - Auto-focus input
 * - toggleSidebar()              - Sidebar mobile toggle
 * - confirmAction()              - Confirmation dialog
 * - copyToClipboard()            - Copy text
 * - debounce()                   - Debounce function
 * - onReady()                    - DOM ready handler
 * - showToast()                  - Toast notification (max 3)
 * - removeToast()                - Remove toast
 * - initSessionMonitor()         - Session inactivity monitor (auto-logout)
 * - showLoading()                - SweetAlert loading
 * - showSuccess()                - SweetAlert success
 * - showSuccessWithCountdown()   - SweetAlert success with countdown & username
 * - showError()                  - SweetAlert error
 * - showPasswordMismatchError()  - Password mismatch error (REUSABLE!)
 * - showInvalidPasswordError()   - Invalid password error (REUSABLE!)
 * - showConfirm()                - SweetAlert confirm
 * - ajaxFormSubmit()             - AJAX form (simple, no SweetAlert)
 * - ajaxFormSubmitWithSwal()     - AJAX form with SweetAlert (REUSABLE!)
 * 
 * Configuration:
 * TOAST_CONFIG.MAX_TOASTS = 3  (change if needed)
 * TOAST_CONFIG.DURATION = 5000 (ms, change if needed)
 */

// ==========================================
// PASSWORD TOGGLE
// ==========================================

/**
 * Toggle password visibility
 * @param {string} inputId - ID of password input
 * @param {string} iconId - ID of toggle icon
 */
function togglePassword(inputId = 'password', iconId = 'toggleIcon') {
    const passwordInput = document.getElementById(inputId);
    const toggleIcon = document.getElementById(iconId);
    
    if (!passwordInput || !toggleIcon) return;
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleIcon.classList.remove('fa-eye');
        toggleIcon.classList.add('fa-eye-slash');
    } else {
        passwordInput.type = 'password';
        toggleIcon.classList.remove('fa-eye-slash');
        toggleIcon.classList.add('fa-eye');
    }
}

// ==========================================
// FORM SUBMIT LOADING
// ==========================================

/**
 * Add loading state to form submission
 * @param {string} formSelector - CSS selector for form
 * @param {string} buttonId - ID of submit button
 * @param {string} loadingText - Loading text to display
 */
function formSubmitLoading(formSelector, buttonId, loadingText = 'Memproses...') {
    const form = document.querySelector(formSelector);
    const button = document.getElementById(buttonId);
    
    if (!form || !button) return;
    
    form.addEventListener('submit', function() {
        button.innerHTML = `<i class="fas fa-spinner fa-spin mr-2"></i> ${loadingText}`;
        button.disabled = true;
    });
}

// ==========================================
// AUTO FOCUS
// ==========================================

/**
 * Auto focus on input field (desktop only)
 * @param {string} selector - CSS selector for input
 * @param {number} minWidth - Minimum screen width (default: 768px)
 */
function autoFocusInput(selector, minWidth = 768) {
    if (window.innerWidth > minWidth) {
        const input = document.querySelector(selector);
        if (input) input.focus();
    }
}

// ==========================================
// SIDEBAR TOGGLE (for mobile)
// ==========================================

/**
 * Toggle sidebar visibility
 */
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (sidebar) {
        sidebar.classList.toggle('active');
    }
}

// ==========================================
// CONFIRM DIALOG
// ==========================================

/**
 * Show confirmation dialog before action
 * @param {string} message - Confirmation message
 * @param {function} callback - Function to execute if confirmed
 */
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// ==========================================
// COPY TO CLIPBOARD
// ==========================================

/**
 * Copy text to clipboard
 * @param {string} text - Text to copy
 * @param {string} successMessage - Success message to show
 */
function copyToClipboard(text, successMessage = 'Copied to clipboard!') {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            alert(successMessage);
        });
    } else {
        // Fallback for older browsers
        const textarea = document.createElement('textarea');
        textarea.value = text;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        alert(successMessage);
    }
}

// ==========================================
// DEBOUNCE (for search inputs)
// ==========================================

/**
 * Debounce function to limit function calls
 * @param {function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 */
function debounce(func, wait = 300) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ==========================================
// READY STATE
// ==========================================

/**
 * Execute function when DOM is ready
 * @param {function} callback - Function to execute
 */
function onReady(callback) {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', callback);
    } else {
        callback();
    }
}

// ==========================================
// DATE INPUT (dd-mm-yyyy) - Reusable
// - Use class: js-date-ddmmyyyy (set by backend helper date_ddmmyyyy_attrs)
// - Works with plain input[type=text] and preserves local-only policy
// ==========================================
function initDateDdMmYyyy(root) {
    const scope = root && root.querySelectorAll ? root : document;
    const inputs = Array.from(scope.querySelectorAll('input.js-date-ddmmyyyy'));
    inputs.forEach(function (inp) {
        if (!inp || inp.dataset.dateEnhanced === '1') return;
        inp.dataset.dateEnhanced = '1';

        try {
            inp.setAttribute('autocomplete', 'off');
            inp.setAttribute('inputmode', 'numeric');
            if (!inp.getAttribute('placeholder')) inp.setAttribute('placeholder', 'dd-mm-yyyy');
        } catch (_) {}

        function formatRawDigits(digits) {
            const d = (digits || '').replace(/\D/g, '').slice(0, 8);
            const dd = d.slice(0, 2);
            const mm = d.slice(2, 4);
            const yyyy = d.slice(4, 8);
            let out = dd;
            if (mm) out += '-' + mm;
            if (yyyy) out += '-' + yyyy;
            return out;
        }

        function isValidDateStr(v) {
            const m = String(v || '').match(/^(\d{2})-(\d{2})-(\d{4})$/);
            if (!m) return false;
            const dd = parseInt(m[1], 10);
            const mm = parseInt(m[2], 10);
            const yyyy = parseInt(m[3], 10);
            if (!yyyy || mm < 1 || mm > 12 || dd < 1 || dd > 31) return false;
            const dt = new Date(yyyy, mm - 1, dd);
            return dt.getFullYear() === yyyy && (dt.getMonth() + 1) === mm && dt.getDate() === dd;
        }

        function ddmmyyyyToIso(v) {
            const m = String(v || '').match(/^(\d{2})-(\d{2})-(\d{4})$/);
            if (!m) return '';
            const dd = m[1];
            const mm = m[2];
            const yyyy = m[3];
            return `${yyyy}-${mm}-${dd}`;
        }

        function isoToDdMmYyyy(v) {
            const m = String(v || '').match(/^(\d{4})-(\d{2})-(\d{2})$/);
            if (!m) return '';
            const yyyy = m[1];
            const mm = m[2];
            const dd = m[3];
            return `${dd}-${mm}-${yyyy}`;
        }

        try {
            if (!inp.dataset.datePickerAttached) {
                inp.dataset.datePickerAttached = '1';

                // Wrap into an input-group style container (Laravel-like)
                const originalParent = inp.parentElement;
                let host = originalParent;
                try {
                    if (originalParent && originalParent.dataset && originalParent.dataset.dateGroup === '1') {
                        host = originalParent;
                    } else if (originalParent) {
                        const group = document.createElement('div');
                        group.className = 'flex w-full';
                        group.dataset.dateGroup = '1';
                        originalParent.insertBefore(group, inp);
                        group.appendChild(inp);
                        host = group;
                    }
                } catch (_) {}

                const hidden = document.createElement('input');
                hidden.type = 'date';
                hidden.tabIndex = -1;
                hidden.setAttribute('aria-hidden', 'true');
                hidden.style.position = 'absolute';
                hidden.style.left = '0';
                hidden.style.top = '0';
                hidden.style.width = '100%';
                hidden.style.height = '100%';
                hidden.style.opacity = '0';
                hidden.style.pointerEvents = 'none';
                hidden.dataset.dateProxy = '1';

                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'relative flex-none w-12 h-12 flex items-center justify-center bg-gray-100 border-2 border-gray-200 border-l-0 text-gray-500 hover:text-gray-700 rounded-r-lg focus:outline-none focus:ring-0 focus-visible:outline-none focus-visible:ring-0';
                btn.innerHTML = '<i class="fas fa-calendar-alt"></i>';
                btn.dataset.dateBtn = '1';

                try {
                    host.appendChild(btn);
                    inp.style.borderTopRightRadius = '0';
                    inp.style.borderBottomRightRadius = '0';
                    inp.style.borderRightWidth = '0';
                    inp.style.flex = '1 1 auto';
                    btn.style.outline = 'none';

                    // Put the proxy input inside the addon button so the picker anchors correctly
                    btn.appendChild(hidden);
                } catch (_) {}

                function syncHiddenFromText() {
                    const v = (inp.value || '').trim();
                    if (!isValidDateStr(v)) return;
                    const iso = ddmmyyyyToIso(v);
                    if (iso) hidden.value = iso;
                }

                function syncTextFromHidden() {
                    const v = (hidden.value || '').trim();
                    const ddmmyyyy = isoToDdMmYyyy(v);
                    if (ddmmyyyy) {
                        inp.value = ddmmyyyy;
                        try { inp.dispatchEvent(new Event('change', { bubbles: true })); } catch (_) {}
                    }
                }

                btn.addEventListener('click', function () {
                    try { syncHiddenFromText(); } catch (_) {}
                    try {
                        if (hidden.showPicker) hidden.showPicker();
                        else hidden.click();
                    } catch (_) {
                        try { hidden.focus(); hidden.click(); } catch (_) {}
                    }
                });

                btn.addEventListener('mousedown', function (e) {
                    try { e.preventDefault(); } catch (_) {}
                });

                hidden.addEventListener('change', function () {
                    try { syncTextFromHidden(); } catch (_) {}
                });

                inp.addEventListener('blur', function () {
                    try { syncHiddenFromText(); } catch (_) {}
                });

                try { syncHiddenFromText(); } catch (_) {}
            }
        } catch (_) {}

        // Normalize initial value if it's digits-only
        try {
            const v0 = (inp.value || '').trim();
            if (v0 && /^\d{8}$/.test(v0)) {
                inp.value = formatRawDigits(v0);
            }
        } catch (_) {}

        inp.addEventListener('input', function () {
            const start = inp.selectionStart;
            const raw = inp.value;
            const formatted = formatRawDigits(raw);
            if (raw !== formatted) {
                inp.value = formatted;
                try {
                    const pos = Math.min(formatted.length, (start || formatted.length));
                    inp.setSelectionRange(pos, pos);
                } catch (_) {}
            }
        });

        inp.addEventListener('blur', function () {
            const v = (inp.value || '').trim();
            if (!v) {
                try { inp.classList.remove('border-red-500'); } catch (_) {}
                return;
            }
            if (isValidDateStr(v)) {
                try { inp.classList.remove('border-red-500'); } catch (_) {}
            } else {
                try { inp.classList.add('border-red-500'); } catch (_) {}
            }
        });
    });
}

try {
    onReady(function(){
        try {
            if (document.getElementById('aplikasi-test-modal-open-hide-dt-style')) return;
            const st = document.createElement('style');
            st.id = 'aplikasi-test-modal-open-hide-dt-style';
            st.type = 'text/css';
            st.textContent = `
              body.aplikasi-test-modal-open .dataTables_processing { display: none !important; }
              body.aplikasi-test-modal-open #table-loading-overlay { display: none !important; }
            `;
            document.head && document.head.appendChild(st);
        } catch(_) {}
    });
} catch(_) {}

// ==========================================
// TOAST NOTIFICATION (Dynamic & Reusable)
// ==========================================

// Global config for toast system
const TOAST_CONFIG = {
    MAX_TOASTS: 3,       // Maximum toasts visible at once
    DURATION: 5000,      // Auto-hide duration in milliseconds
    THROTTLE_MS: 300     // Minimum time between toasts (prevent spam)
};

// Track last toast time for throttling
let lastToastTime = 0;

// Session inactivity config
const SESSION_CONFIG = {
    TIMEOUT: 1800000,      // 30 minutes in milliseconds (30 * 60 * 1000)
    WARNING_TIME: 300000   // Show warning 5 minutes before timeout (5 * 60 * 1000)
};

try {
    document.addEventListener('DOMContentLoaded', function() {
        try {
            const raw = sessionStorage.getItem('__esimpeg_toast_next__');
            if (!raw) return;
            sessionStorage.removeItem('__esimpeg_toast_next__');
            const data = JSON.parse(raw);
            if (!data) return;
            const msg = data.message;
            const type = data.type || 'success';
            if (msg && typeof window.showToast === 'function') {
                window.showToast(msg, type);
            }
        } catch (_) {
            try { sessionStorage.removeItem('__esimpeg_toast_next__'); } catch (_) {}
        }
    });
} catch (_) {}

// Track user activity
let lastActivityTime = Date.now();
let inactivityWarningShown = false;
let sessionExpiredShown = false;
let sessionSupersededShown = false;

/**
 * Show dynamic toast notification
 * Reusable across all pages
 * Maximum 3 toasts at a time to prevent spam
 * @param {string} message - Toast message
 * @param {string} type - Toast type (success, error, warning, info)
 */
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    // THROTTLE: Prevent spam (ignore if called too quickly)
    const now = Date.now();
    if (now - lastToastTime < TOAST_CONFIG.THROTTLE_MS) {
        return; // ✅ Ignore spam calls
    }
    lastToastTime = now;
    
    // Limit max toasts (prevent spam)
    const existingToasts = container.querySelectorAll('.toast-message');
    
    if (existingToasts.length >= TOAST_CONFIG.MAX_TOASTS) {
        // FORCE REMOVE oldest toast IMMEDIATELY (no animation delay)
        const oldestToast = existingToasts[0];
        if (oldestToast) {
            oldestToast.remove(); // ✅ Instant removal (synchronous)
        }
    }
    
    const colors = {
        'success': 'bg-green-500 border-green-700',
        'error': 'bg-red-500 border-red-700',
        'warning': 'bg-amber-500 border-amber-700',
        'info': 'bg-blue-500 border-blue-700'
    };
    
    const icons = {
        'success': 'fa-check-circle',
        'error': 'fa-exclamation-circle',
        'warning': 'fa-exclamation-triangle',
        'info': 'fa-info-circle'
    };
    
    const colorClass = colors[type] || colors['info'];
    const iconClass = icons[type] || icons['info'];
    
    const toast = document.createElement('div');
    toast.className = `toast-message relative overflow-hidden rounded-lg shadow-lg border-l-4 ${colorClass} text-white transform transition-all duration-500 ease-in-out opacity-0 translate-x-full`;
    toast.innerHTML = `
        <div class="flex items-start p-4">
            <div class="flex items-center gap-3 flex-1">
                <i class="fas ${iconClass} text-xl"></i>
                <span class="text-sm font-medium">${message}</span>
            </div>
            <button type="button" class="ml-3 text-white hover:text-gray-200 transition-colors" onclick="removeToast(this)">
                <i class="fas fa-times"></i>
            </button>
        </div>
        <div class="absolute bottom-0 left-0 h-1.5 bg-black/10 w-full overflow-hidden">
            <div class="toast-timer h-full" style="width: 100%; background: linear-gradient(90deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.7) 100%);"></div>
        </div>
    `;
    
    container.appendChild(toast);
    
    const timer = toast.querySelector('.toast-timer');
    
    setTimeout(() => {
        toast.style.opacity = '1';
        toast.style.transform = 'translateX(0)';
        
        if (timer) {
            timer.offsetHeight;
            timer.style.transition = `width ${TOAST_CONFIG.DURATION}ms linear`;
            requestAnimationFrame(() => {
                requestAnimationFrame(() => {
                    timer.style.width = '0%';
                });
            });
        }
    }, 50);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }, TOAST_CONFIG.DURATION);
}

/**
 * Remove toast manually
 * @param {HTMLElement} button - Close button element
 */
function removeToast(button) {
    const toast = button.closest('.toast-message');
    if (!toast) return;
    
    const timer = toast.querySelector('.toast-timer');
    if (timer) timer.style.transition = 'none';
    
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    setTimeout(() => toast.remove(), 300);
}

// ==========================================
// SESSION INACTIVITY MONITOR
// ==========================================

/**
 * Initialize session inactivity monitor
 * Auto-logout user after 30 minutes of inactivity
 * Show warning 5 minutes before logout
 */
function initSessionMonitor() {
    // Update activity time on user interactions
    const activityEvents = ['mousedown', 'keydown', 'scroll', 'touchstart', 'click'];
    
    activityEvents.forEach(event => {
        document.addEventListener(event, function() {
            lastActivityTime = Date.now();
            inactivityWarningShown = false;
        });
    });
    
    // Check inactivity and session status every 30 seconds
    setInterval(function() {
        const now = Date.now();
        const inactiveTime = now - lastActivityTime;
        const remainingTime = SESSION_CONFIG.TIMEOUT - inactiveTime;
        
        // Show warning 5 minutes before logout
        if (remainingTime <= SESSION_CONFIG.WARNING_TIME && !inactivityWarningShown) {
            inactivityWarningShown = true;
            
            const minutes = Math.floor(remainingTime / 60000);
            
            Swal.fire({
                icon: 'warning',
                title: 'Sesi Akan Berakhir',
                html: `Sesi Anda akan berakhir dalam <b>${minutes}</b> menit karena tidak ada aktivitas.<br><br>Klik OK untuk melanjutkan sesi.`,
                confirmButtonText: 'OK, Lanjutkan Sesi',
                confirmButtonColor: '#3085d6',
                allowOutsideClick: false
            }).then((result) => {
                if (result.isConfirmed) {
                    // Reset activity time
                    lastActivityTime = Date.now();
                    inactivityWarningShown = false;
                    
                    // Ping server to keep session alive
                    fetch('/dashboard/', {
                        method: 'GET',
                        credentials: 'same-origin'
                    });
                }
            });
        }
        
        // Session expired: show blocking modal, logout ONLY after user clicks OK
        if (inactiveTime >= SESSION_CONFIG.TIMEOUT && !sessionExpiredShown) {
            sessionExpiredShown = true;
            Swal.fire({
                icon: 'info',
                title: 'Sesi Berakhir',
                text: 'Sesi Anda telah berakhir karena tidak ada aktivitas. Klik OK untuk logout.',
                confirmButtonText: 'OK',
                allowOutsideClick: false,
                allowEscapeKey: false,
                backdrop: true,
                showCancelButton: false,
                focusConfirm: true
            }).then(() => {
                const logoutUrl = window.LOGOUT_URL || '/accounts/logout/';
                window.location.href = logoutUrl;
            });
        }

        // Detect session superseded (login from another device)
        if (!sessionSupersededShown && !sessionExpiredShown) {
            fetch('/session/status', { credentials: 'same-origin' })
                .then(r => r.ok ? r.json() : null)
                .then(data => {
                    if (data && data.session_superseded && !sessionSupersededShown) {
                        sessionSupersededShown = true;
                        Swal.fire({
                            icon: 'warning',
                            title: 'Akun Dipakai di Perangkat Lain',
                            text: 'Akun Anda terdeteksi login di perangkat lain. Klik OK untuk logout dari perangkat ini.',
                            confirmButtonText: 'OK',
                            allowOutsideClick: false,
                            allowEscapeKey: false,
                            backdrop: true,
                            showCancelButton: false,
                            focusConfirm: true
                        }).then(() => {
                            const logoutUrl = window.LOGOUT_URL || '/accounts/logout/';
                            window.location.href = logoutUrl;
                        });
                    }
                })
                .catch(() => {});
        }
    }, 30000); // Check every 30 seconds
}

// ==========================================
// SWEETALERT2 HELPERS (Reusable)
// ==========================================

/**
 * Show loading SweetAlert
 * @param {string} title - Loading title
 * @param {string} text - Loading text
 */
function showLoading(title = 'Memproses...', text = 'Mohon tunggu sebentar') {
    Swal.fire({
        title: title,
        html: text,
        allowOutsideClick: false,
        allowEscapeKey: false,
        didOpen: () => {
            Swal.showLoading();
        }
    });
}

/**
 * Show success SweetAlert
 * @param {string} title - Success title
 * @param {string} text - Success text
 * @param {function} callback - Callback after close
 */
function showSuccess(title = 'Berhasil!', text = '', callback = null) {
    Swal.fire({
        icon: 'success',
        title: title,
        text: text,
        timer: 1500,
        showConfirmButton: false
    }).then(() => {
        if (callback) callback();
    });
}

/**
 * Show error SweetAlert
 * @param {string} title - Error title
 * @param {string} text - Error text
 */
function showError(title = 'Terjadi Kesalahan!', text = 'Silakan coba lagi') {
    Swal.fire({
        icon: 'error',
        title: title,
        html: text,
        confirmButtonText: 'OK',
        confirmButtonColor: '#3085d6',
        allowOutsideClick: false,
        allowEscapeKey: false,
        focusConfirm: true
    });
}

/**
 * Show password mismatch error (REUSABLE!)
 */
function showPasswordMismatchError() {
    return Swal.fire({
        icon: 'error',
        title: 'Password Tidak Cocok',
        text: 'Password baru dan konfirmasi password harus sama',
        confirmButtonColor: '#0066cc'
    });
}

/**
 * Show invalid password error (REUSABLE!)
 * @param {string} message - Custom error message
 */
function showInvalidPasswordError(message = 'Password tidak valid!') {
    return Swal.fire({
        icon: 'error',
        title: 'Password Tidak Valid',
        text: message,
        confirmButtonColor: '#0066cc'
    });
}

/**
 * Show success SweetAlert with countdown timer (REUSABLE & FLEXIBLE!)
 * Can be used for any success scenario: login, save, delete, password change, etc.
 * 
 * @param {string|object} titleOrOptions - Title string OR options object
 * @param {string} message - Message (if first param is string)
 * @param {object} options - Options (if first param is string)
 * 
 * OPTIONS (when using object as first param):
 * @param {string} options.title - Success title (default: 'Berhasil!')
 * @param {string} options.message - Success message
 * @param {string} options.icon - Icon type: success, warning, info, error (default: 'success')
 * @param {number} options.countdown - Countdown duration in seconds (default: 5, set 0 to disable)
 * @param {boolean} options.showCountdown - Show countdown text (default: true if countdown > 0)
 * @param {boolean} options.progressBar - Show progress bar (default: true if countdown > 0)
 * @param {boolean} options.showButton - Show confirm button (default: false if countdown > 0)
 * @param {string} options.buttonText - Confirm button text (default: 'OK')
 * @param {string} options.username - Username to display
 * @param {string} options.fullName - Full name to display (priority over username)
 * @param {string} options.userLabel - Custom label for user display
 * @param {string} options.customHtml - Additional custom HTML
 * @param {function} options.callback - Callback after close
 * @param {string} options.redirectUrl - Auto redirect URL after close
 * @param {boolean} options.allowOutsideClick - Allow close by clicking outside (default: false if countdown)
 * 
 * USAGE EXAMPLES:
 * 
 * // 1. Simple with countdown (one-liner)
 * showSuccessWithCountdown('Data Tersimpan!', 'Data berhasil disimpan', {countdown: 3});
 * 
 * // 2. With username display
 * showSuccessWithCountdown({title: 'Login Berhasil!', username: 'Admin', countdown: 5});
 * 
 * // 3. Without countdown (standard SweetAlert but consistent API)
 * showSuccessWithCountdown({title: 'Berhasil!', message: 'Data tersimpan', countdown: 0, showButton: true});
 * 
 * // 4. With redirect
 * showSuccessWithCountdown({title: 'Berhasil!', countdown: 3, redirectUrl: '/dashboard/'});
 * 
 * // 5. Custom icon & callback
 * showSuccessWithCountdown({title: 'Peringatan!', icon: 'warning', countdown: 5, callback: () => console.log('Done')});
 */
function showSuccessWithCountdown(titleOrOptions = 'Berhasil!', message = '', options = {}) {
    // Parse parameters (support both function signatures)
    let config;
    
    if (typeof titleOrOptions === 'object') {
        // New style: single options object
        config = titleOrOptions;
    } else {
        // Legacy style: (title, message, options)
        config = {
            title: titleOrOptions,
            message: message,
            ...options
        };
    }
    
    // Default configuration
    const defaults = {
        title: 'Berhasil!',
        message: '',
        icon: 'success',
        countdown: 5,
        showCountdown: null, // auto-detect based on countdown
        progressBar: null,   // auto-detect based on countdown
        showButton: null,    // auto-detect based on countdown
        buttonText: 'OK',
        username: '',
        fullName: '',
        userLabel: null,
        customHtml: '',
        callback: null,
        redirectUrl: '',
        allowOutsideClick: null // auto-detect based on countdown
    };
    
    // Merge config with defaults
    config = { ...defaults, ...config };
    
    // Auto-detect based on countdown
    if (config.showCountdown === null) {
        config.showCountdown = config.countdown > 0;
    }
    if (config.progressBar === null) {
        config.progressBar = config.countdown > 0;
    }
    if (config.showButton === null) {
        config.showButton = config.countdown === 0;
    }
    if (config.allowOutsideClick === null) {
        config.allowOutsideClick = config.countdown === 0;
    }
    
    // Build user display
    const displayName = config.fullName || config.username || '';
    const userHtml = displayName ? `
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-3">
            <i class="fas fa-user text-blue-600 mr-2"></i>
            ${config.userLabel ? `<span class="text-gray-600 text-sm mr-2">${config.userLabel}:</span>` : ''}
            <strong class="text-blue-800">${displayName}</strong>
        </div>
    ` : '';
    
    // Build countdown display
    const countdownHtml = config.showCountdown ? `
        <div class="mt-4 text-sm text-gray-500">
            <i class="fas fa-clock mr-2"></i>
            ${config.redirectUrl ? 'Redirect' : 'Menutup'} otomatis dalam <strong id="countdown-timer">${config.countdown}</strong> detik...
        </div>
    ` : '';
    
    // Build final HTML
    const html = `
        <div class="text-center">
            ${config.message ? `<p class="text-gray-700 mb-3">${config.message}</p>` : ''}
            ${userHtml}
            ${config.customHtml}
            ${countdownHtml}
        </div>
    `;
    
    let timerInterval;
    
    Swal.fire({
        icon: config.icon,
        title: config.title,
        html: html,
        timer: config.countdown > 0 ? config.countdown * 1000 : undefined,
        timerProgressBar: config.progressBar,
        showConfirmButton: config.showButton,
        confirmButtonText: config.buttonText,
        confirmButtonColor: '#3085d6',
        allowOutsideClick: config.allowOutsideClick,
        allowEscapeKey: config.allowOutsideClick,
        didOpen: () => {
            if (config.countdown > 0) {
                const countdownElement = document.getElementById('countdown-timer');
                let timeLeft = config.countdown;
                
                timerInterval = setInterval(() => {
                    timeLeft--;
                    if (countdownElement && timeLeft >= 0) {
                        countdownElement.textContent = timeLeft;
                    }
                }, 1000);
            }
        },
        willClose: () => {
            if (timerInterval) clearInterval(timerInterval);
        }
    }).then(() => {
        // Auto redirect if specified
        if (config.redirectUrl) {
            window.location.href = config.redirectUrl;
        }
        // Callback
        if (config.callback) config.callback();
    });
}

/**
 * Show confirm dialog
 * @param {string} title - Confirm title
 * @param {string} text - Confirm text
 * @param {function} confirmCallback - Callback if confirmed
 * @param {function} cancelCallback - Callback if cancelled
 */
function showConfirm(title, text, confirmCallback, cancelCallback = null) {
    Swal.fire({
        title: title,
        text: text,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Ya',
        cancelButtonText: 'Batal'
    }).then((result) => {
        if (result.isConfirmed && confirmCallback) {
            confirmCallback();
        } else if (result.isDismissed && cancelCallback) {
            cancelCallback();
        }
    });
}

// ==========================================
// GLOBAL PAGE/HTMX LOADING OVERLAY
// ==========================================

(function initGlobalLoadingOverlay(){
    try {
        if (window.__APLIKASI_TEST_GLOBAL_LOADING_INIT__) return;
        window.__APLIKASI_TEST_GLOBAL_LOADING_INIT__ = true;

        let pending = 0;
        let timer = null;
        let isOpen = false;

        function open(title, text) {
            if (!window.Swal) return;
            if (isOpen) return;
            isOpen = true;
            Swal.fire({
                title: title || 'Memuat Halaman...',
                html: text || 'Mohon tunggu sebentar...',
                allowOutsideClick: false,
                allowEscapeKey: false,
                backdrop: true,
                didOpen: function(){
                    try { Swal.showLoading(); } catch(_) {}
                }
            });
        }

        function close() {
            if (timer) { clearTimeout(timer); timer = null; }
            pending = Math.max(0, pending);
            if (!window.Swal) return;
            if (!isOpen) return;
            try { Swal.close(); } catch(_) {}
            isOpen = false;
        }

        function scheduleOpen(kind) {
            if (!window.Swal) return;
            if (timer || isOpen) return;
            timer = setTimeout(function(){
                timer = null;
                if (pending > 0 && !isOpen) {
                    const title = (kind === 'htmx') ? 'Memuat Data...' : 'Memuat Halaman...';
                    open(title, 'Mohon tunggu sebentar...');
                }
            }, 250);
        }

        function start(kind) {
            pending += 1;
            scheduleOpen(kind);
        }

        function stop() {
            pending = Math.max(0, pending - 1);
            if (pending === 0) close();
        }

        // Close any leftover loader on load (including bfcache)
        window.addEventListener('load', function(){ try { pending = 0; close(); } catch(_) {} });
        window.addEventListener('pageshow', function(){ try { pending = 0; close(); } catch(_) {} });

        // Full page navigation: intercept clicks and show loader
        document.addEventListener('click', function(e){
            try {
                const a = e.target && e.target.closest ? e.target.closest('a') : null;
                if (!a) return;
                const href = a.getAttribute('href');
                if (!href) return;
                if (href.startsWith('#')) return;
                if (a.hasAttribute('download')) return;
                // Skip loader for actions that open confirmations/modals or are handled via JS
                if (a.getAttribute('data-no-loader') === '1') return;
                if (a.closest && a.closest('[data-row-delete]')) return;
                const titleAttr = (a.getAttribute('title') || '').trim();
                if (titleAttr.toLowerCase().startsWith('delete')) return;
                // Common delete endpoints /.../delete or ?action=delete should not trigger page loader
                try {
                    const hrefLower = String(href).toLowerCase();
                    if (hrefLower.includes('/delete')) return;
                    if (hrefLower.includes('action=delete')) return;
                } catch (_) {}
                const target = a.getAttribute('target');
                if (target && target.toLowerCase() === '_blank') return;
                if (a.getAttribute('rel') && a.getAttribute('rel').toLowerCase().includes('external')) return;
                if (a.getAttribute('data-no-loader') === '1') return;
                if (a.hasAttribute('hx-get') || a.hasAttribute('hx-post') || a.hasAttribute('hx-boost')) return;
                if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
                start('page');
            } catch(_) {}
        }, true);

        // HTMX lifecycle
        document.body.addEventListener('htmx:beforeRequest', function(evt){
            try {
                // One-shot opt-out (for htmx.ajax callers)
                if (window.__APLIKASI_TEST_NO_LOADER_NEXT) {
                    window.__APLIKASI_TEST_NO_LOADER_NEXT = false;
                    return;
                }

                const hdrs = (
                    (evt && evt.detail && evt.detail.requestConfig && evt.detail.requestConfig.headers) ||
                    (evt && evt.detail && evt.detail.headers) ||
                    null
                );
                const noLoaderByHeader = hdrs && (hdrs['X-Aplikasi-Test-No-Loader'] === '1' || hdrs['x-aplikasi-test-no-loader'] === '1');
                if (noLoaderByHeader) return;

                const elt = evt && evt.detail && evt.detail.elt;
                try {
                    if (elt && elt.closest && elt.closest('[data-no-loader="1"]')) return;
                } catch(_){ }
            } catch(_) {}
            start('htmx');
        });
        document.body.addEventListener('htmx:afterRequest', function(){ stop(); });
        document.body.addEventListener('htmx:responseError', function(){ try { pending = 0; close(); } catch(_) {} });
        document.body.addEventListener('htmx:sendError', function(){ try { pending = 0; close(); } catch(_) {} });
        document.body.addEventListener('htmx:timeout', function(){ try { pending = 0; close(); } catch(_) {} });
    } catch(_) {}
})();

// ==========================================
// AJAX FORM SUBMIT (Reusable with SweetAlert)
// ==========================================

/**
 * Submit form via AJAX with SweetAlert (REUSABLE & FLEXIBLE!)
 * Perfect for login, save, delete, password change, etc.
 * 
 * @param {string} formId - ID of form
 * @param {object} options - Configuration options
 * @param {string} options.loadingTitle - Loading title (default: 'Memproses...')
 * @param {string} options.loadingText - Loading text (default: 'Mohon tunggu sebentar')
 * @param {string} options.successTitle - Success title (default: 'Berhasil!')
 * @param {string} options.successIcon - Success icon: success, warning, info (default: 'success')
 * @param {number} options.countdown - Countdown seconds (default: 5, set 0 to disable)
 * @param {boolean} options.showCountdown - Show countdown text (default: auto)
 * @param {boolean} options.progressBar - Show progress bar (default: auto)
 * @param {boolean} options.showButton - Show confirm button (default: auto)
 * @param {boolean} options.autoRedirect - Auto redirect on success (default: false)
 * @param {boolean} options.showUsername - Show username in success (default: auto-detect from response)
 * @param {string} options.userLabel - Custom label for username display
 * @param {function} options.onSuccess - Custom success callback
 * @param {function} options.onError - Custom error callback
 * 
 * USAGE EXAMPLES:
 * 
 * // 1. Simple (with countdown)
 * ajaxFormSubmitWithSwal('myForm', {successTitle: 'Data Tersimpan!', countdown: 3});
 * 
 * // 2. Without countdown
 * ajaxFormSubmitWithSwal('myForm', {countdown: 0, showButton: true});
 * 
 * // 3. Password change (with username auto-detect)
 * ajaxFormSubmitWithSwal('changePasswordForm', {successTitle: 'Password Berhasil Diganti!', autoRedirect: true});
 * 
 * // 4. Custom callback
 * ajaxFormSubmitWithSwal('myForm', {
 *     countdown: 5,
 *     onSuccess: (data) => console.log('Success:', data)
 * });
 */
function ajaxFormSubmitWithSwal(formId, options = {}) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    // Default options
    const config = {
        loadingTitle: options.loadingTitle || 'Memproses...',
        loadingText: options.loadingText || 'Mohon tunggu sebentar',
        successTitle: options.successTitle || 'Berhasil!',
        successIcon: options.successIcon || 'success',
        countdown: options.countdown !== undefined ? options.countdown : 5,
        showCountdown: options.showCountdown,
        progressBar: options.progressBar,
        showButton: options.showButton,
        autoRedirect: options.autoRedirect !== undefined ? options.autoRedirect : false,
        showUsername: options.showUsername !== undefined ? options.showUsername : null, // auto-detect
        userLabel: options.userLabel || null,
        onSuccess: options.onSuccess || null,
        onError: options.onError || null
    };
    
    let isSubmitting = false; // Prevent spam
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (isSubmitting) return;
        
        try {
            const uEl = form.querySelector('input[name="username"]');
            const pEl = form.querySelector('input[name="password"]');
            if (uEl && pEl) {
                const uVal = (uEl.value || '').trim();
                const pVal = (pEl.value || '').trim();
                if (!uVal || !pVal) {
                    showError('Gagal!', 'Username dan password harus diisi.');
                    return;
                }
            }
        } catch(_) {}
        
        isSubmitting = true;
        showLoading(config.loadingTitle, config.loadingText);
        
        const formData = new FormData(form);
        
        // AJAX request
        fetch(form.action || window.location.href, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(async (response) => {
            const contentType = (response.headers && response.headers.get && response.headers.get('content-type')) || '';
            let data;
            if (contentType.includes('application/json')) {
                data = await response.json();
            } else {
                const text = await response.text();
                const err = new Error('Non-JSON response');
                err.__nonJson = true;
                err.__status = response.status;
                err.__text = text;
                throw err;
            }
            return { response, data };
        })
        .then(({ response, data }) => {
            isSubmitting = false;

            const successFlag = !!(data && data.success);
            if (!response.ok && !successFlag) {
                const msg = (data && (data.message || data.error_message)) || `Request gagal (HTTP ${response.status})`;
                if (config.onError) {
                    config.onError(data);
                } else {
                    showError('Gagal!', msg);
                }
                return;
            }

            if (successFlag) {
                // Auto-detect if should show username
                const shouldShowUsername = config.showUsername !== null 
                    ? config.showUsername 
                    : !!(data.username || data.full_name);
                
                // Build redirect URL
                const redirectUrl = (config.autoRedirect && (data.redirect_url || data.redirect)) 
                    ? (data.redirect_url || data.redirect) 
                    : '';
                
                // Show success with countdown
                showSuccessWithCountdown({
                    title: config.successTitle,
                    message: data.message || '',
                    icon: config.successIcon,
                    countdown: config.countdown,
                    showCountdown: config.showCountdown,
                    progressBar: config.progressBar,
                    showButton: config.showButton,
                    username: shouldShowUsername ? data.username : '',
                    fullName: shouldShowUsername ? data.full_name : '',
                    userLabel: config.userLabel,
                    redirectUrl: redirectUrl,
                    callback: function() {
                        // Custom callback
                        if (config.onSuccess) config.onSuccess(data);
                    }
                });
            } else {
                // Error
                if (config.onError) {
                    config.onError(data);
                } else {
                    showError('Gagal!', (data && (data.message || data.error_message)) || 'Silakan coba lagi.');
                }
            }
        })
        .catch(error => {
            isSubmitting = false;
            try {
                if (error && error.__nonJson) {
                    const status = error.__status || '';
                    const raw = (error.__text || '').toString();
                    const trimmed = raw.length > 600 ? raw.slice(0, 600) + '...' : raw;
                    const safe = trimmed
                        .replace(/&/g, '&amp;')
                        .replace(/</g, '&lt;')
                        .replace(/>/g, '&gt;');
                    showError('Terjadi Kesalahan!', `Response server tidak valid (HTTP ${status}).<br><br><pre style="text-align:left; white-space:pre-wrap;">${safe}</pre>`);
                    return;
                }
            } catch (_) {}
            showError('Terjadi Kesalahan!', (error && error.message) ? error.message : 'Silakan coba lagi.');
        });
    });
}

/**
 * Legacy AJAX form submit (simple version, no SweetAlert)
 * @param {string} formId - ID of form
 * @param {function} successCallback - Callback on success
 * @param {function} errorCallback - Callback on error
 */
function ajaxFormSubmit(formId, successCallback, errorCallback) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    let isSubmitting = false; // Prevent spam submit
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Prevent spam - ignore if already submitting
        if (isSubmitting) {
            return;
        }
        
        isSubmitting = true;
        const formData = new FormData(form);
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalBtnText = submitBtn.innerHTML;
        
        // Show loading
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Memproses...';
        submitBtn.disabled = true;
        
        // AJAX request
        fetch(form.action || window.location.href, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            // Restore button
            submitBtn.innerHTML = originalBtnText;
            submitBtn.disabled = false;
            isSubmitting = false;
            
            if (data.success) {
                if (successCallback) successCallback(data);
            } else {
                if (errorCallback) errorCallback(data);
            }
        })
        .catch(error => {
            // Restore button
            submitBtn.innerHTML = originalBtnText;
            submitBtn.disabled = false;
            isSubmitting = false;
            
            if (errorCallback) {
                errorCallback({ success: false, message: 'Terjadi kesalahan. Silakan coba lagi.' });
            }
        });
    });
}

// ==========================================
// Reusable binder: SweetAlert for HTMX form events (NO TIMER)
// ==========================================
function bindFormSwal(container, options = {}) {
    const el = (typeof container === 'string') ? document.querySelector(container) : container;
    if (!el) return;
    if (el.__FORM_SWAL_BOUND__) return;
    el.__FORM_SWAL_BOUND__ = true;

    const successEvent = options.successEvent || 'form-success';
    const invalidEvent = options.invalidEvent || 'form-invalid';
    const allowOutsideClick = options.allowOutsideClick === undefined ? false : !!options.allowOutsideClick;
    const allowEscapeKey = options.allowEscapeKey === undefined ? false : !!options.allowEscapeKey;
    const confirmButtonText = options.confirmButtonText || 'OK';
    const scrollToTop = options.scrollToTop === undefined ? true : !!options.scrollToTop;
    const dedupeInvalid = options.dedupeInvalid === undefined ? true : !!options.dedupeInvalid;

    // Ensure global CSS is present to make error border visible and persistent even on focus
    try {
        if (!document.getElementById('swal-inline-error-styles')) {
            const st = document.createElement('style');
            st.id = 'swal-inline-error-styles';
            st.type = 'text/css';
            st.textContent = `
            .swal-error-input, .swal-error-input:focus, .swal-error-input:focus-visible {
                border-color: #ef4444 !important; /* red-500 */
                border-width: 2px !important;
                /* force Tailwind ring to red */
                --tw-ring-color: rgba(239,68,68,0.25) !important;
                --tw-ring-offset-shadow: 0 0 #0000 !important;
                --tw-ring-shadow: 0 0 0 3px rgba(239,68,68,0.25) !important;
                box-shadow: var(--tw-ring-offset-shadow), var(--tw-ring-shadow), var(--tw-shadow, 0 0 #0000) !important;
                outline: none !important;   /* avoid browser blue focus */
            }
            input[aria-invalid="true"], textarea[aria-invalid="true"], select[aria-invalid="true"] {
                border-color: #ef4444 !important;
                border-width: 2px !important;
                --tw-ring-color: rgba(239,68,68,0.25) !important;
                --tw-ring-offset-shadow: 0 0 #0000 !important;
                --tw-ring-shadow: 0 0 0 3px rgba(239,68,68,0.25) !important;
                box-shadow: var(--tw-ring-offset-shadow), var(--tw-ring-shadow), var(--tw-shadow, 0 0 #0000) !important;
                outline: none !important;
            }
            input[aria-invalid="true"]:focus, textarea[aria-invalid="true"]:focus, select[aria-invalid="true"]:focus,
            input[aria-invalid="true"]:focus-visible, textarea[aria-invalid="true"]:focus-visible, select[aria-invalid="true"]:focus-visible {
                border-color: #ef4444 !important;
                border-width: 2px !important;
                --tw-ring-color: rgba(239,68,68,0.25) !important;
                --tw-ring-offset-shadow: 0 0 #0000 !important;
                --tw-ring-shadow: 0 0 0 3px rgba(239,68,68,0.25) !important;
                box-shadow: var(--tw-ring-offset-shadow), var(--tw-ring-shadow), var(--tw-shadow, 0 0 #0000) !important;
                outline: none !important;
            }
            `;
            document.head && document.head.appendChild(st);
        }
    } catch(_) {}

    function topScroll() {
        if (scrollToTop) {
            try { window.scrollTo(0, 0); } catch(e) {}
            try { const mc = document.querySelector('.main-content'); if (mc) { if (mc.scrollTo) mc.scrollTo(0, 0); else mc.scrollTop = 0; } } catch(e) {}
        }
    }

    function focusFirstInvalidField(rootEl, fieldErrors) {
        try {
            const root = rootEl || el;
            let target = null;
            if (fieldErrors && typeof fieldErrors === 'object') {
                for (const k of Object.keys(fieldErrors)) {
                    target = root.querySelector('[name="'+CSS.escape(k)+'"]');
                    if (target) break;
                }
            }
            if (!target) target = root.querySelector('.swal-error-input');
            if (target && target.focus) {
                try { target.focus({ preventScroll: true }); } catch(_) { try { target.focus(); } catch(_) {} }
                try { if (target.select) target.select(); } catch(_) {}
            }
        } catch(_) {}
    }

    function clearInlineErrors(rootEl) {
        const root = rootEl || el;
        try {
            const prev = root.querySelectorAll('[data-inline-error], .swal-error-msg');
            prev.forEach(function(n){ n.remove(); });
            const errInputs = root.querySelectorAll('.swal-error-input');
            errInputs.forEach(function(inp){
                try { inp.removeAttribute('aria-invalid'); } catch(_) {}
                inp.classList.remove('swal-error-input','border-red-500','border-red-600','focus:border-red-500','focus:ring-red-200','text-red-600','placeholder-red-400','ring-red-200','ring-1','ring-2','ring-red-400','ring-red-500','ring-inset');
                // restore any Tailwind ring/focus classes we removed while invalid
                try {
                    if (inp.dataset && inp.dataset.swalRemovedClasses) {
                        inp.dataset.swalRemovedClasses.split(' ').forEach(function(c){ if (c) { try { inp.classList.add(c); } catch(_) {} } });
                        delete inp.dataset.swalRemovedClasses;
                    }
                } catch(_) {}
                try { if (inp.dataset && inp.dataset.swalHadBorder2 === '0') { inp.classList.remove('border-2'); } } catch(_) {}
                try { if (inp.dataset) { delete inp.dataset.swalHadBorder2; } } catch(_) {}
                try {
                    if (inp && inp.style) {
                        inp.style.color = '';
                        inp.style.removeProperty('border');
                        inp.style.removeProperty('border-color');
                        inp.style.removeProperty('border-width');
                        inp.style.removeProperty('box-shadow');
                        inp.style.removeProperty('outline');
                        inp.style.removeProperty('outline-offset');
                    }
                } catch(_) {}
            });
        } catch(_) {}
    }

    // Remove inline errors only for fields that are now valid (i.e., NOT present in new fieldErrors)
    function syncInlineErrorsTo(fieldErrors, rootEl) {
        const root = rootEl || el;
        try {
            const names = new Set(Object.keys(fieldErrors || {}));
            // Remove messages for fields not in names
            root.querySelectorAll('[data-inline-error]')
                .forEach(function(msg){
                    const key = msg.getAttribute('data-inline-error') || '';
                    if (!names.has(key)) { try { msg.remove(); } catch(_) {} }
                });
            // Remove error styles for inputs not in names
            root.querySelectorAll('.swal-error-input')
                .forEach(function(inp){
                    const key = inp.getAttribute('name');
                    if (!names.has(key)) {
                        try { inp.removeAttribute('aria-invalid'); } catch(_) {}
                        inp.classList.remove('swal-error-input','border-red-500','border-red-600','focus:border-red-500','focus:ring-red-200','text-red-600','placeholder-red-400','ring-red-200','ring-1','ring-2','ring-red-400','ring-red-500','ring-inset');
                        try {
                            if (inp.dataset && inp.dataset.swalRemovedClasses) {
                                inp.dataset.swalRemovedClasses.split(' ').forEach(function(c){ if (c) { try { inp.classList.add(c); } catch(_) {} } });
                                delete inp.dataset.swalRemovedClasses;
                            }
                        } catch(_) {}
                        try { if (inp.dataset && inp.dataset.swalHadBorder2 === '0') { inp.classList.remove('border-2'); } } catch(_) {}
                        try { if (inp.dataset) { delete inp.dataset.swalHadBorder2; } } catch(_) {}
                        try {
                            if (inp && inp.style) {
                                inp.style.color = '';
                                inp.style.removeProperty('border');
                                inp.style.removeProperty('border-color');
                                inp.style.removeProperty('border-width');
                                inp.style.removeProperty('box-shadow');
                                inp.style.removeProperty('outline');
                                inp.style.removeProperty('outline-offset');
                            }
                        } catch(_) {}
                    }
                });
        } catch(_) {}
    }

    // Show/refresh a red alert box with summary errors at the top of the form
    function updateErrorBox(rootEl, errs) {
        try {
            const root = rootEl || el;
            const form = root.querySelector('form');
            if (!form) return;
            let box = root.querySelector('[data-inline-errors-box]');
            if (!errs || !Array.isArray(errs) || errs.length === 0) {
                if (box) box.remove();
                return;
            }
            if (!box) {
                box = document.createElement('div');
                box.setAttribute('data-inline-errors-box','');
                box.className = 'bg-red-50 border border-red-200 rounded-lg p-4 mb-6';
                form.insertBefore(box, form.firstChild);
            }
            const inner = [
                '<div class="text-red-700 font-medium mb-2"><i class="fas fa-exclamation-circle mr-1"></i> Periksa kembali input Anda.</div>',
                '<ul class="list-disc list-inside text-red-700">',
                errs.map(function(x){ return '<li>'+String(x)+'</li>'; }).join(''),
                '</ul>'
            ].join('');
            box.innerHTML = inner;
        } catch(_) {}
    }

    function applyInlineErrors(fieldErrors, rootEl) {
        const root = rootEl || el;
        if (!fieldErrors || typeof fieldErrors !== 'object') return;
        try {
            Object.keys(fieldErrors).forEach(function(name){
                const msgs = Array.isArray(fieldErrors[name]) ? fieldErrors[name] : [String(fieldErrors[name] || '')];
                const field = root.querySelector('[name="'+CSS.escape(name)+'"]');
                if (!field) return;
                try { field.setAttribute('aria-invalid','true'); } catch(_) {}
                var hadBorder2 = false;
                try { hadBorder2 = field.classList.contains('border-2'); } catch(_) {}
                try { field.dataset.swalHadBorder2 = hadBorder2 ? '1' : '0'; } catch(_) {}
                field.classList.add('swal-error-input','border-2','border-red-500','focus:border-red-500');
                // remove Tailwind ring/focus classes that might override our red border
                try {
                    var removed = [];
                    Array.from(field.classList).forEach(function(c){
                        if (c && (c.startsWith('focus:ring') || c.startsWith('ring-') || c.startsWith('focus:border'))) {
                            removed.push(c);
                        }
                    });
                    removed.forEach(function(c){ try { field.classList.remove(c); } catch(_) {} });
                    if (field.dataset) field.dataset.swalRemovedClasses = removed.join(' ');
                } catch(_) {}
                try {
                    if (field && field.style) {
                        field.style.setProperty('border', '2px solid #ef4444', 'important');
                        field.style.setProperty('border-color', '#ef4444', 'important');
                        field.style.setProperty('border-width', '2px', 'important');
                        field.style.removeProperty('box-shadow');
                        field.style.removeProperty('outline');
                        field.style.removeProperty('outline-offset');
                    }
                } catch(_) {}
                const htmlMsg = msgs.map(function(m){return String(m);}).join('<br>');
                let next = null;
                try { next = field.nextElementSibling; } catch(_) {}
                if (next && (next.hasAttribute && next.hasAttribute('data-inline-error'))) {
                    next.innerHTML = htmlMsg;
                    return;
                }
                // do not overwrite template-provided error blocks with similar color classes
                const msgEl = document.createElement('p');
                msgEl.setAttribute('data-inline-error', name);
                msgEl.className = 'swal-error-msg text-red-600 text-sm mt-1';
                msgEl.innerHTML = htmlMsg;
                if (field.parentNode) {
                    field.parentNode.insertBefore(msgEl, field.nextSibling);
                }
                // keep error state while typing; we only clear on next HTMX event (success/invalid)
            });
        } catch(_) {}
    }

    function onInvalid(e) {
        try {
            e.stopImmediatePropagation();
            e.stopPropagation();
            const d = e.detail || {};
            const errs = d.errors || [];
            const fieldErrors = d.fieldErrors || d.field_errors || null;
            let sig = '';
            try { if (Array.isArray(errs)) { sig = JSON.stringify(errs.map(function(x){return String(x)}).sort()); } else if (errs && typeof errs === 'object') { sig = JSON.stringify(errs); } else { sig = String(errs || ''); } } catch(_) { sig = String(errs || ''); }
            if (dedupeInvalid && el.__lastInvalidSig === sig) { return; }
            el.__lastInvalidSig = sig;
            topScroll();
            var scope = (function(){
                try {
                    if (typeof container === 'string') {
                        return document.querySelector(container) || e.target || el;
                    }
                    return e.target || el;
                } catch(_) { return e.target || el; }
            })();
            syncInlineErrorsTo(fieldErrors, scope);
            applyInlineErrors(fieldErrors, scope);
            updateErrorBox(scope, errs);
            if (window.Swal) {
                try { if (document.activeElement) document.activeElement.blur(); } catch(_) {}
                Swal.fire({
                    icon: 'error',
                    title: 'Periksa kembali input Anda',
                    html: '<ul style="text-align:left;margin-left:1rem">' + errs.map(function(x){return '<li>'+x+'</li>';}).join('') + '</ul>',
                    allowOutsideClick,
                    allowEscapeKey,
                    confirmButtonText,
                    focusConfirm: true,
                    returnFocus: false,
                    didOpen: () => { try { topScroll(); } catch(_) {} },
                    willClose: () => {
                        topScroll();
                        try { if (document.activeElement) document.activeElement.blur(); } catch(_) {}
                    }
                }).then(function(){
                    topScroll();
                    try { setTimeout(topScroll, 0); } catch(_) {}
                    try { setTimeout(topScroll, 120); } catch(_) {}
                    try { setTimeout(topScroll, 300); } catch(_) {}
                });
            } else {
                topScroll();
            }
        } catch(err) {}
    }

    function onSuccess(e) {
        try {
            e.stopImmediatePropagation();
            e.stopPropagation();
            const d = e.detail || {};
            const msg = d.message || 'Berhasil';
            const url = d.redirect;
            el.__lastInvalidSig = undefined;
            topScroll();
            var scope = (function(){
                try {
                    if (typeof container === 'string') {
                        return document.querySelector(container) || e.target || el;
                    }
                    return e.target || el;
                } catch(_) { return e.target || el; }
            })();
            clearInlineErrors(scope);
            updateErrorBox(scope, []);
            if (window.Swal) {
                Swal.fire({
                    icon: 'success',
                    title: 'Berhasil',
                    text: msg,
                    allowOutsideClick,
                    allowEscapeKey,
                    confirmButtonText,
                    focusConfirm: true
                }).then(function(){ if (url) window.location = url; });
            } else if (url) {
                window.location = url;
            }
            if (typeof options.onSuccess === 'function') options.onSuccess(d);
        } catch(err) {}
    }

    // Capture-phase listeners to win over other handlers
    el.addEventListener(invalidEvent, onInvalid, true);
    el.addEventListener(successEvent, onSuccess, true);
    // Also guard generic events if they bubble through this container
    el.addEventListener('form-invalid', onInvalid, true);
    el.addEventListener('form-success', onSuccess, true);
    // Attach document-level listeners for the specific unique events (once per event name)
    try {
        if (!document.__FORM_SWAL_DOC_BOUND__) document.__FORM_SWAL_DOC_BOUND__ = {};
        if (invalidEvent && !document.__FORM_SWAL_DOC_BOUND__['invalid:'+invalidEvent]) {
            document.__FORM_SWAL_DOC_BOUND__['invalid:'+invalidEvent] = true;
            document.addEventListener(invalidEvent, onInvalid, true);
        }
        if (successEvent && !document.__FORM_SWAL_DOC_BOUND__['success:'+successEvent]) {
            document.__FORM_SWAL_DOC_BOUND__['success:'+successEvent] = true;
            document.addEventListener(successEvent, onSuccess, true);
        }
        // Also guard generic events globally so body hx-on does not double-handle on pages that use bindFormSwal
        if (!document.__FORM_SWAL_DOC_BOUND__['invalid:form-invalid']) {
            document.__FORM_SWAL_DOC_BOUND__['invalid:form-invalid'] = true;
            document.addEventListener('form-invalid', onInvalid, true);
        }
        if (!document.__FORM_SWAL_DOC_BOUND__['success:form-success']) {
            document.__FORM_SWAL_DOC_BOUND__['success:form-success'] = true;
            document.addEventListener('form-success', onSuccess, true);
        }
    } catch(e) {}
    // Re-bind after HTMX swaps: ensure newly swapped container gets listeners
    try {
        if (!window.__FORM_SWAL_REBINDERS__) window.__FORM_SWAL_REBINDERS__ = {};
        const key = (typeof container === 'string') ? String(container) : (el && el.id ? ('#' + el.id) : 'container');
        if (!window.__FORM_SWAL_REBINDERS__[key]) {
            window.__FORM_SWAL_REBINDERS__[key] = true;
            document.addEventListener('htmx:afterSwap', function(){
                try {
                    const target = (typeof container === 'string') ? document.querySelector(container) : (el && el.id ? document.getElementById(el.id) : null);
                    if (target && !target.__FORM_SWAL_BOUND__) {
                        bindFormSwal(target, options);
                    }
                } catch(e) {}
            });
        }
    } catch(e) {}
}

// ==========================================
// SEARCHABLE SELECT (no jQuery, local only)
// - Global reusable enhancer with opt-out & threshold
// ==========================================
function cleanupSelectWrappers(root){
    try {
        const r = root && root.querySelectorAll ? root : document;
        // Remove duplicate wrappers (keep first per form + key)
        const seen = {};
        Array.from(r.querySelectorAll('[data-select-enhanced-wrapper]')).forEach(function(w){
            try {
                const key = (w.getAttribute('data-enhanced-for') || '').trim();
                if (!key) return;
                const fm = w.closest('form');
                const scopeId = (fm && (fm.getAttribute('id') || fm.action || 'form')) || 'doc';
                const gk = scopeId + '::' + key;
                if (seen[gk]) { w.remove(); }
                else { seen[gk] = w; }
            } catch(_){}
        });
        // Remove orphan wrappers without a select (can happen after swaps)
        Array.from(r.querySelectorAll('[data-select-enhanced-wrapper]')).forEach(function(w){
            try { if (!w.querySelector('select')) w.remove(); } catch(_){}
        });
    } catch(_) {}
}
function initSearchableSelect(root, config) {
    const scope = root && root.querySelectorAll ? root : document;
    const cfg = Object.assign({ threshold: 6, placeholder: 'Cari...', optOutClass: 'no-search', flagAttr: 'data-select-search' }, (config || {}));
    // Pre-clean duplicates in the scope
    cleanupSelectWrappers(scope);
    const selects = scope.querySelectorAll('select');
    selects.forEach(function(sel){
        if (!sel) return;
        // Skip if already enhanced (flag) or if it's already wrapped
        if (sel.dataset.selectEnhanced === '1') return;
        try { if (sel.closest('[data-select-enhanced-wrapper]')) return; } catch(_) {}
        // opt-out
        try { if (sel.classList.contains(cfg.optOutClass)) return; } catch(_){ }
        const flag = (sel.getAttribute(cfg.flagAttr) || '').toLowerCase();
        const forceOn = sel.classList.contains('js-select-search') || flag === 'on' || flag === 'true' || flag === '1';
        const forceOff = flag === 'off' || flag === 'false' || flag === '0';
        const th = parseInt(sel.getAttribute('data-search-threshold') || cfg.threshold, 10) || cfg.threshold;
        const enoughOptions = (sel.options ? sel.options.length : 0) >= th;
        if (!forceOn && (forceOff || !enoughOptions)) return;
        sel.dataset.selectEnhanced = '1';

        // Clean up any previous enhanced wrapper in the same container to avoid duplicates
        try {
            const host = sel.parentNode;
            Array.from(host ? host.children : []).forEach(function(ch){
                if (ch !== sel && ch.getAttribute && ch.hasAttribute('data-select-enhanced-wrapper')) {
                    try { ch.remove(); } catch(_) {}
                }
            });
        } catch(_) {}

        // If a sibling wrapper already exists (race condition), skip enhancing again
        try {
            const host2 = sel.parentNode;
            if (host2 && Array.from(host2.children).some(function(ch){ return ch !== sel && ch.getAttribute && ch.hasAttribute('data-select-enhanced-wrapper'); })) {
                return;
            }
        } catch(_) {}

        const wrapper = document.createElement('div');
        wrapper.className = 'relative w-full';
        wrapper.setAttribute('data-select-enhanced-wrapper','');
        try { if (sel.id) wrapper.setAttribute('data-enhanced-for', sel.id); else if (sel.name) wrapper.setAttribute('data-enhanced-for', sel.name); } catch(_) {}
        sel.parentNode.insertBefore(wrapper, sel);
        wrapper.appendChild(sel);

        // Remove any other wrappers for the same select in this field container
        try {
            const container = wrapper.parentNode;
            const key = (sel.id || sel.name || '').toString();
            if (container && key) {
                const dups = Array.from(container.querySelectorAll('[data-select-enhanced-wrapper]'))
                    .filter(function(w){ return w !== wrapper && (w.getAttribute('data-enhanced-for') === key); });
                dups.forEach(function(w){ try { w.remove(); } catch(_) {} });
            }
        } catch(_) {}

        // Robustly hide the native select to avoid visual duplicates (padding/border)
        // Keep it in the DOM so form submission still works
        sel.style.display = 'none';
        sel.style.position = 'absolute';
        sel.style.left = '-9999px';
        sel.style.width = '0';
        sel.style.height = '0';
        sel.style.margin = '0';
        sel.style.padding = '0';
        sel.style.border = '0';
        sel.style.pointerEvents = 'none';
        sel.tabIndex = -1;
        try { sel.setAttribute('aria-hidden', 'true'); } catch(_) {}

        const isMultiple = !!sel.multiple;

        function selectedText() {
            if (sel.disabled) {
                const dl = sel.getAttribute('data-disabled-label');
                if (dl) return dl;
            }
            if (isMultiple) return '';
            const opt = sel.options[sel.selectedIndex] || sel.options[0];
            return opt ? opt.text : '';
        }

        const display = document.createElement('div');
        const baseDisplay = 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 bg-white text-gray-800 flex items-center justify-between';
        display.className = baseDisplay + (sel.disabled ? ' cursor-not-allowed' : ' cursor-pointer');
        let labelSpan = null;
        let chipsWrap = null;
        let chipsPlaceholder = null;
        if (isMultiple) {
            chipsWrap = document.createElement('div');
            chipsWrap.className = 'flex flex-wrap gap-2 items-center min-w-0 flex-1';
            chipsPlaceholder = document.createElement('span');
            chipsPlaceholder.className = 'text-gray-500 truncate';
            chipsPlaceholder.textContent = sel.getAttribute('data-multi-placeholder') || (sel.options[0] ? sel.options[0].text : 'Pilih...');
            chipsWrap.appendChild(chipsPlaceholder);
        } else {
            labelSpan = document.createElement('span');
            labelSpan.className = 'truncate';
            labelSpan.textContent = selectedText();
        }
        const caret = document.createElement('i');
        caret.className = 'fas fa-chevron-down text-gray-400';

        const clearBtn = document.createElement('button');
        clearBtn.type = 'button';
        clearBtn.className = 'text-gray-400 hover:text-gray-700 px-1';
        clearBtn.textContent = '×';
        clearBtn.setAttribute('aria-label', 'Clear');

        const rightWrap = document.createElement('div');
        rightWrap.className = 'flex items-center gap-2 ml-3';
        rightWrap.appendChild(clearBtn);
        rightWrap.appendChild(caret);

        if (chipsWrap) display.appendChild(chipsWrap);
        if (labelSpan) display.appendChild(labelSpan);
        display.appendChild(rightWrap);

        const dropdown = document.createElement('div');
        dropdown.className = 'fixed bg-white border border-gray-200 rounded-lg shadow-lg hidden';
        try { dropdown.style.zIndex = '10050'; } catch(_) {}
        const search = document.createElement('input');
        search.type = 'text';
        search.className = 'w-full px-3 py-2 border-b border-gray-200 outline-none';
        search.placeholder = sel.getAttribute('data-search-placeholder') || cfg.placeholder;
        const list = document.createElement('ul');
        list.className = 'py-1';

        function applyDropdownScrollMode() {
            const noScroll = !!sel.getAttribute('data-dropdown-no-scroll');
            try {
                if (!noScroll) {
                    const miRaw = (sel.getAttribute('data-dropdown-max-items') || '').trim();
                    const mi = parseInt(miRaw, 10);
                    const h = (sel.getAttribute('data-dropdown-max-height') || '').trim();
                    if (!isNaN(mi) && mi > 0) {
                        // Approximate list row height. Our li uses `py-2` which is 0.5rem top+bottom.
                        // 2.5rem per row gives a good visual fit across browsers.
                        list.style.maxHeight = (mi * 2.5) + 'rem';
                    } else if (h) {
                        list.style.maxHeight = h; // accept values like '16rem', '320px', '60vh'
                    } else {
                        list.style.maxHeight = '16rem'; // default ~256px
                    }
                    list.style.overflow = '';
                    list.style.overflowY = 'auto';
                } else {
                    // Force no scrollbar
                    list.style.maxHeight = '';
                    list.style.overflow = 'hidden';
                    list.style.overflowY = 'hidden';
                }
            } catch(_) {
                if (!noScroll) {
                    list.style.maxHeight = '16rem';
                    list.style.overflow = '';
                    list.style.overflowY = 'auto';
                } else {
                    list.style.maxHeight = '';
                    list.style.overflow = 'hidden';
                    list.style.overflowY = 'hidden';
                }
            }
        }

        // Initial apply
        applyDropdownScrollMode();
        dropdown.appendChild(search);
        dropdown.appendChild(list);

        // Portal dropdown to body to avoid clipping inside overflow containers (e.g., modals)
        try { document.body.appendChild(dropdown); } catch(_){ }

        // Remote search config (optional)
        let remoteUrl = sel.getAttribute('data-search-url');
        const minChars = parseInt(sel.getAttribute('data-min-chars') || '2', 10);
        function getPageSize(){
            try {
                const v = parseInt(sel.getAttribute('data-page-size') || '50', 10);
                return (isNaN(v) || v <= 0) ? 50 : v;
            } catch(_) { return 50; }
        }
        let rQuery = '';
        let rPage = 1;
        let rHasMore = false;
        let rLoading = false;
        let rAbort = null;

        function ensureOption(val, label, selectByDefault){
            let opt = Array.from(sel.options).find(function(o){ return String(o.value) === String(val); });
            if (!opt) {
                const selByDef = (selectByDefault === true);
                opt = new Option(label, val, false, selByDef);
                sel.add(opt);
            } else {
                opt.text = label;
            }
        }

        function isSelectedValue(val){
            try {
                return Array.from(sel.options).some(function(o){ return o && o.selected && String(o.value) === String(val); });
            } catch(_) { return false; }
        }

        function setSelectedValue(val, selected){
            try {
                const opt = Array.from(sel.options).find(function(o){ return String(o.value) === String(val); });
                if (opt) opt.selected = !!selected;
            } catch(_) {}
        }

        function showInfoRow(text){
            const li = document.createElement('li');
            li.className = 'px-3 py-2 text-gray-500 text-sm';
            li.textContent = text;
            li.dataset.info = '1';
            list.appendChild(li);
            return li;
        }

        function clearInfoRows(){
            Array.from(list.querySelectorAll('li[data-info="1"]')).forEach(function(n){ n.remove(); });
        }

        function renderResults(results, append){
            if (!append) list.innerHTML = '';
            results.forEach(function(item){
                const li = document.createElement('li');
                li.className = 'px-3 py-2 cursor-pointer hover:bg-gray-100';
                li.textContent = item.label || item.text || '';
                li.dataset.value = String(item.value);
                if (isMultiple && isSelectedValue(li.dataset.value)) {
                    li.classList.add('bg-gray-200');
                }
                li.addEventListener('click', function(){ choose(li.dataset.value, li.textContent); });
                list.appendChild(li);
            });
        }

        async function fetchPage(query, page, append){
            if (!remoteUrl || rLoading) return;
            rLoading = true;
            clearInfoRows();
            const loadingRow = showInfoRow('Memuat...');
            try {
                if (rAbort) { try { rAbort.abort(); } catch(_){} }
                rAbort = new AbortController();
                const u = new URL(remoteUrl, window.location.origin);
                u.searchParams.set('q', query || '');
                u.searchParams.set('page', String(page || 1));
                const ps = getPageSize();
                u.searchParams.set('page_size', String(ps));
                const resp = await fetch(u.toString(), { signal: rAbort.signal, headers: { 'X-Requested-With': 'XMLHttpRequest' } });
                const data = await resp.json();
                let results = Array.isArray(data) ? data : (data.results || []);
                // Enforce client-side cap even if server returns more
                try { results = results.slice(0, ps); } catch(_) {}
                rHasMore = !!(Array.isArray(data) ? (results.length >= ps) : data.has_more);
                renderResults(results, !!append);
                // Hard guard: never show more than configured limit in UI
                try {
                    const lis = Array.from(list.querySelectorAll('li[data-value]'));
                    if (lis.length > ps) {
                        lis.slice(ps).forEach(function(n){ try { n.remove(); } catch(_) {} });
                    }
                } catch(_) {}
                if (!results.length) showInfoRow('Tidak ada data');
            } catch(err) {
                if (err && err.name === 'AbortError') {
                    // ignore
                } else {
                    showInfoRow('Gagal memuat');
                }
            } finally {
                try { loadingRow && loadingRow.remove(); } catch(_){}
                rLoading = false;
            }
        }

        wrapper.appendChild(display);

        function syncDisabled(){
            const baseDisplay = 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 bg-white text-gray-800 flex items-center justify-between';
            display.className = baseDisplay + (sel.disabled ? ' cursor-not-allowed' : ' cursor-pointer');
            if (sel.disabled) close();
            try {
                if (labelSpan) labelSpan.textContent = selectedText();
                if (isMultiple) renderChips();
            } catch(_){ }
        }

        function getSelectedOptions(){
            try {
                return Array.from(sel.options).filter(function(o){ return !!o.selected && String(o.value || '') !== ''; });
            } catch(_) { return []; }
        }

        function hasAnyValue(){
            try {
                if (sel.disabled) return false;
                if (isMultiple) return getSelectedOptions().length > 0;
                const v = (sel.value == null) ? '' : String(sel.value);
                return v !== '';
            } catch(_) { return false; }
        }

        function updateClearVisibility(){
            try {
                clearBtn.style.display = hasAnyValue() ? '' : 'none';
            } catch(_) {}
        }

        function renderChips(){
            if (!isMultiple || !chipsWrap) return;
            // Clear chips but keep placeholder node instance (we'll re-add)
            try { chipsWrap.innerHTML = ''; } catch(_) {}
            const selectedOpts = getSelectedOptions();
            if (sel.disabled) {
                const dl = sel.getAttribute('data-disabled-label');
                const sp = document.createElement('span');
                sp.className = 'text-gray-500 truncate';
                sp.textContent = dl || (sel.getAttribute('data-multi-placeholder') || '');
                chipsWrap.appendChild(sp);
                return;
            }
            if (!selectedOpts.length) {
                const sp = document.createElement('span');
                sp.className = 'text-gray-500 truncate';
                sp.textContent = sel.getAttribute('data-multi-placeholder') || (sel.options[0] ? sel.options[0].text : 'Pilih...');
                chipsWrap.appendChild(sp);
                return;
            }
            selectedOpts.forEach(function(opt){
                const chip = document.createElement('span');
                chip.className = 'inline-flex items-center gap-2 px-2 py-1 rounded-md bg-gray-200 text-gray-800 text-sm max-w-full';
                const tx = document.createElement('span');
                tx.className = 'truncate';
                tx.textContent = opt.text || '';
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'text-gray-500 hover:text-gray-700';
                btn.textContent = '×';
                btn.addEventListener('click', function(e){
                    try { e.preventDefault(); e.stopPropagation(); } catch(_) {}
                    try { opt.selected = false; } catch(_) {}
                    try { sel.dispatchEvent(new Event('change', {bubbles:true})); } catch(_) {}
                    try {
                        // If dropdown open, reflect unselected state visually
                        const active = Array.from(list.children).find(function(li){ return li.dataset.value === String(opt.value); });
                        if (active) active.classList.remove('bg-gray-200');
                    } catch(_) {}
                    renderChips();
                });
                chip.appendChild(tx);
                chip.appendChild(btn);
                chipsWrap.appendChild(chip);
            });
            updateClearVisibility();
        }

        const items = [];
        if (!remoteUrl) {
            Array.from(sel.options).forEach(function(opt){
                const li = document.createElement('li');
                li.className = 'px-3 py-2 cursor-pointer hover:bg-gray-100';
                li.textContent = opt.text;
                li.dataset.value = opt.value;
                if (!isMultiple && sel.value === opt.value) li.classList.add('bg-gray-200');
                if (isMultiple && opt.selected) li.classList.add('bg-gray-200');
                li.addEventListener('click', function(){ choose(opt.value, opt.text); });
                items.push({el: li, text: (opt.text || '').toLowerCase()});
                list.appendChild(li);
            });
        }

        function positionDropdown(){
            try {
                const rect = display.getBoundingClientRect();
                dropdown.style.left = rect.left + 'px';
                dropdown.style.top = rect.bottom + 'px';
                dropdown.style.width = rect.width + 'px';
                dropdown.style.maxWidth = rect.width + 'px';
            } catch(_){ }
        }

        function onViewportChange(e){
            try {
                // We intentionally listen to scroll on capture to close on page scroll,
                // but ignore scroll events that originate from inside the dropdown itself
                // (so the user can scroll the options list).
                if (e && e.target && dropdown && dropdown.contains(e.target)) return;
            } catch(_){ }
            close();
        }

        function open() {
            // Re-apply on open (attributes may be set after initial enhancement)
            applyDropdownScrollMode();
            // Re-read remoteUrl to ensure dynamic attributes applied (e.g. via HTMX)
            remoteUrl = sel.getAttribute('data-search-url');
            if (remoteUrl) {
                // Force remote mode: never show local options
                try { list.innerHTML = ''; } catch(_) {}
                try { items.length = 0; } catch(_) {}
                try { clearInfoRows(); } catch(_) {}
                // If initial fetch is enabled, do not show "type minimum" hint.
                // fetchPage() will show "Memuat..." and then results.
                if (!sel.getAttribute('data-initial-fetch') && (minChars || 0) > 0) {
                    showInfoRow(`Ketik minimal ${minChars} huruf...`);
                }
            }
            positionDropdown();
            dropdown.classList.remove('hidden');
            try { search.focus(); } catch(_) {}
            if (remoteUrl && !list.querySelector('li')) {
                // initial fetch to show first page without typing if allowed
                if (sel.getAttribute('data-initial-fetch')) {
                    rQuery = '';
                    rPage = 1;
                    fetchPage(rQuery, rPage, false);
                } else {
                    showInfoRow(`Ketik minimal ${minChars} huruf...`);
                }
            }
            document.addEventListener('click', onDoc, true);
            window.addEventListener('scroll', onViewportChange, true);
            window.addEventListener('resize', onViewportChange, true);
        }
        function close() {
            dropdown.classList.add('hidden');
            document.removeEventListener('click', onDoc, true);
            window.removeEventListener('scroll', onViewportChange, true);
            window.removeEventListener('resize', onViewportChange, true);
        }
        function toggle() { if (sel.disabled) return; dropdown.classList.contains('hidden') ? open() : close(); }
        function onDoc(e){ if (!wrapper.contains(e.target) && !dropdown.contains(e.target)) close(); }

        function choose(val, label) {
            if (isMultiple) {
                // Compute toggle state before ensureOption(), because remote ensureOption()
                // can create and/or preselect an option.
                const next = !isSelectedValue(val);
                if (remoteUrl) { ensureOption(val, label || '', false); }
                setSelectedValue(val, next);
                sel.dispatchEvent(new Event('change', {bubbles:true}));
                const active = Array.from(list.children).find(function(li){ return li.dataset.value === String(val); });
                if (active) {
                    if (next) active.classList.add('bg-gray-200');
                    else active.classList.remove('bg-gray-200');
                }
                updateClearVisibility();
                return;
            }
            if (sel.value !== val) {
                if (remoteUrl) { ensureOption(val, label || '', true); }
                sel.value = val;
                sel.dispatchEvent(new Event('change', {bubbles:true}));
            }
            labelSpan.textContent = selectedText();
            Array.from(list.children).forEach(function(li){ li.classList.remove('bg-gray-200'); });
            const active = Array.from(list.children).find(function(li){ return li.dataset.value === val; });
            if (active) active.classList.add('bg-gray-200');
            updateClearVisibility();
            close();
        }

        function filter(q) {
            remoteUrl = sel.getAttribute('data-search-url');
            if (remoteUrl) {
                const qv = (q || '').trim();
                rQuery = qv;
                rPage = 1;
                list.innerHTML = '';
                if (qv.length < minChars && !sel.getAttribute('data-initial-fetch')) {
                    showInfoRow(`Ketik minimal ${minChars} huruf...`);
                    return;
                }
                fetchPage(qv, rPage, false);
                return;
            }
            const s = (q || '').toLowerCase();
            items.forEach(function(it){
                const show = !s || it.text.indexOf(s) !== -1;
                it.el.style.display = show ? '' : 'none';
            });
        }

        display.addEventListener('click', function(){ toggle(); });
        display.addEventListener('keydown', function(e){ if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle(); } });

        clearBtn.addEventListener('click', function(e){
            try { e.preventDefault(); e.stopPropagation(); } catch(_) {}
            try {
                if (sel.disabled) return;
                if (isMultiple) {
                    Array.from(sel.options || []).forEach(function(o){ try { o.selected = false; } catch(_) {} });
                } else {
                    sel.value = '';
                }
                sel.dispatchEvent(new Event('change', {bubbles:true}));
                try {
                    Array.from(list.children).forEach(function(li){ li.classList.remove('bg-gray-200'); });
                } catch(_) {}
                updateClearVisibility();
            } catch(_) {}
        });
        const debFilter = debounce(function(){ filter(search.value); }, 200);
        search.addEventListener('input', function(){ debFilter(); });
        search.addEventListener('keydown', function(e){ if (e.key === 'Escape') { e.preventDefault(); close(); display.focus && display.focus(); }});

        // Keyboard navigation
        let idx = -1;
        search.addEventListener('keydown', function(e){
            const visible = remoteUrl 
                ? Array.from(list.querySelectorAll('li[data-value]'))
                : Array.from(items).map(function(it){ return it.el; }).filter(function(n){ return n.style.display !== 'none'; });
            if (e.key === 'ArrowDown') { e.preventDefault(); idx = Math.min(idx+1, visible.length-1); if (idx>=0) visible[idx].scrollIntoView({block:'nearest'}); }
            if (e.key === 'ArrowUp') { e.preventDefault(); idx = Math.max(idx-1, 0); if (idx>=0) visible[idx].scrollIntoView({block:'nearest'}); }
            if (e.key === 'Enter') { e.preventDefault(); if (idx>=0 && visible[idx]) choose(visible[idx].dataset.value, visible[idx].textContent); }
        });

        // Infinite scroll for remote
        if (remoteUrl) {
            list.addEventListener('scroll', function(){
                try { if (sel.getAttribute('data-disable-infinite-scroll')) return; } catch(_) {}
                if (!rHasMore || rLoading) return;
                const nearBottom = list.scrollTop + list.clientHeight >= (list.scrollHeight - 40);
                if (nearBottom) {
                    rPage += 1;
                    fetchPage(rQuery, rPage, true);
                }
            });
        }

        // Re-sync label/chips when select value changes programmatically
        sel.addEventListener('change', function(){
            try {
                if (labelSpan) labelSpan.textContent = selectedText();
                if (isMultiple) renderChips();
                updateClearVisibility();
            } catch(_) {}
        });
        // Observe disabled changes
        try {
            const mo = new MutationObserver(function(m){ m.forEach(function(rec){ if (rec.attributeName === 'disabled') syncDisabled(); }); });
            mo.observe(sel, { attributes: true, attributeFilter: ['disabled'] });
        } catch(_){ }
        // Initial sync
        syncDisabled();
        try { if (isMultiple) renderChips(); } catch(_) {}
        try { updateClearVisibility(); } catch(_) {}
    });
    // Post-clean duplicates in the scope
    cleanupSelectWrappers(scope);
}

try {
    onReady(function(){ initSearchableSelect(document); cleanupSelectWrappers(document); });
    document.addEventListener('htmx:afterSwap', function(e){ try { var r = e.target || document; initSearchableSelect(r); cleanupSelectWrappers(r); } catch(_) {} });
} catch(_) {}

try {
    onReady(function(){ initDateDdMmYyyy(document); });
    document.addEventListener('htmx:afterSwap', function(e){
        try {
            var r = e.target || document;
            initDateDdMmYyyy(r);
        } catch(_) {}
    });
} catch(_) {}

// Export for use in modules (if needed)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        togglePassword,
        formSubmitLoading,
        autoFocusInput,
        toggleSidebar,
        confirmAction,
        copyToClipboard,
        debounce,
        onReady,
        showToast,
        removeToast,
        initSessionMonitor,
        showLoading,
        showSuccess,
        showSuccessWithCountdown,
        showError,
        showPasswordMismatchError,
        showInvalidPasswordError,
        showConfirm,
        ajaxFormSubmit,
        ajaxFormSubmitWithSwal,
        bindFormSwal,
        initSearchableSelect
    };
}
