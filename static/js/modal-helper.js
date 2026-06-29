(function () {
  function byId(id) {
    return document.getElementById(id);
  }

  function open(modalId) {
    const modal = byId(modalId);
    if (!modal) return;

    const overlay = modal.querySelector('[data-modal-overlay]');
    const panel = modal.querySelector('[data-modal-panel]');

    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';

    requestAnimationFrame(() => {
      if (overlay) {
        overlay.classList.remove('opacity-0');
        overlay.classList.add('opacity-100');
      }
      if (panel) {
        panel.classList.remove('opacity-0', 'scale-95', 'translate-y-2');
        panel.classList.add('opacity-100', 'scale-100', 'translate-y-0');
      }
    });
  }

  function close(modalId) {
    const modal = byId(modalId);
    if (!modal) return;

    const overlay = modal.querySelector('[data-modal-overlay]');
    const panel = modal.querySelector('[data-modal-panel]');

    if (overlay) {
      overlay.classList.remove('opacity-100');
      overlay.classList.add('opacity-0');
    }
    if (panel) {
      panel.classList.remove('opacity-100', 'scale-100', 'translate-y-0');
      panel.classList.add('opacity-0', 'scale-95', 'translate-y-2');
    }

    window.setTimeout(() => {
      modal.classList.add('hidden');
      document.body.style.overflow = 'auto';
      const content = modal.querySelector('[data-modal-content]');
      if (content) content.innerHTML = '';
    }, 230);
  }

  function previewFoto(imgSrc, imgAlt) {
    const modal = byId('fotoPreviewModal');
    if (!modal) return;

    const content = modal.querySelector('[data-modal-content]');
    if (!content) return;

    content.innerHTML = '';
    const img = document.createElement('img');
    img.src = imgSrc;
    img.alt = imgAlt || 'Preview Foto';
    img.className = 'rounded-lg shadow-2xl animate-zoom-in';
    img.style.maxWidth = '100%';
    img.style.maxHeight = '85vh';
    img.style.margin = '0 auto';
    img.style.display = 'block';

    const closeBtn = document.createElement('button');
    closeBtn.innerHTML = '&times;';
    closeBtn.className = 'absolute text-white hover:text-gray-300';
    closeBtn.style.top = '4px';
    closeBtn.style.right = '8px';
    closeBtn.style.fontSize = '32px';
    closeBtn.style.zIndex = '10';
    closeBtn.style.background = 'none';
    closeBtn.style.border = 'none';
    closeBtn.style.cursor = 'pointer';
    closeBtn.onclick = function () { closeFotoPreview(); };

    content.appendChild(closeBtn);
    content.appendChild(img);

    const overlay = modal.querySelector('[data-modal-overlay]');
    const panel = modal.querySelector('[data-modal-panel]');

    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';

    requestAnimationFrame(function () {
      void overlay.offsetHeight;
      if (overlay) { overlay.classList.remove('opacity-0'); overlay.classList.add('opacity-100'); }
      if (panel) {
        panel.classList.remove('opacity-0', 'scale-95', 'translate-y-2');
        panel.classList.add('opacity-100', 'scale-100', 'translate-y-0');
      }
    });
  }

  function closeFotoPreview() {
    const modal = byId('fotoPreviewModal');
    if (!modal) return;

    const content = modal.querySelector('[data-modal-content]');
    const overlay = modal.querySelector('[data-modal-overlay]');
    const panel = modal.querySelector('[data-modal-panel]');

    if (overlay) { overlay.classList.remove('opacity-100'); overlay.classList.add('opacity-0'); }
    if (panel) {
      panel.classList.remove('opacity-100', 'scale-100', 'translate-y-0');
      panel.classList.add('opacity-0', 'scale-95', 'translate-y-2');
    }

    window.setTimeout(function () {
      modal.classList.add('hidden');
      document.body.style.overflow = 'auto';
      if (content) content.innerHTML = '';
    }, 230);
  }

  function fallbackPasFoto(img) {
    img.onerror = null;
    var d = document.createElement('div');
    d.className = 'w-24 h-24 rounded-full bg-gray-200 flex items-center justify-center text-gray-400 mx-auto';
    d.innerHTML = '<i class="fas fa-user text-lg"></i>';
    img.parentNode.replaceChild(d, img);
  }

  window.ModalHelper = { open, close, previewFoto, closeFotoPreview, fallbackPasFoto };
})();
