#!/bin/bash

# Ermittelt das aktuelle Verzeichnis, von dem aus das Skript aufgerufen wird
SCRIPT_DIR="$(pwd)"

# Dateiname des Python-Skripts (angenommen es heißt pkrclonegui.py)
SCRIPT_NAME="pkrclonegui.py"

# Vollständiger Pfad zur Python-Datei
SCRIPT_PATH="$SCRIPT_DIR/$SCRIPT_NAME"

# Pfad für die .desktop-Datei
DESKTOP_FILE="$HOME/.local/share/applications/pkrclonegui.desktop"

# Icon-Name (kann angepasst werden)
ICON_NAME="network-server"

# Erstelle die .desktop-Datei mit dynamischem Pfad
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=pkrclonegui
Comment=Manage rclone mounts via system tray
Exec=python3 $SCRIPT_PATH
Icon=$ICON_NAME
Terminal=false
Type=Application
Categories=Network;Internet;
StartupNotify=true
EOF

echo "Desktop entry created at $DESKTOP_FILE"
echo "You may need to run 'update-desktop-database' or log out and back in."
