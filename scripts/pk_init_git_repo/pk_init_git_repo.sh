#version 0.0.1

#============================================================================
#MIT License
#
#Copyright (c) 2025 Peter Kasparak <peter.kasparak@gmail.com>
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#DEALINGS IN THE SOFTWARE.
#============================================================================

#!/bin/bash

# Titel
echo "📦 GitHub Repo Initializer"

# Stelle sicher, dass gh installiert ist
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) ist nicht installiert. Bitte zuerst installieren: https://cli.github.com/"
    exit 1
fi

# Prüfe ob gh authentifiziert ist
if ! gh auth status &>/dev/null; then
    echo "🔐 Du bist nicht bei GitHub angemeldet. Starte gh auth login..."
    gh auth login
    if [ $? -ne 0 ]; then
        echo "❌ Authentifizierung fehlgeschlagen."
        exit 1
    fi
fi

# Benutzer nach Repo-Namen fragen
read -p "📛 Wie soll das neue GitHub-Repository heißen? " repo_name
if [ -z "$repo_name" ]; then
    echo "❌ Kein Repository-Name angegeben. Abbruch."
    exit 1
fi

# Aktuelles Verzeichnis
repo_path=$(pwd)
repo_dirname=$(basename "$repo_path")

# Falls kein Git-Repo, initialisieren
if [ ! -d ".git" ]; then
    echo "📁 Initialisiere neues Git-Repository im aktuellen Verzeichnis ($repo_path)..."
    git init
fi

# Hauptbranch auf main setzen (falls noch nicht)
git symbolic-ref HEAD refs/heads/main

# Repository bei GitHub erstellen (öffentlich)
echo "🌐 Erstelle Remote-Repository '$repo_name' bei GitHub..."
gh repo create "$repo_name" --source=. --public --remote=origin --push
if [ $? -ne 0 ]; then
    echo "❌ Fehler beim Erstellen des Repositories auf GitHub."
    exit 1
fi

# Sicherheitsabfrage
read -p "❓ Möchtest du das lokale Repository '$repo_path' jetzt committen und pushen? (y/N): " answer
if [[ "$answer" =~ ^[YyJj]$ ]]; then
    echo "✅ Dateien werden hinzugefügt, committed und gepusht..."
    git add .
    git commit -m "init: Initial commit"
    git push -u origin main
else
    echo "ℹ️ Vorgang abgebrochen. Du kannst später manuell mit 'git add . && git commit && git push' fortfahren."
fi
