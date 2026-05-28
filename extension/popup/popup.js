const selectorInput = document.getElementById('selectorInput');
const selectorStatus = document.getElementById('selectorStatus');
const pickBtn = document.getElementById('pickBtn');
const inputHours = document.getElementById('inputHours');
const inputMinutes = document.getElementById('inputMinutes');
const inputSeconds = document.getElementById('inputSeconds');
const inputMs = document.getElementById('inputMs');
const repeatInput = document.getElementById('repeatInput');
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const statsBar = document.getElementById('statsBar');
const clickCount = document.getElementById('clickCount');
const limitInfo = document.getElementById('limitInfo');
const errorMsg = document.getElementById('errorMsg');

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
  return document.querySelector('input[name="clickType"]:checked').value;
}

function showError(msg) {
  errorMsg.textContent = msg;
  errorMsg.classList.remove('hidden');
}

function clearError() {
  errorMsg.classList.add('hidden');
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
  repeatInput.disabled = running;
}

function updateStats(count, limit) {
  clickCount.textContent = count;
  limitInfo.textContent = limit > 0 ? ` / ${limit}` : '';
}

// Einstellungen laden
chrome.storage.local.get(['selector', 'hours', 'minutes', 'seconds', 'ms', 'repeat', 'clickType'], (data) => {
  if (data.selector) selectorInput.value = data.selector;
  if (data.hours !== undefined) inputHours.value = data.hours;
  if (data.minutes !== undefined) inputMinutes.value = data.minutes;
  if (data.seconds !== undefined) inputSeconds.value = data.seconds;
  if (data.ms !== undefined) inputMs.value = data.ms;
  if (data.repeat !== undefined) repeatInput.value = data.repeat;
  if (data.clickType) {
    const radio = document.querySelector(`input[name="clickType"][value="${data.clickType}"]`);
    if (radio) radio.checked = true;
  }
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
  isPicking = true;
  pickBtn.classList.add('active');
  selectorStatus.textContent = 'Klicke auf ein Element im Tab...';

  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (!tabs[0]) { cancelPicker(); return; }
    chrome.tabs.sendMessage(tabs[0].id, { action: 'startPicker' }, (resp) => {
      if (chrome.runtime.lastError) {
        showError('Seite kann nicht verwendet werden (z.B. neue-Tab-Seite).');
        cancelPicker();
      }
    });
  });
});

function cancelPicker() {
  isPicking = false;
  pickBtn.classList.remove('active');
  selectorStatus.textContent = '';
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

  const settings = {
    selector,
    interval,
    clickType: getClickType(),
    repeat: parseInt(repeatInput.value) || 0,
  };

  // Einstellungen speichern
  chrome.storage.local.set({
    selector,
    hours: inputHours.value,
    minutes: inputMinutes.value,
    seconds: inputSeconds.value,
    ms: inputMs.value,
    repeat: repeatInput.value,
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
