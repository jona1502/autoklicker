# AutoKlicker - EXE Build Anleitung

## Quick Start

### Option 1: Automatisches Build-Script (Empfohlen)
```bash
build.bat
```

### Option 2: Manuell
```bash
# 1. PyInstaller installieren
pip install -r requirements.txt

# 2. EXE erstellen
pyinstaller autoklicker.spec

# 3. EXE ist fertig in:
dist/AutoKlicker.exe
```

## Was passiert beim Build?

1. **PyInstaller** packt alle Python-Dateien, Dependencies und Module in eine einzige EXE
2. Die EXE ist **standalone** - kein Python muss installiert sein
3. Settings werden in `data/settings.json` gespeichert (wird automatisch erstellt)

## Build-Optionen

### Icon hinzufügen
1. Erstelle/besorge ein `icon.ico` File (256x256 oder kleiner)
2. Kopiere es ins Hauptverzeichnis
3. Öffne `autoklicker.spec` und ändere:
   ```python
   icon='icon.ico'  # Statt icon=None
   ```
4. Führe Build erneut aus

### Debug-Version (mit Console)
Wenn die EXE nicht funktioniert, kannst du eine Debug-Version erstellen:
1. Öffne `autoklicker.spec`
2. Ändere: `console=True`  (Statt `console=False`)
3. Build erneut ausführen
4. Jetzt siehst du Fehlermeldungen im Console-Fenster

## Troubleshooting

### "Modul nicht gefunden" Fehler
- Füge das Modul in `autoklicker.spec` unter `hiddenimports` hinzu
- Beispiel: `'dein_modul_name'`

### EXE startet nicht
- Erstelle Debug-Version (siehe oben)
- Prüfe ob alle Dependencies in `requirements.txt` sind
- Versuche: `pyinstaller --clean autoklicker.spec`

### Antivirus blockiert EXE
- PyInstaller EXEs werden manchmal als Virus erkannt (False Positive)
- Füge `dist/AutoKlicker.exe` als Ausnahme hinzu
- Oder: Signiere die EXE mit einem Code-Signing-Zertifikat

## Fertige EXE verteilen

Die EXE kann einfach kopiert werden:
- Keine Installation nötig
- Keine Python-Installation nötig
- Funktioniert auf jedem Windows PC
- Settings werden lokal im `data/` Ordner gespeichert

## Build-Dateien

Nach dem Build existieren folgende Ordner:
- `build/` - Temporäre Build-Dateien (kann gelöscht werden)
- `dist/` - **Hier ist die fertige EXE!**
- `dist/AutoKlicker.exe` - **Das ist die finale EXE**

Tipp: Du kannst den gesamten `dist/` Ordner als ZIP verteilen!

