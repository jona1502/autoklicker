#!/bin/bash
set -e

echo "🚀 Building AutoKlicker AppImage..."

# PATH für pipx-Binaries sicherstellen
export PATH="$HOME/.local/bin:$PATH"

# 1. PyInstaller ausführen
echo "Step 1: Building with PyInstaller..."
pyinstaller autoklicker-linux.spec --clean

# 2. AppDir-Struktur erstellen
echo "Step 2: Creating AppDir structure..."
mkdir -p dist/AutoKlicker.AppDir/usr/bin
mkdir -p dist/AutoKlicker.AppDir/usr/share/applications
mkdir -p dist/AutoKlicker.AppDir/usr/share/icons/hicolor/256x256/apps

# 3. Binary kopieren
echo "Step 3: Copying binary..."
cp dist/autoklicker dist/AutoKlicker.AppDir/usr/bin/

# 4. Desktop-Datei erstellen
echo "Step 4: Creating desktop entry..."
cat > dist/AutoKlicker.AppDir/autoklicker.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=AutoKlicker
Comment=Professioneller AutoKlicker für Linux
Exec=autoklicker
Icon=autoklicker
Categories=Utility;
Terminal=false
EOF

# 5. Icon kopieren
echo "Step 5: Copying icon..."
cp icons/mauszeiger.png dist/AutoKlicker.AppDir/autoklicker.png
cp icons/mauszeiger.png dist/AutoKlicker.AppDir/usr/share/icons/hicolor/256x256/apps/autoklicker.png

# 6. AppRun-Script erstellen
echo "Step 6: Creating AppRun launcher..."
cat > dist/AutoKlicker.AppDir/AppRun << 'EOF'
#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
exec "${HERE}/usr/bin/autoklicker" "$@"
EOF
chmod +x dist/AutoKlicker.AppDir/AppRun

# 7. AppImage erstellen
echo "Step 7: Creating AppImage..."
ARCH=x86_64 appimagetool dist/AutoKlicker.AppDir

echo ""
echo "✅ Fertig! AppImage erstellt: AutoKlicker-x86_64.AppImage"
echo ""
echo "Zum Ausführen:"
echo "  chmod +x AutoKlicker-x86_64.AppImage"
echo "  ./AutoKlicker-x86_64.AppImage"




