@echo off
echo ============================================
echo   AutoKlicker EXE Build Script
echo ============================================
echo.

REM PyInstaller installieren falls nicht vorhanden
echo [1/3] Checking PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller nicht gefunden - installiere...
    pip install pyinstaller
) else (
    echo PyInstaller bereits installiert!
)
echo.

REM Alte Build-Dateien löschen
echo [2/3] Cleaning old build files...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo.

REM EXE erstellen
echo [3/3] Building EXE...
pyinstaller autoklicker.spec
echo.

REM Erfolgsmeldung
if exist dist\AutoKlicker.exe (
    echo ============================================
    echo   BUILD ERFOLGREICH!
    echo ============================================
    echo.
    echo Die EXE befindet sich in: dist\AutoKlicker.exe
    echo.
    echo Du kannst jetzt die EXE starten:
    echo   dist\AutoKlicker.exe
    echo.
) else (
    echo ============================================
    echo   BUILD FEHLGESCHLAGEN!
    echo ============================================
    echo.
    echo Bitte prüfe die Fehlermeldungen oben.
    echo.
)

pause

