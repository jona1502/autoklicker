# AutoKlicker — Browser Extension

Auto-klickt Buttons und DOM-Elemente direkt im Browser-Tab — ohne den Mauszeiger zu bewegen. Du kannst deinen PC normal weiterbenutzen.

## Installation

### Brave

1. [AutoKlicker-Brave-MV3.zip](https://github.com/jona1502/autoklicker/releases/latest) aus den Releases herunterladen
2. ZIP entpacken
3. Brave öffnen → `brave://extensions/`
4. **Entwicklermodus** (oben rechts) aktivieren
5. **"Entpackte Erweiterung laden"** → entpackten `extension`-Ordner auswählen

### Chrome / Edge

1. [AutoKlicker-Chrome-MV3.zip](https://github.com/jona1502/autoklicker/releases/latest) aus den Releases herunterladen
2. ZIP entpacken
3. Chrome öffnen → `chrome://extensions/`
4. **Entwicklermodus** (oben rechts) aktivieren
5. **"Entpackte Erweiterung laden"** → entpackten `extension`-Ordner auswählen

### Legacy Manifest V2

`AutoKlicker-Legacy-MV2.zip` ist nur für alte Chromium-basierte Browser gedacht, die Manifest V2 noch laden. Aktuelle Chrome-Versionen unterstützen MV2 nicht mehr. Brave unterstützt MV2 nur eingeschränkt für ausgewählte Erweiterungen; für AutoKlicker sollte dort die MV3-Version verwendet werden.

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

## Funktionstest

Zum technischen Testen kann `test-page.html` lokal im Browser geöffnet werden.

1. Extension laden
2. `extension/test-page.html` im Browser öffnen
3. Selector `#likeButton` eintragen
4. AutoKlicker starten

Wenn der Zähler steigt, kommt der Klick technisch an. Wenn `isTrusted` auf `false` steht, wurde der Klick per Script erzeugt. Einige Webseiten ignorieren solche Klicks absichtlich.

---

## Dateistruktur

```
extension/
├── manifest.json          # Manifest V3
├── manifest.v2.json       # Legacy Manifest V2
├── test-page.html         # Lokale Testseite fuer Klick-Events
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
