// Leitet Nachrichten vom Content-Script an das Popup weiter
chrome.runtime.onMessage.addListener((msg, sender) => {
  const forward = ['clickTick', 'stopped', 'pickedSelector', 'pickerCancelled'];
  if (forward.includes(msg.action)) {
    try {
      chrome.runtime.sendMessage(msg, () => {
        if (chrome.runtime.lastError) {
          // Kein Popup offen. Das ist normal; persistente Daten liegen in chrome.storage.
        }
      });
    } catch (_error) {
      // Popup oder Empfänger existiert nicht.
    }
  }
});
