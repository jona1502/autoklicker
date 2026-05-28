(() => {
  let timer = null;
  let clickCount = 0;
  let currentSettings = null;
  let missCount = 0;
  let isPicking = false;
  let pickerActive = false;
  let pickerTimer = null;
  let pickerCountdownTimer = null;
  let highlightEl = null;
  let overlay = null;
  let pickerHud = null;

  // ── Klick-Ausführung ──────────────────────────────────────────────────────

  function getButtonCode(button) {
    if (button === 'middle') return 1;
    if (button === 'right') return 2;
    return 0;
  }

  function getButtonsMask(buttonCode) {
    if (buttonCode === 1) return 4;
    if (buttonCode === 2) return 2;
    return 1;
  }

  function dispatchSingleClick(el, mouseButton) {
    const btn = getButtonCode(mouseButton);
    const opts = {
      bubbles: true,
      cancelable: true,
      button: btn,
      buttons: getButtonsMask(btn),
      view: window,
    };
    // Pointer-Events zuerst (React und viele moderne Frameworks hören hier)
    el.dispatchEvent(new PointerEvent('pointerover',  { bubbles: true, cancelable: true }));
    el.dispatchEvent(new PointerEvent('pointerenter', { bubbles: true, cancelable: false }));
    el.dispatchEvent(new PointerEvent('pointerdown',  { ...opts, pointerId: 1, pointerType: 'mouse' }));
    el.dispatchEvent(new MouseEvent('mousedown', opts));
    el.dispatchEvent(new PointerEvent('pointerup',    { ...opts, pointerId: 1, pointerType: 'mouse' }));
    el.dispatchEvent(new MouseEvent('mouseup', opts));
    if (mouseButton === 'right') {
      el.dispatchEvent(new MouseEvent('contextmenu', { bubbles: true, cancelable: true, view: window }));
    } else if (mouseButton === 'middle') {
      el.dispatchEvent(new MouseEvent('auxclick', { ...opts, buttons: 0 }));
    } else {
      el.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
    }
  }

  function dispatchClick(el, mouseButton, clickType) {
    const clickTimes = clickType === 'triple' ? 3 : clickType === 'double' ? 2 : 1;
    for (let i = 0; i < clickTimes; i++) {
      dispatchSingleClick(el, mouseButton);
    }
    if (clickTimes >= 2 && mouseButton === 'left') {
      el.dispatchEvent(new MouseEvent('dblclick', { bubbles: true, cancelable: true, button: 0, view: window }));
    }
  }

  function querySelectorSafe(selector) {
    try {
      return document.querySelector(selector);
    } catch (_error) {
      return null;
    }
  }

  function selectorFromStableAttribute(selector) {
    const attrMatch = selector.match(/\[(data-e2e|data-testid|data-test|data-cy|data-id|aria-label|name|role)=["']([^"']+)["']\]/);
    if (!attrMatch) return null;
    return `[${attrMatch[1]}="${CSS.escape(attrMatch[2])}"]`;
  }

  function resolveClickTarget(selector) {
    const direct = querySelectorSafe(selector);
    if (direct) return getClickableTarget(direct);

    const stableSelector = selectorFromStableAttribute(selector);
    if (!stableSelector) return null;

    const stableTarget = querySelectorSafe(stableSelector);
    if (!stableTarget) return null;

    const clickTarget = getClickableTarget(stableTarget);
    if (currentSettings && currentSettings.selector !== stableSelector) {
      currentSettings.selector = stableSelector;
      chrome.storage.local.set({
        selector: stableSelector,
        pickedTagInfo: `<${clickTarget.tagName.toLowerCase()}> ${stableSelector}`,
        pickerStatus: 'picked',
      });
    }
    return clickTarget;
  }

  function tick() {
    const { selector, mouseButton, clickType, repeat } = currentSettings;
    const el = resolveClickTarget(selector);

    if (!el) {
      missCount++;
      if (missCount >= 10) {
        stop('elementNotFound');
        return;
      }
      timer = setTimeout(tick, Math.min(250, Math.max(50, currentSettings.interval)));
      return;
    }

    missCount = 0;
    dispatchClick(el, mouseButton, clickType);
    clickCount++;

    chrome.runtime.sendMessage({ action: 'clickTick', count: clickCount, limit: repeat });

    if (repeat > 0 && clickCount >= repeat) {
      stop('limitReached');
      return;
    }

    timer = setTimeout(tick, currentSettings.interval);
  }

  function start(settings) {
    stop();
    currentSettings = settings;
    clickCount = 0;
    missCount = 0;
    tick();
  }

  function stop(reason) {
    if (timer) {
      clearTimeout(timer);
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
    missCount = 0;
  }

  // ── Element-Picker ────────────────────────────────────────────────────────

  // Stabile data-/aria-Attribute die als eindeutige Selector-Anker gut geeignet sind
  const ANCHOR_ATTRS = [
    'data-e2e', 'data-testid', 'data-test', 'data-cy', 'data-id',
    'data-component', 'aria-label', 'name', 'role',
  ];

  function unique(sel) {
    return document.querySelectorAll(sel).length === 1;
  }

  function getClickableTarget(el) {
    if (!el || el === document.documentElement || el === document.body) return el;

    const directTarget = el.closest(
      'button, a, input, select, textarea, [role="button"], [role="link"], [onclick], [tabindex], ' +
      '[data-e2e], [data-testid], [data-test], [data-cy], [aria-label]'
    );

    return directTarget || el;
  }

  function buildSelector(el) {
    // 1. ID
    if (el.id) return `#${CSS.escape(el.id)}`;

    // 2. Stabile data-/aria-Attribute
    for (const attr of ANCHOR_ATTRS) {
      const val = el.getAttribute(attr);
      if (val) {
        const sel = `[${attr}="${CSS.escape(val)}"]`;
        if (unique(sel)) return sel;
        // Mit Tag kombinieren falls nicht eindeutig
        const selWithTag = `${el.tagName.toLowerCase()}${sel}`;
        if (unique(selWithTag)) return selWithTag;
        if (attr.startsWith('data-') || attr === 'aria-label') return selWithTag;
      }
    }

    // 3. Klassen (Tailwind-Klassen überspringen — zu instabil)
    const stableClasses = [...el.classList].filter(c =>
      !c.match(/^(w-|h-|p-|m-|flex|grid|block|inline|text-|bg-|border-|rounded|items-|justify-|cursor-|hover:|focus:|active:|sm:|md:|lg:|xl:|gap-|space-|overflow-|z-|top-|left-|right-|bottom-|absolute|relative|fixed|sticky|opacity-|transition|duration-|ease-)/)
    );
    if (stableClasses.length > 0) {
      const sel = el.tagName.toLowerCase() + stableClasses.map(c => `.${CSS.escape(c)}`).join('');
      if (unique(sel)) return sel;
    }

    // 4. Pfad über Parent aufbauen
    return buildPathSelector(el);
  }

  function buildPathSelector(el) {
    const parts = [];
    let current = el;
    while (current && current !== document.body) {
      let part = current.tagName.toLowerCase();
      if (current.id) {
        parts.unshift(`#${CSS.escape(current.id)}`);
        break;
      }
      // Stabiles Attribut am aktuellen Element?
      for (const attr of ANCHOR_ATTRS) {
        const val = current.getAttribute(attr);
        if (val) { part = `[${attr}="${CSS.escape(val)}"]`; break; }
      }
      // nth-child als Fallback
      if (current.parentElement) {
        const siblings = [...current.parentElement.children].filter(c => c.tagName === current.tagName);
        if (siblings.length > 1) {
          const idx = siblings.indexOf(current) + 1;
          part += `:nth-of-type(${idx})`;
        }
      }
      parts.unshift(part);
      current = current.parentElement;
      const candidate = parts.join(' > ');
      if (unique(candidate)) return candidate;
    }
    return parts.join(' > ');
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

  function createPickerHud(text) {
    if (!pickerHud) {
      pickerHud = document.createElement('div');
      Object.assign(pickerHud.style, {
        position: 'fixed',
        top: '16px',
        left: '50%',
        transform: 'translateX(-50%)',
        maxWidth: 'min(520px, calc(100vw - 32px))',
        padding: '10px 14px',
        background: '#111315',
        border: '1px solid #4fb3bf',
        borderRadius: '6px',
        color: '#edf2f4',
        font: '13px/1.35 Segoe UI, Arial, sans-serif',
        boxShadow: '0 10px 30px rgba(0,0,0,0.35)',
        pointerEvents: 'none',
        zIndex: '2147483647',
      });
      document.documentElement.appendChild(pickerHud);
    }
    pickerHud.textContent = text;
  }

  function removePickerHud() {
    if (pickerHud) {
      pickerHud.remove();
      pickerHud = null;
    }
  }

  function onPickerMouseMove(e) {
    if (e.target === overlay || e.target === pickerHud) return;
    highlightEl = getClickableTarget(e.target);
    createOverlay(highlightEl);
  }

  function finishPick(el) {
    if (!el || el === overlay || el === pickerHud) return;
    const target = getClickableTarget(el);
    const selector = buildSelector(target);
    const tagInfo = `<${target.tagName.toLowerCase()}> ${selector}`;

    chrome.storage.local.set({
      selector,
      pickedTagInfo: tagInfo,
      pickerStatus: 'picked',
      pickerPickedAt: Date.now(),
    });

    cancelPicker(false);
    chrome.runtime.sendMessage({ action: 'pickedSelector', selector, tagInfo });
  }

  function onPickerClick(e) {
    if (!pickerActive) return;
    e.preventDefault();
    e.stopPropagation();
    e.stopImmediatePropagation();
    finishPick(highlightEl || e.target);
  }

  function onPickerKeyDown(e) {
    if (e.key === 'Enter') {
      e.preventDefault();
      e.stopImmediatePropagation();
      finishPick(highlightEl);
    }
    if (e.key === 'Escape') {
      e.preventDefault();
      e.stopImmediatePropagation();
      cancelPicker(true);
      chrome.runtime.sendMessage({ action: 'pickerCancelled' });
    }
  }

  function activatePicker() {
    pickerActive = true;
    createPickerHud('Element auswählen: Maus bewegen, Linksklick bestätigt. Esc bricht ab.');
    document.addEventListener('mousemove', onPickerMouseMove, true);
    document.addEventListener('click', onPickerClick, true);
    document.addEventListener('keydown', onPickerKeyDown, true);
    document.body.style.cursor = 'crosshair';
  }

  function startPicker(options = {}) {
    cancelPicker(false);
    isPicking = true;
    pickerActive = false;
    highlightEl = null;
    const delaySeconds = Math.max(0, parseInt(options.delaySeconds, 10) || 0);

    document.addEventListener('keydown', onPickerKeyDown, true);
    chrome.storage.local.set({ pickerStatus: 'active' });

    if (delaySeconds <= 0) {
      activatePicker();
      return;
    }

    let remaining = delaySeconds;
    createPickerHud(`Picker startet in ${remaining}s. Menüs oder Dropdowns jetzt öffnen. Esc bricht ab.`);
    pickerCountdownTimer = setInterval(() => {
      remaining--;
      if (remaining <= 0) {
        clearInterval(pickerCountdownTimer);
        pickerCountdownTimer = null;
      } else {
        createPickerHud(`Picker startet in ${remaining}s. Menüs oder Dropdowns jetzt öffnen. Esc bricht ab.`);
      }
    }, 1000);

    pickerTimer = setTimeout(() => {
      pickerTimer = null;
      if (pickerCountdownTimer) {
        clearInterval(pickerCountdownTimer);
        pickerCountdownTimer = null;
      }
      activatePicker();
    }, delaySeconds * 1000);
  }

  function cancelPicker(markCancelled = true) {
    if (pickerTimer) {
      clearTimeout(pickerTimer);
      pickerTimer = null;
    }
    if (pickerCountdownTimer) {
      clearInterval(pickerCountdownTimer);
      pickerCountdownTimer = null;
    }
    isPicking = false;
    pickerActive = false;
    document.removeEventListener('mousemove', onPickerMouseMove, true);
    document.removeEventListener('click', onPickerClick, true);
    document.removeEventListener('keydown', onPickerKeyDown, true);
    document.body.style.cursor = '';
    removeOverlay();
    removePickerHud();
    if (markCancelled) {
      chrome.storage.local.set({ pickerStatus: 'cancelled' });
    }
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
      startPicker(msg.options || {});
      sendResponse({ ok: true });
    }
    if (msg.action === 'cancelPicker') {
      cancelPicker();
      sendResponse({ ok: true });
    }
    return true;
  });
})();
