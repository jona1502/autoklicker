# AutoKlicker

Ein professioneller AutoKlicker für Windows, entwickelt in Python mit tkinter GUI.

## Features

- **Click-Intervall**: Konfigurierbare Intervalle in Stunden, Minuten, Sekunden und Millisekunden
- **Click-Optionen**: 
  - Maus-Button: Links, Rechts, Mittel
  - Click-Typ: Single, Double, Triple
- **Wiederholung**: 
  - X-mal wiederholen
  - Bis gestoppt (unendlich)
- **Cursor-Position**:
  - Aktuelle Position
  - Feste Koordinaten (Pick Location mit transparentem Overlay)
- **Hotkeys**: 
  - **F6 = Start** (AutoKlicker starten)
  - **F7 = Stop** (AutoKlicker stoppen)
  - Konfigurierbar über "Hotkey setting"
- **Record & Playback**: Aufzeichnen und Abspielen von Click-Sequenzen
- **Settings-Persistierung**: Automatisches Speichern und Laden der Einstellungen
- **Multi-Monitor Support**: Unterstützt negative Koordinaten für mehrere Bildschirme

## Installation

1. Python 3.8 oder höher installieren

2. Dependencies installieren:
```bash
pip install -r requirements.txt
```

## Verwendung

### Starten der Anwendung

```bash
python src/main.py
```

### Grundlegende Verwendung

1. **Click-Intervall einstellen**: Geben Sie die gewünschte Zeit in Stunden, Minuten, Sekunden und Millisekunden ein.

2. **Click-Optionen wählen**: 
   - Wählen Sie den Maus-Button (Links/Rechts/Mittel)
   - Wählen Sie den Click-Typ (Single/Double/Triple)

3. **Wiederholung konfigurieren**:
   - "Repeat": Geben Sie die Anzahl der Wiederholungen ein
   - "Repeat until stopped": Klickt unendlich bis gestoppt

4. **Position wählen**:
   - "Current location": Verwendet die aktuelle Mausposition beim Start
   - "Pick location": Klicken Sie auf "Pick location" → transparentes Overlay erscheint → Linksklick an gewünschter Position

5. **Starten**: Klicken Sie auf "Start (F6)" oder drücken Sie **F6**

6. **Stoppen**: Klicken Sie auf "Stop (F7)" oder drücken Sie **F7**

**⚠️ WICHTIG: Merke dir die Hotkeys!**
- **F6 = Start**
- **F7 = Stop** (zum Notfall-Stoppen!)

Wenn der AutoKlicker nicht mehr stoppt, drücke einfach **F7**!

### Hotkeys konfigurieren

1. Klicken Sie auf "Hotkey setting"
2. Geben Sie die gewünschten Hotkeys ein
3. Optional: Wählen Sie Modifier-Keys (Ctrl, Alt, Shift)
4. Klicken Sie auf "OK"

### Record & Playback

1. Klicken Sie auf "Record & Playback"
2. **Aufzeichnen**:
   - Klicken Sie auf "Start Recording"
   - Führen Sie die gewünschten Clicks aus
   - Klicken Sie auf "Stop Recording"
3. **Abspielen**:
   - Klicken Sie auf "Play" um die Sequenz abzuspielen
4. **Speichern/Laden**:
   - "Save": Speichert die Sequenz als JSON-Datei
   - "Load": Lädt eine gespeicherte Sequenz

## Projektstruktur

```
autoklicker/
├── src/
│   ├── main.py                 # Entry Point
│   ├── gui/                    # GUI-Komponenten
│   │   ├── main_window.py
│   │   ├── hotkey_dialog.py
│   │   └── record_window.py
│   ├── core/                   # Core-Funktionalität
│   │   ├── clicker.py
│   │   ├── mouse_controller.py
│   │   └── hotkey_manager.py
│   ├── services/               # Services
│   │   ├── recorder.py
│   │   └── settings_manager.py
│   ├── models/                 # Data Models
│   │   ├── settings.py
│   │   └── click_event.py
│   └── utils/                  # Utilities
│       └── validators.py
├── data/                       # Daten (Settings)
├── requirements.txt
└── README.md
```

## Technische Details

- **GUI**: tkinter
- **Maus-Steuerung**: pynput
- **Hotkeys**: keyboard
- **Threading**: threading (für Background-Tasks)
- **Settings**: JSON-basierte Persistierung

## Hinweise

- Die Anwendung benötigt Administrator-Rechte für globale Hotkeys (je nach System)
- Auf Windows funktionieren Hotkeys am zuverlässigsten
- Die Settings werden automatisch in `data/settings.json` gespeichert

## GitHub Release (EXE)

Bei jedem Version-Tag baut GitHub Actions automatisch `AutoKlicker.exe` und veröffentlicht sie als Release.

```bash
# Version in src/gui/theme.py anpassen (APP_VERSION), dann:
git add .
git commit -m "Release v1.1.1"
git tag v1.1.1
git push origin main
git push origin v1.1.1
```

Nach dem Push des Tags erscheint unter **Releases** auf GitHub die fertige EXE zum Download.
Zusätzlich werden die Browser-Pakete `AutoKlicker-Chrome-MV3.zip`, `AutoKlicker-Brave-MV3.zip` und `AutoKlicker-Legacy-MV2.zip` veröffentlicht.

Lokaler Build (ohne GitHub):

```bash
build.bat
```

## Python oder C#?

| | Python (aktuell) | C# (WPF/WinUI) |
|---|---|---|
| Entwicklung | Schnell, Code bleibt nutzbar | Neuschreiben nötig |
| EXE-Größe | ~15–25 MB (PyInstaller) | Kleiner (~2–5 MB) |
| UI | tkinter, funktional | Moderner, natives Windows-Look |
| Hotkeys/Maus | pynput + keyboard | WinAPI / InputSimulator |

**Empfehlung:** Bei Python bleiben, solange Features und UI im Griff sind. Ein Wechsel zu C# lohnt sich vor allem für kleinere EXEs, Code-Signing und ein natives Windows-UI — nicht zwingend für die Kernfunktion.

## Lizenz

Dieses Projekt ist für den persönlichen Gebrauch bestimmt.

