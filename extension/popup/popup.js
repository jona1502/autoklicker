const selectorInput = document.getElementById('selectorInput');
const selectorStatus = document.getElementById('selectorStatus');
const pickBtn = document.getElementById('pickBtn');
const pickerDelayRow = document.getElementById('pickerDelayRow');
const pickerDelay = document.getElementById('pickerDelay');
const inputHours = document.getElementById('inputHours');
const inputMinutes = document.getElementById('inputMinutes');
const inputSeconds = document.getElementById('inputSeconds');
const inputMs = document.getElementById('inputMs');
const mouseButton = document.getElementById('mouseButton');
const clickType = document.getElementById('clickType');
const repeatInput = document.getElementById('repeatInput');
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const statsBar = document.getElementById('statsBar');
const clickCount = document.getElementById('clickCount');
const limitInfo = document.getElementById('limitInfo');
const errorMsg = document.getElementById('errorMsg');
const intervalWarning = document.getElementById('intervalWarning');

let isRunning = false;
let isPicking = false;

function getIntervalMs() {
  const h = parseInt(inputHours.value) || 0;
  const m = parseInt(inputMinutes.value) || 0;
  const s = parseInt(inputSeconds.value) || 0;
  const ms = parseInt(inputMs.value) || 0;
  return (h * 3600 + m * 60 + s) * 1000 + ms;
}

function getClickType() {
  return clickType.value;
}

function getRepeatMode() {
  return document.querySelector('input[name="repeatMode"]:checked').value;
}

function setRepeatMode(mode) {
  const radio = document.querySelector(`input[name="repeatMode"][value="${mode}"]`);
  if (radio) radio.checked = true;
  repeatInput.disabled = mode !== 'count';
}

function getRepeatCount() {
  if (getRepeatMode() === 'untilStopped') return -1;
  return Math.max(1, parseInt(repeatInput.value, 10) || 1);
}

function showError(msg) {
  errorMsg.textContent = msg;
  errorMsg.classList.remove('hidden');
}

function clearError() {
  errorMsg.classList.add('hidden');
}

function updateIntervalWarning() {
  const interval = getIntervalMs();
  const hasAnyValue = [inputHours, inputMinutes, inputSeconds, inputMs].some((input) => {
    return (parseInt(input.value, 10) || 0) > 0;
  });

  if (!hasAnyValue || interval >= 1000) {
    intervalWarning.classList.add('hidden');
    intervalWarning.textContent = '';
    return;
  }

  intervalWarning.textContent = 'Sehr kurze oder exakt gleichmaessige Intervalle koennen von Webseiten ignoriert oder gefiltert werden. Script-Klicks bleiben trotzdem isTrusted=false.';
  intervalWarning.classList.remove('hidden');
}

function setRunning(running) {
  isRunning = running;
  startBtn.classList.toggle('hidden', running);
  stopBtn.classList.toggle('hidden', !running);
  statsBar.classList.toggle('hidden', !running);
  selectorInput.disabled = running;
  pickBtn.disabled = running;
  inputHours.disabled = running;
  inputMinutes.disabled = running;
  inputSeconds.disabled = running;
  inputMs.disabled = running;
  mouseButton.disabled = running;
  clickType.disabled = running;
  document.querySelectorAll('input[name="repeatMode"]').forEach((radio) => {
    radio.disabled = running;
  });
  repeatInput.disabled = running || getRepeatMode() !== 'count';
}

function updateStats(count, limit) {
  clickCount.textContent = count;
  limitInfo.textContent = limit > 0 ? ` / ${limit}` : '';
}

// Einstellungen laden
chrome.storage.local.get(
  [
    'selector',
    'hours',
    'minutes',
    'seconds',
    'ms',
    'repeat',
    'repeatMode',
    'mouseButton',
    'clickType',
    'pickerDelay',
    'pickedTagInfo',
    'pickerStatus',
  ],
  (data) => {
  if (data.selector) selectorInput.value = data.selector;
  if (data.hours !== undefined) inputHours.value = data.hours;
  if (data.minutes !== undefined) inputMinutes.value = data.minutes;
  if (data.seconds !== undefined) inputSeconds.value = data.seconds;
  if (data.ms !== undefined) inputMs.value = data.ms;
  if (data.repeat !== undefined) repeatInput.value = data.repeat;
  if (data.repeatMode) setRepeatMode(data.repeatMode);
  if (data.mouseButton) mouseButton.value = data.mouseButton;
  if (data.pickerDelay !== undefined) pickerDelay.value = data.pickerDelay;
  if (data.clickType) clickType.value = data.clickType;
  if (data.pickerStatus === 'picked' && data.pickedTagInfo) {
    selectorStatus.textContent = `Gewählt: ${data.pickedTagInfo}`;
  }
  if (data.pickerStatus === 'active') {
    selectorStatus.textContent = 'Picker läuft im Tab. Auf ein Element klicken oder Esc drücken.';
  }
  if (data.pickerStatus === 'cancelled') {
    selectorStatus.textContent = 'Auswahl abgebrochen.';
  }
  updateIntervalWarning();
});

