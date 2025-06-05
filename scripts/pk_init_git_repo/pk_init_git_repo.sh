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

# Abbrechen bei Fehlern
set -e

# Funktion: GitHub-Login prüfen
check_gh_auth() {
    if ! gh auth status &>/dev/null; then
        echo "Du bist noch nicht bei GitHub (gh) angemeldet. Starte Login..."
        gh auth login
    else
        echo "GitHub-Login erkannt: $(gh auth status --show-token | grep 'Logged in to')"
    fi
}

# GitHub-Login prüfen
check_gh_auth

# Benutzer nach Repository-Namen fragen
read -p "Name des neuen GitHub-Repositories: " repo_name

# Prüfen, ob Eingabe leer ist
if [[ -z "$repo_name" ]]; then
    echo "Fehler: Repository-Name darf nicht leer sein."
    exit 1
fi

# Repository-Ordner erstellen
mkdir "$repo_name"
cd "$repo_name"

# Git-Repo initialisieren
git init -b main

# Beispieldatei hinzufügen
echo "# $repo_name" > README.md
git add README.md
git commit -m "Initial commit"

# GitHub-Repository erstellen und pushen
gh repo create "$repo_name" --source=. --remote=origin --push --public

echo "✅ Repository '$repo_name' wurde erfolgreich erstellt und gepusht."
