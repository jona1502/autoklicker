// Leitet Nachrichten vom Content-Script an das Popup weiter
chrome.runtime.onMessage.addListener((msg, sender) => {
  if (msg.action === 'clickTick' || msg.action === 'stopped' || msg.action === 'pickedSelector') {
    chrome.runtime.sendMessage(msg).catch(() => {});
  }
});
