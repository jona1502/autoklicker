(() => {
  let timer = null;
  let clickCount = 0;
  let currentSettings = null;
  let isPicking = false;
  let highlightEl = null;
  let overlay = null;

  // ── Klick-Ausführung ──────────────────────────────────────────────────────

  function dispatchClick(el, type) {
    if (type === 'double') {
      el.dispatchEvent(new MouseEvent('dblclick', { bubbles: true, cancelable: true, view: window }));
      return;
    }
    const btn = type === 'right' ? 2 : 0;
    el.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, cancelable: true, button: btn, view: window }));
    el.dispatchEvent(new MouseEvent('mouseup',   { bubbles: true, cancelable: true, button: btn, view: window }));
    if (type === 'right') {
      el.dispatchEvent(new MouseEvent('contextmenu', { bubbles: true, cancelable: true, view: window }));
    } else {
      el.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
    }
  }

  function tick() {
    const { selector, clickType, repeat } = currentSettings;
    const el = document.querySelector(selector);

    if (!el) {
      stop('elementNotFound');
      return;
    }

    dispatchClick(el, clickType);
    clickCount++;

    chrome.runtime.sendMessage({ action: 'clickTick', count: clickCount, limit: repeat });

    if (repeat > 0 && clickCount >= repeat) {
      stop('limitReached');
    }
  }

  function start(settings) {
    stop();
    currentSettings = settings;
    clickCount = 0;
    timer = setInterval(tick, settings.interval);
  }

  function stop(reason) {
    if (timer) {
      clearInterval(timer);
      timer = null;
    }
    if (reason) {
      chrome.runtime.sendMessage({
        action: 'stopped',
        reason,
        count: clickCount,
        selector: currentSettings ? currentSettings.selector : '',
      });
    }
    currentSettings = null;
  }

  // ── Element-Picker ────────────────────────────────────────────────────────

  function buildSelector(el) {
    if (el.id) return `#${CSS.escape(el.id)}`;

    let selector = el.tagName.toLowerCase();
    if (el.className) {
      const classes = [...el.classList].map(c => `.${CSS.escape(c)}`).join('');
      if (classes) selector += classes;
    }

    // Prüfen ob eindeutig
    if (document.querySelectorAll(selector).length === 1) return selector;

    // Mit Index unter Parent
    const siblings = el.parentElement
      ? [...el.parentElement.children].filter(c => c.tagName === el.tagName)
      : [];
    if (siblings.length > 1) {
      const idx = siblings.indexOf(el) + 1;
      selector += `:nth-of-type(${idx})`;
    }
    return selector;
  }

  function createOverlay(el) {
    removeOverlay();
    const rect = el.getBoundingClientRect();
    overlay = document.createElement('div');
    Object.assign(overlay.style, {
      position: 'fixed',
      top: rect.top + 'px',
      left: rect.left + 'px',
      width: rect.width + 'px',
      height: rect.height + 'px',
      background: 'rgba(123,104,238,0.35)',
      border: '2px solid #7b68ee',
      borderRadius: '3px',
      pointerEvents: 'none',
      zIndex: '2147483647',
    });
    document.body.appendChild(overlay);
  }

  function removeOverlay() {
    if (overlay) { overlay.remove(); overlay = null; }
  }

  function onPickerMouseMove(e) {
    if (e.target === overlay) return;
    highlightEl = e.target;
    createOverlay(e.target);
  }

  function onPickerClick(e) {
    e.preventDefault();
    e.stopPropagation();
    const el = highlightEl || e.target;
    const selector = buildSelector(el);
    const tagInfo = `<${el.tagName.toLowerCase()}> ${selector}`;
    cancelPicker();
    chrome.runtime.sendMessage({ action: 'pickedSelector', selector, tagInfo });
  }

  function startPicker() {
    isPicking = true;
    document.addEventListener('mousemove', onPickerMouseMove, true);
    document.addEventListener('click', onPickerClick, true);
    document.body.style.cursor = 'crosshair';
  }

  function cancelPicker() {
    isPicking = false;
    document.removeEventListener('mousemove', onPickerMouseMove, true);
    document.removeEventListener('click', onPickerClick, true);
    document.body.style.cursor = '';
    removeOverlay();
  }

  // ── Nachrichten-Handler ───────────────────────────────────────────────────

  chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
    if (msg.action === 'start') {
      start(msg.settings);
      sendResponse({ ok: true });
    }
    if (msg.action === 'stop') {
      stop();
      sendResponse({ ok: true });
    }
    if (msg.action === 'getStatus') {
      sendResponse({
        running: timer !== null,
        count: clickCount,
        limit: currentSettings ? currentSettings.repeat : 0,
      });
    }
    if (msg.action === 'startPicker') {
      startPicker();
      sendResponse({ ok: true });
    }
    if (msg.action === 'cancelPicker') {
      cancelPicker();
      sendResponse({ ok: true });
    }
    return true;
  });
})();
