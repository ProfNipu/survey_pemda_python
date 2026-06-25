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

  window.ModalHelper = { open, close };
})();
