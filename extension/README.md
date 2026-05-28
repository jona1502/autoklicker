# AutoKlicker — Browser Extension

Auto-klickt Buttons und DOM-Elemente direkt im Browser-Tab — ohne den Mauszeiger zu bewegen. Du kannst deinen PC normal weiterbenutzen.

## Installation

### Chrome / Edge / Brave (Manifest V2)

> **Hinweis:** Chrome zeigt bei MV2-Extensions eine Warnung an, da Google MV2 auslaufen lässt. Die Extension funktioniert aber weiterhin. Für zuverlässigen Langzeit-Einsatz empfiehlt sich **Firefox**.

1. [AutoKlicker-Extension.zip](https://github.com/jona1502/autoklicker/releases/latest) aus den Releases herunterladen
2. ZIP entpacken
3. Chrome öffnen → `chrome://extensions/`
4. **Entwicklermodus** (oben rechts) aktivieren
5. **"Entpackte Erweiterung laden"** → entpackten `extension`-Ordner auswählen

### Firefox

1. [AutoKlicker-Extension.zip](https://github.com/jona1502/autoklicker/releases/latest) herunterladen
2. Firefox öffnen → `about:debugging#/runtime/this-firefox`
3. **"Temporäres Add-on laden"** → `manifest.json` im entpackten Ordner auswählen

---

## Verwendung

1. Extension-Icon in der Browser-Toolbar klicken
2. **Element auswählen:**
   - CSS-Selector manuell eingeben (`#button-id`, `.btn-class`, `button`)  
   - **oder** auf das 🎯-Symbol klicken und das Element im Tab anklicken
3. **Interval** einstellen (min. 50 ms)
4. Optional: Klick-Typ (Links / Rechts / Doppel) und Klick-Anzahl (0 = unbegrenzt)
5. **▶ Start** klicken

Das Klicken läuft im Hintergrund weiter, auch wenn du in anderen Apps arbeitest.

---

## Einschränkungen

| Problem | Ursache |
|---|---|
| Klick hat keine Wirkung | Seite prüft `event.isTrusted` (Anti-Bot) |
| Extension nicht verfügbar | Browser-interne Seiten (`chrome://`, `about:`) |
| Element nicht gefunden | Selector stimmt nicht mehr (z.B. nach Seitenupdate) |

---

## Dateistruktur

```
extension/
├── manifest.json          # Manifest V2
├── popup/
│   ├── popup.html         # UI
│   ├── popup.js           # UI-Logik
│   └── popup.css          # Styling
├── content/
│   └── content.js         # Klick-Ausführung + Element-Picker
├── background/
│   └── background.js      # Nachrichten-Weiterleitung
└── icons/
    ├── icon16.png
    ├── icon48.png
    ├── icon128.png
    ├── icon.svg            # Quell-SVG
    └── generate_icons.py  # Icons neu generieren (pip install Pillow)
```