[inputHours, inputMinutes, inputSeconds, inputMs].forEach((input) => {
  input.addEventListener('input', updateIntervalWarning);
});

document.querySelectorAll('input[name="repeatMode"]').forEach((radio) => {
  radio.addEventListener('change', () => setRepeatMode(getRepeatMode()));
});

// Laufenden Status beim Öffnen abfragen
chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
  if (!tabs[0]) return;
  chrome.tabs.sendMessage(tabs[0].id, { action: 'getStatus' }, (resp) => {
    if (chrome.runtime.lastError) return;
    if (resp && resp.running) {
      setRunning(true);
      updateStats(resp.count, resp.limit);
    }
  });
});

// Element-Picker
pickBtn.addEventListener('click', () => {
  if (isPicking) {
    cancelPicker();
    return;
  }

  const delay = parseInt(pickerDelay.value) || 0;
  isPicking = true;
  pickBtn.classList.add('active');
  pickerDelayRow.classList.remove('hidden');
  chrome.storage.local.set({ pickerDelay: pickerDelay.value });
  selectorStatus.textContent = delay > 0
    ? `Picker startet im Tab in ${delay}s. Popup darf sich schließen.`
    : 'Picker läuft im Tab. Element anklicken, Esc bricht ab.';

  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (!tabs[0]) {
      cancelPicker();
      return;
    }
    chrome.tabs.sendMessage(
      tabs[0].id,
      { action: 'startPicker', options: { delaySeconds: delay } },
      (resp) => {
      if (chrome.runtime.lastError) {
        showError('Seite kann nicht verwendet werden (z.B. neue-Tab-Seite).');
        cancelPicker();
        return;
      }
      chrome.storage.local.set({ pickerStatus: 'active' });
    });
  });
});

function cancelPicker() {
  isPicking = false;
  pickBtn.classList.remove('active');
  selectorStatus.textContent = 'Auswahl abgebrochen.';
  chrome.storage.local.set({ pickerStatus: 'cancelled' });
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (tabs[0]) chrome.tabs.sendMessage(tabs[0].id, { action: 'cancelPicker' });
  });
}

// Nachrichten vom Content-Script empfangen
chrome.runtime.onMessage.addListener((msg) => {
  if (msg.action === 'pickedSelector') {
    selectorInput.value = msg.selector;
    selectorStatus.textContent = `Gewählt: ${msg.tagInfo}`;
    isPicking = false;
    pickBtn.classList.remove('active');
    chrome.storage.local.set({
      selector: msg.selector,
      pickedTagInfo: msg.tagInfo,
      pickerStatus: 'picked',
    });
  }
  if (msg.action === 'pickerCancelled') {
    isPicking = false;
    pickBtn.classList.remove('active');
    selectorStatus.textContent = 'Abgebrochen.';
  }
  if (msg.action === 'clickTick') {
    updateStats(msg.count, msg.limit);
  }
  if (msg.action === 'stopped') {
    setRunning(false);
    if (msg.reason === 'limitReached') {
      selectorStatus.textContent = `Fertig — ${msg.count} Klicks ausgeführt.`;
    }
    if (msg.reason === 'elementNotFound') {
      showError(`Element nicht gefunden: "${msg.selector}"`);
    }
  }
});

// Start
startBtn.addEventListener('click', () => {
  clearError();
  const selector = selectorInput.value.trim();
  if (!selector) {
    showError('Bitte einen CSS-Selector eingeben oder Element auswählen.');
    return;
  }
  const interval = getIntervalMs();
  if (interval < 50) {
    showError('Interval muss mindestens 50 ms sein.');
    return;
  }
  updateIntervalWarning();

  const settings = {
    selector,
    interval,
    mouseButton: mouseButton.value,
    clickType: getClickType(),
    repeat: getRepeatCount(),
  };

  // Einstellungen speichern
  chrome.storage.local.set({
    selector,
    hours: inputHours.value,
    minutes: inputMinutes.value,
    seconds: inputSeconds.value,
    ms: inputMs.value,
    repeat: repeatInput.value,
    repeatMode: getRepeatMode(),
    mouseButton: settings.mouseButton,
    clickType: settings.clickType,
  });

  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (!tabs[0]) { showError('Kein aktiver Tab gefunden.'); return; }
    chrome.tabs.sendMessage(tabs[0].id, { action: 'start', settings }, (resp) => {
      if (chrome.runtime.lastError) {
        showError('Content-Script nicht verfügbar. Seite neu laden und erneut versuchen.');
        return;
      }
      if (resp && resp.ok) {
        updateStats(0, settings.repeat);
        setRunning(true);
      }
    });
  });
});

// Stop
stopBtn.addEventListener('click', () => {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (!tabs[0]) return;
    chrome.tabs.sendMessage(tabs[0].id, { action: 'stop' });
  });
  setRunning(false);
});
