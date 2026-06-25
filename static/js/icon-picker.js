(function(){
  'use strict';

  // Lightweight reusable Icon Picker
  // Usage:
  // 1) Include once in base layout: <script src="/static/js/icon-picker.js"></script>
  // 2) Add a button with data-icon-picker="#inputId"
  // 3) Optional: window.IconPicker.open({ input: document.querySelector('#inputId'), initial: 'fas fa-folder', onSelect: fn })

  var DEFAULT_ICONS = [
    'fas fa-0','fas fa-1','fas fa-2','fas fa-3','fas fa-4','fas fa-5','fas fa-6','fas fa-7','fas fa-8','fas fa-9',
    'fas fa-folder','fas fa-folder-open','fas fa-home','fas fa-tachometer-alt','fas fa-users','fas fa-user','fas fa-user-friends','fas fa-id-card','fas fa-address-book','fas fa-briefcase','fas fa-building','fas fa-cog','fas fa-cogs','fas fa-tools','fas fa-wrench','fas fa-database','fas fa-server','fas fa-cloud','fas fa-upload','fas fa-download','fas fa-file','fas fa-file-alt','fas fa-file-excel','fas fa-file-pdf','fas fa-book','fas fa-book-open','fas fa-chart-bar','fas fa-chart-line','fas fa-chart-pie','fas fa-table','fas fa-list','fas fa-list-alt','fas fa-calendar','fas fa-clock','fas fa-history','fas fa-bell','fas fa-envelope','fas fa-inbox','fas fa-paper-plane','fas fa-search','fas fa-filter','fas fa-check','fas fa-times','fas fa-plus','fas fa-minus','fas fa-edit','fas fa-trash','fas fa-sync','fas fa-sync-alt','fas fa-spinner','fas fa-lock','fas fa-unlock','fas fa-key','fas fa-shield-alt','fas fa-link','fas fa-external-link-alt','fas fa-map','fas fa-map-marker-alt','fas fa-phone','fas fa-comment','fas fa-comments','fas fa-info-circle','fas fa-question-circle','fas fa-exclamation-triangle','fas fa-bug','fas fa-code','fas fa-terminal','fas fa-globe','fas fa-star','far fa-star','far fa-file','far fa-file-alt','far fa-envelope','far fa-bell','fab fa-github','fab fa-gitlab','fab fa-docker','fab fa-aws','fab fa-linux','fab fa-windows','fab fa-apple','fab fa-android','fab fa-python','fab fa-laravel','fab fa-node','fab fa-react','fab fa-bootstrap'
  ];
  var LUCIDE_ICONS = [
    'lucide:home','lucide:user','lucide:users','lucide:settings','lucide:folder','lucide:file','lucide:search','lucide:bell','lucide:calendar','lucide:check','lucide:x','lucide:plus','lucide:minus','lucide:edit','lucide:trash','lucide:star','lucide:globe','lucide:map','lucide:phone','lucide:mail','lucide:lock','lucide:unlock','lucide:key','lucide:shield','lucide:cloud','lucide:download','lucide:upload','lucide:database','lucide:alert-circle','lucide:info','lucide:help-circle','lucide:log-in','lucide:log-out','lucide:link','lucide:external-link','lucide:refresh-cw','lucide:server','lucide:terminal'
  ];

  var state = {
    icons: DEFAULT_ICONS.concat(LUCIDE_ICONS),
    current: DEFAULT_ICONS.concat(LUCIDE_ICONS),
    query: '',
    cat: 'all',
    focusIndex: -1,
    targetInput: null,
    onSelect: null,
    openedAt: 0,
    userClickedCategory: false
  };

  var lucideCatalogLoaded = false;
  var lucideKebabSet = null;
  function toKebab(s){
    var str = String(s||'');
    // Handle ABCd -> AB-Cd before the common a-z0-9 to Uppercase split
    str = str.replace(/([A-Z]+)([A-Z][a-z])/g, '$1-$2');
    // Handle aZ -> a-Z
    str = str.replace(/([a-z0-9])([A-Z])/g,'$1-$2');
    // Underscore to hyphen
    str = str.replace(/_/g,'-');
    return str.toLowerCase();
  }
  function ensureLucideCatalog(){
    if (lucideCatalogLoaded) return;
    try {
      if (window.lucide && lucide.icons){
        var keys = Object.keys(lucide.icons || {});
        if (keys && keys.length){
          var existing = new Set(state.icons);
          var kebabSet = new Set();
          keys.forEach(function(k){
            var kebab = toKebab(k);
            kebabSet.add(kebab);
            var v = 'lucide:' + kebab;
            if (!existing.has(v)){
              state.icons.push(v);
              existing.add(v);
            }
          });
          lucideKebabSet = kebabSet;
          lucideCatalogLoaded = true;
        }
      }
    } catch(e){}
  }

  function lucideAlias(name){
    var map = {
      'aarrow-down': 'a-arrow-down',
      'aarrow-up': 'a-arrow-up',
      'alarge-small': 'a-large-small',
      'xcircle': 'x-circle',
      'xsquare': 'x-square',
      'xoctagon': 'x-octagon',
      'file-xcorner': 'file-x',
      'map-pin-xinside': 'map-pin-x'
    };
    return map[name] || name;
  }

  function scrollToTop(){
    function run(){
      var list = [ document.getElementById('ipScroll'), document.getElementById('iconPickerModal') ];
      list.forEach(function(sc){ if (!sc) return; try { sc.scrollTo({ top: 0, behavior: 'auto' }); } catch(e){ sc.scrollTop = 0; } });
    }
    run();
    setTimeout(run, 0);
    setTimeout(run, 50);
    setTimeout(run, 150);
    try { requestAnimationFrame(run); } catch(e){}
  }

  function resetPickerScroll(){
    try {
      var el = document.getElementById('ipScroll');
      if (el && typeof el.scrollTo === 'function') el.scrollTo({ top: 0, behavior: 'auto' });
      else if (el) el.scrollTop = 0;
    } catch(e){}
  }

  // Prevent layout shift when locking scroll by compensating scrollbar width
  function lockPageScroll(){
    try {
      var doc = document.documentElement;
      var sbw = Math.max(0, window.innerWidth - doc.clientWidth);
      // Lock scroll via style to work regardless of utility classes
      doc.style.overflowY = 'hidden';
      document.body.style.overflow = 'hidden';
      if (sbw){
        doc.style.paddingRight = sbw + 'px';
        document.body.style.paddingRight = sbw + 'px';
      }
    } catch(e){}
  }
  function unlockPageScroll(){
    try {
      var doc = document.documentElement;
      doc.style.overflowY = '';
      document.body.style.overflow = '';
      doc.style.paddingRight = '';
      document.body.style.paddingRight = '';
    } catch(e){}
  }

  var faMeta = null;
  function ensureFACatalog(done){
    if (faMeta) { if (done) done(); return; }
    try {
      fetch('/static/js/fa-icons.json', { credentials: 'same-origin' })
        .then(function(r){ return r.ok ? r.json() : null; })
        .then(function(json){
          if (json){
            faMeta = json;
            // Build FA lists based on styles
            var set = new Set();
            var faList = [];
            Object.keys(json).forEach(function(name){
              var styles = (json[name] && (json[name].free || json[name].styles)) || [];
              styles.forEach(function(st){
                if (st === 'solid') faList.push('fas fa-' + name);
                else if (st === 'regular') faList.push('far fa-' + name);
                else if (st === 'brands') faList.push('fab fa-' + name);
              });
            });
            // Add numeric glyph icons 0-9 so they appear in the picker as well
            try {
              ['0','1','2','3','4','5','6','7','8','9'].forEach(function(d){
                faList.push('fas fa-' + d);
              });
            } catch(e){}
            // Rebuild state.icons with FA + existing (Lucide entries already present)
            state.icons = faList.concat(state.icons.filter(function(x){ return String(x).indexOf('lucide:')===0; }));
          }
          if (done) done();
        })
        .catch(function(){ if (done) done(); });
    } catch(e){ if (done) done(); }
  }

  function tpl(){
    return (
      '<div id="iconPickerModal" class="fixed inset-0 z-[10000] hidden overflow-hidden">' +
        '<div id="ipOverlay" class="absolute inset-0 bg-gray-900/60 backdrop-blur-[1px] z-40" data-close="1"></div>' +
        '<div class="absolute inset-0 z-50 flex items-center justify-center p-0 md:p-4">' +
          '<div id="ipPanel" class="w-screen h-screen md:w-[90vw] md:max-w-5xl md:h-[50vh] bg-white rounded-none md:rounded-xl shadow-2xl ring-1 ring-black/5 overflow-hidden flex flex-col">' +
            '<div class="flex items-center justify-between px-5 py-3 border-b shrink-0">' +
              '<h3 class="font-semibold text-gray-800">Pilih Icon</h3>' +
              '<button type="button" class="text-gray-500 hover:text-gray-700" id="ipClose" aria-label="Tutup">' +
                '<i class="fas fa-times"></i>' +
              '</button>' +
            '</div>' +
            '<div id="ipScroll" class="relative z-50 flex-1 min-h-0 p-0 flex flex-col overflow-y-scroll overscroll-y-contain bg-white pb-36 md:pb-44">' +
              '<div class="sticky top-0 z-40 bg-white">' +
                '<div class="flex items-center gap-3 px-5 pt-3 pb-3 border-b shadow-md">' +
                  '<div class="relative flex-1">' +
                    '<i class="fas fa-search absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"></i>' +
                    '<input id="ipSearch" type="text" class="w-full pl-9 pr-3 py-2 rounded-lg border-2 border-gray-200 bg-white shadow-sm focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none placeholder-gray-400" placeholder="Cari icon (contoh: users, chart, folder)">' +
                  '</div>' +
                  '<button type="button" id="ipClear" class="px-3 py-2 rounded-lg border text-sm text-gray-600 hover:bg-gray-50">Clear</button>' +
                '</div>' +
                '<div id="ipCats" class="px-5 py-3 border-b bg-white flex flex-wrap items-center gap-2 text-xs">' +
                  '<button type="button" data-cat="all" class="px-3 py-1 rounded border border-primary bg-primary text-white">Semua</button>' +
                  '<button type="button" data-cat="fas" class="px-3 py-1 rounded border border-gray-200 text-gray-700 hover:bg-gray-50">Solid</button>' +
                  '<button type="button" data-cat="far" class="px-3 py-1 rounded border border-gray-200 text-gray-700 hover:bg-gray-50">Regular</button>' +
                  '<button type="button" data-cat="fab" class="px-3 py-1 rounded border border-gray-200 text-gray-700 hover:bg-gray-50">Brands</button>' +
                  '<button type="button" data-cat="lucide" class="px-3 py-1 rounded border border-gray-200 text-gray-700 hover:bg-gray-50">Lucide</button>' +
                '</div>' +
              '</div>' +
              '<div id="ipRecent" class="mt-2 mb-3 px-6 hidden border-b border-gray-200 py-3">' +
                '<div class="text-xs text-gray-500 mb-2">Recently used</div>' +
                '<div id="ipRecentGrid" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3 mt-1"></div>' +
              '</div>' +
              '<div id="ipGrid" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3 flex-1 min-h-0 px-6 mt-4 pb-56"></div>' +
              '<div class="h-32"></div>' +
            '</div>' +
          '</div>' +
        '</div>' +
      '</div>'
    );
  }

  function ensureModal(){
    var m = document.getElementById('iconPickerModal');
    if (!m){
      var wrap = document.createElement('div');
      wrap.innerHTML = tpl();
      document.body.appendChild(wrap.firstElementChild);
    }
    // Fallback binding for category tabs within the modal container (runs once)
    var modal = document.getElementById('iconPickerModal');
    var cats = modal ? modal.querySelector('#ipCats') : null;
    if (cats && !cats.dataset.bound){
      cats.dataset.bound = '1';
      cats.addEventListener('click', function(ev){
        var btn = ev.target && ev.target.closest && ev.target.closest('button[data-cat]');
        if (!btn) return;
        state.userClickedCategory = true;
        var cat = btn.getAttribute('data-cat') || 'all';
        activateCategory(cat);
        resetPickerScroll();
        state.current = filtered();
        renderIcons(state.current, -1);
        resetPickerScroll();
      });
    }
    return modal;
  }

  function getRecent(){
    try { return JSON.parse(localStorage.getItem('aplikasi_test_icon_recent') || '[]'); } catch(e){ return []; }
  }
  function saveRecent(cls){
    var arr = getRecent().filter(function(x){return x!==cls;});
    arr.unshift(cls);
    localStorage.setItem('aplikasi_test_icon_recent', JSON.stringify(arr.slice(0,5)));
  }

  function filtered(){
    return state.icons.filter(function(c){
      var lc = c.toLowerCase();
      var isLucide = lc.indexOf('lucide:')===0;
      if (isLucide && lucideKebabSet){
        var name = toKebab(lc.split(':')[1]||'');
        if (!lucideKebabSet.has(name)) return false;
      }
      var inCat = (state.cat==='all') || (state.cat==='lucide' && isLucide) || (lc.indexOf(state.cat + ' ')===0);
      var matches = !state.query || lc.indexOf(state.query.toLowerCase())>=0;
      return inCat && matches;
    });
  }

  function markMatch(text,q){
    if (!q) return text;
    var t=String(text), idx=t.toLowerCase().indexOf(q.toLowerCase());
    if (idx<0) return t;
    return t.substring(0,idx) + '<span class="bg-yellow-100">' + t.substring(idx,idx+q.length) + '</span>' + t.substring(idx+q.length);
  }

  var BRAND_SET = new Set([
    'fa-aws','fa-github','fa-gitlab','fa-docker','fa-linux','fa-windows','fa-apple','fa-android','fa-python','fa-laravel','fa-node','fa-react','fa-bootstrap','fa-cc-visa','fa-lastfm','fa-redhat','fa-yoast','fa-cloudflare','fa-buysellads','fa-stackpath','fa-js','fa-js-square'
  ]);
  function normalizeFAClass(cls){
    if (!cls) return cls;
    var parts = String(cls).trim().split(/\s+/);
    var pref = parts[0];
    var icon = parts.find(function(p){ return p.indexOf('fa-')===0 && p!=='fas' && p!=='far' && p!=='fab'; });
    if (!icon) return cls;
    if (BRAND_SET.has(icon) && (pref==='fas' || pref==='far')){
      parts[0] = 'fab';
      return parts.join(' ');
    }
    return cls;
  }

  function setFocus(idx){
    var grid = document.getElementById('ipGrid');
    if (!grid) return;
    var old = grid.querySelector('[data-focused="1"]');
    if (old){ old.removeAttribute('data-focused'); old.classList.remove('border-primary','ring-2','ring-primary/30'); }
    state.focusIndex = idx;
    var el = grid.querySelector('[data-index="'+idx+'"]');
    if (el){ el.setAttribute('data-focused','1'); el.classList.add('border-primary','ring-2','ring-primary/30'); el.scrollIntoView({block:'nearest'}); }
  }

  function renderIcons(items, focusIdx){
    var grid = document.getElementById('ipGrid');
    if (!grid) return;
    grid.innerHTML='';
    items.forEach(function(cls,i){
      var btn = document.createElement('button');
      btn.type='button';
      btn.className='group w-full text-left border rounded-lg px-3 py-3 hover:border-primary focus:outline-none';
      btn.setAttribute('data-index', String(i));
      if (cls.indexOf('lucide:')===0){
        var name = lucideAlias(toKebab(cls.split(':')[1]));
        btn.innerHTML = '<div class="flex items-center gap-3">' +
          '<div class="w-10 h-10 flex items-center justify-center rounded bg-gray-50 text-xl text-gray-700 group-hover:text-primary">' +
          '<i data-lucide="'+name+'"></i></div>' +
          '<div class="text-xs text-gray-700 truncate">'+ markMatch(cls,state.query) +'</div></div>';
      } else {
        cls = normalizeFAClass(cls);
        btn.innerHTML = '<div class="flex items-center gap-3">' +
          '<div class="w-10 h-10 flex items-center justify-center rounded bg-gray-50 text-xl group-hover:text-primary">' +
          '<i class="'+cls+'"></i></div>' +
          '<div class="text-xs text-gray-700 truncate">'+ markMatch(cls,state.query) +'</div></div>';
      }
      btn.addEventListener('click', function(){ selectIcon(cls); });
      grid.appendChild(btn);
    });
    // Render lucide icons inside the grid
    try { if (window.lucide && lucide.createIcons) { lucide.createIcons({ nameAttr: 'data-lucide' }); } } catch(e){}
    if (typeof focusIdx === 'number' && focusIdx >= 0) setFocus(focusIdx); else state.focusIndex=-1;
  }

  function renderRecent(list){
    var wrap = document.getElementById('ipRecent');
    var grid = document.getElementById('ipRecentGrid');
    if (!wrap||!grid) return;
    grid.innerHTML='';
    var recent = (list||[]).slice(0,5);
    if (!recent.length){ wrap.classList.add('hidden'); return; }
    wrap.classList.remove('hidden');
    recent.forEach(function(cls){
      var btn=document.createElement('button');
      btn.type='button';
      btn.className='group w-full text-left border rounded-lg px-3 py-3 hover:border-primary focus:outline-none';
      if (cls.indexOf('lucide:')===0){
        if (lucideKebabSet){
          var n0 = lucideAlias(toKebab(cls.split(':')[1]||''));
          if (!lucideKebabSet.has(n0)) return; // skip missing icons
        }
        var name = lucideAlias(toKebab(cls.split(':')[1]));
        btn.innerHTML='<div class="flex items-center gap-3">' +
          '<div class="w-10 h-10 flex items-center justify-center rounded bg-gray-50 text-xl text-gray-700 group-hover:text-primary">' +
          '<i data-lucide="'+name+'"></i></div>' +
          '<div class="text-xs text-gray-700 truncate">'+cls+'</div></div>';
      } else {
        cls = normalizeFAClass(cls);
        btn.innerHTML='<div class="flex items-center gap-3">' +
          '<div class="w-10 h-10 flex items-center justify-center rounded bg-gray-50 text-xl group-hover:text-primary">' +
          '<i class="'+cls+'"></i></div>' +
          '<div class="text-xs text-gray-700 truncate">'+cls+'</div></div>';
      }
      btn.addEventListener('click', function(){ selectIcon(cls); });
      grid.appendChild(btn);
    });
    try { if (window.lucide && lucide.createIcons) { lucide.createIcons({ nameAttr: 'data-lucide' }); } } catch(e){}
  }

  function activateCategory(cat){
    state.cat = cat;
    var wrap = document.getElementById('ipCats');
    if (wrap){
      wrap.querySelectorAll('button[data-cat]').forEach(function(b){
        var active = (b.getAttribute('data-cat')===cat);
        b.classList.toggle('bg-primary', active);
        b.classList.toggle('text-white', active);
        b.classList.toggle('border-primary', active);
      });
    }
  }

  function open(opts){
    opts = opts||{};
    state.targetInput = opts.input || null;
    state.onSelect = typeof opts.onSelect === 'function' ? opts.onSelect : null;

    var modal = ensureModal();
    // Prepare animation states before showing
    var overlay = modal.querySelector('#ipOverlay');
    var panel = modal.querySelector('#ipPanel');
    try {
      if (overlay){ overlay.style.opacity = '0'; overlay.style.transition = 'opacity 90ms ease-out'; }
      if (panel){ panel.style.opacity = '0'; panel.style.transform = 'translateY(4px)'; panel.style.transition = 'transform 90ms ease-out, opacity 90ms ease-out'; }
    } catch(e){}
    modal.classList.remove('hidden');
    // Kick off animate-in immediately for perceived responsiveness
    try {
      requestAnimationFrame(function(){
        if (overlay) overlay.style.opacity = '1';
        if (panel){ panel.style.opacity = '1'; panel.style.transform = 'translateY(0)'; }
      });
    } catch(e){}

    // Always start on 'all' to reduce confusion; still highlight currently selected icon later
    var selected = state.targetInput ? (state.targetInput.value || '').trim() : '';
    function baseIcon(cls){
      if (!cls) return '';
      var parts = String(cls).trim().split(/\s+/);
      if (cls.indexOf('lucide:')===0){
        return 'lucide:' + cls.split(':')[1];
      }
      for (var i=0;i<parts.length;i++){
        var p = parts[i];
        if (p.indexOf('fa-')===0 && p !== 'fas' && p !== 'far' && p !== 'fab') return p;
      }
      return '';
    }
    state.cat = 'all';
    state.openedAt = Date.now();
    state.userClickedCategory = false;
    activateCategory('all');
    var doRender = function(){
      // Start with an empty query for a clean view
      state.query = '';
      state.current = filtered();
      var idx = -1;
      if (selected) {
        var selLower = selected.toLowerCase();
        idx = state.current.findIndex(function(x){ return String(x).toLowerCase().trim() === selLower; });
        if (idx < 0) {
          var b = baseIcon(selected);
          if (b) idx = state.current.findIndex(function(x){ return baseIcon(x) === b; });
        }
      }
      renderIcons(state.current, idx);
      renderRecent(getRecent());
      var search = document.getElementById('ipSearch');
      if (search){ search.value = ''; requestAnimationFrame(function(){ search.focus(); }); }
      // Enforce highlight on 'Semua' tab after async loads
      activateCategory('all');
      // (animation already started before render for snappier feel)
    };
    // Ensure catalogs then render (defer heavy DOM to next frames to avoid initial delay)
    var schedule = function(){
      try {
        requestAnimationFrame(function(){ requestAnimationFrame(doRender); });
      } catch(e){ setTimeout(doRender, 0); }
    };
    var needFA = !faMeta;
    var needLucide = (state.cat === 'lucide' && !lucideCatalogLoaded) || !lucideCatalogLoaded;
    if (needFA && needLucide){ ensureFACatalog(function(){ ensureLucideCatalog(); schedule(); }); }
    else if (needFA){ ensureFACatalog(function(){ schedule(); }); }
    else { if (needLucide) ensureLucideCatalog(); schedule(); }
    lockPageScroll();
  }

  function close(){
    var modal = document.getElementById('iconPickerModal');
    if (!modal) return;
    var overlay = modal.querySelector('#ipOverlay');
    var panel = modal.querySelector('#ipPanel');
    // Animate out
    try {
      if (overlay) overlay.style.opacity = '0';
      if (panel){ panel.style.opacity = '0'; panel.style.transform = 'translateY(4px)'; }
    } catch(e){}
    setTimeout(function(){
      try { if (modal) modal.classList.add('hidden'); } catch(e){}
      unlockPageScroll();
    }, 90);
  }

  function selectIcon(cls){
    saveRecent(cls);
    if (state.targetInput){
      state.targetInput.value = cls;
      if (typeof window.updateIconPreview === 'function') {
        window.updateIconPreview(cls);
      }
    }
    if (state.onSelect) try { state.onSelect(cls); } catch(e){}
    close();
  }

  function delegate(){
    document.addEventListener('click', function(e){
      var modal = document.getElementById('iconPickerModal');
      var isOpen = modal && !modal.classList.contains('hidden');

      // open trigger
      var tgt = e.target;
      if (tgt && tgt.nodeType !== 1) { tgt = tgt.parentElement; }
      var trigger = tgt && tgt.closest && tgt.closest('[data-icon-picker]');
      if (trigger){
        var sel = trigger.getAttribute('data-icon-picker');
        var input = sel ? document.querySelector(sel) : null;
        open({ input: input });
        // enforce 'Semua' after open to avoid any late mutation
        setTimeout(function(){ activateCategory('all'); }, 0);
        e.preventDefault();
        return;
      }

      if (!isOpen) return;

      // close button
      var isCloseBtn = tgt && tgt.closest && tgt.closest('#ipClose');
      var isOverlay = e.target && e.target.dataset && e.target.dataset.close === '1';
      if (isCloseBtn || isOverlay){ e.preventDefault(); close(); return; }

      // category buttons
      var catBtn = tgt && tgt.closest && tgt.closest('#ipCats button[data-cat]');
      if (catBtn){
        state.userClickedCategory = true;
        var cat = catBtn.getAttribute('data-cat') || 'all';
        activateCategory(cat);
        resetPickerScroll();
        state.current = filtered();
        renderIcons(state.current, -1);
        resetPickerScroll();
        return;
      }

      // clear search
      if ((tgt && tgt.id === 'ipClear') || (tgt && tgt.closest && tgt.closest('#ipClear'))){
        var search = document.getElementById('ipSearch');
        if (search){ search.value=''; state.query=''; state.current=filtered(); renderIcons(state.current); search.focus(); }
        return;
      }
    });

    document.addEventListener('input', function(e){
      if (e.target && e.target.id === 'ipSearch'){
        state.query = e.target.value.trim();
        state.current = filtered();
        renderIcons(state.current, -1);
      }
    });

    document.addEventListener('keydown', function(e){
      var modal = document.getElementById('iconPickerModal');
      if (!modal || modal.classList.contains('hidden')) return;
      if (e.key === 'Escape'){ e.preventDefault(); close(); return; }
      if (['ArrowDown','ArrowUp','ArrowLeft','ArrowRight','Enter'].includes(e.key)) e.preventDefault();
      if (e.key === 'Enter' && state.focusIndex >= 0 && state.current[state.focusIndex]){ selectIcon(state.current[state.focusIndex]); return; }
      if (e.key === 'ArrowDown' || e.key === 'ArrowRight'){ if (state.current.length) setFocus((state.focusIndex + 1 + state.current.length) % state.current.length); return; }
      if (e.key === 'ArrowUp' || e.key === 'ArrowLeft'){ if (state.current.length) setFocus((state.focusIndex - 1 + state.current.length) % state.current.length); return; }
    });
  }

  function renderPreviewInto(el, iconClass){
    if (!el) return;
    if (iconClass && (iconClass.indexOf('lucide:') === 0 || iconClass.indexOf('lucide') === 0)){
      var raw = String(iconClass||'');
      var name = '';
      if (raw.indexOf('lucide:') === 0){
        name = raw.split(':')[1] || '';
      } else {
        // Accept forms like 'lucidealign-...', 'lucide-align-...', 'Lucide:Name', etc.
        var rest = raw.slice(6); // remove 'lucide'
        if (rest && (rest[0] === ':' || rest[0] === '-')) rest = rest.slice(1);
        name = rest || '';
      }
      name = toKebab(name);
      el.innerHTML = '<i data-lucide="' + name + '"></i>';
      try {
        if (window.lucide && lucide.createIcons) {
          lucide.createIcons({ nameAttr: 'data-lucide' });
          // Scale SVG to 1em to match FA sizing in preview containers
          var svg = el.querySelector('svg');
          if (svg){ svg.style.width = '1em'; svg.style.height = '1em'; }
          try { setTimeout(function(){ var s = el.querySelector('svg'); if (s){ s.style.width='1em'; s.style.height='1em'; } }, 0); } catch(e){}
        }
      } catch(e){}
    } else {
      el.innerHTML = '<i class="' + (iconClass || '') + '"></i>';
    }
  }
  function updateIconPreview(iconClass){
    // Update default preview if present
    var preview = document.getElementById('iconPreview');
    if (preview) renderPreviewInto(preview, iconClass);
    // Also update per-field preview tied to the active input (if any)
    try {
      if (state && state.targetInput && state.targetInput.id){
        var local = document.getElementById(state.targetInput.id + '_preview');
        if (local) renderPreviewInto(local, iconClass);
      }
    } catch(e){}
  }

  // Public API
  window.IconPicker = {
    open: open,
    setIcons: function(list){ if (Array.isArray(list)) { state.icons = list.slice(); } },
  };
  window.updateIconPreview = window.updateIconPreview || updateIconPreview;
  window.updateIconPreviewFor = window.updateIconPreviewFor || function(inputId, iconClass){
    try { var el = document.getElementById(String(inputId) + '_preview'); renderPreviewInto(el, iconClass); } catch(e){}
  };

  // Init once
  if (document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', delegate);
  } else {
    delegate();
  }
  try { window.IconPickerVersion = '1.9.16-rename'; } catch(e){}
})();
