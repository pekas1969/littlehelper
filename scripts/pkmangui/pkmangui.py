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

import sys
import subprocess
import shutil
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QPushButton, QLabel, QLineEdit, QFileDialog,
    QTextEdit, QComboBox, QMessageBox
)
from PyQt6.QtGui import QTextCharFormat, QColor, QFont, QSyntaxHighlighter, QTextCursor
from PyQt6.QtCore import Qt, QProcess


class ManSyntaxHighlighter(QSyntaxHighlighter):
    """
    Simple syntax highlighter for manpages.
    Highlights manpage headers (all caps), section titles, options (starting with - or --), and URLs.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rules = []

        # Header format (all caps lines)
        header_format = QTextCharFormat()
        header_format.setForeground(QColor("darkblue"))
        header_format.setFontWeight(QFont.Weight.Bold)
        self.rules.append((r"^[A-Z\s]+$", header_format))

        # Section titles, e.g. "NAME", "SYNOPSIS", "DESCRIPTION"
        section_format = QTextCharFormat()
        section_format.setForeground(QColor("darkgreen"))
        section_format.setFontWeight(QFont.Weight.Bold)
        self.rules.append((r"^[A-Z][A-Z\s]+:$", section_format))

        # Options starting with - or --
        option_format = QTextCharFormat()
        option_format.setForeground(QColor("darkred"))
        self.rules.append((r"(--?\w+)", option_format))

        # URLs (simple pattern)
        url_format = QTextCharFormat()
        url_format.setForeground(QColor("blue"))
        url_format.setFontUnderline(True)
        self.rules.append((r"https?://[^\s]+", url_format))

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            import re
            for match in re.finditer(pattern, text, re.MULTILINE):
                start, end = match.span()
                self.setFormat(start, end - start, fmt)


class ManPageWindow(QWidget):
    """
    Fenster zum Anzeigen der Manpage eines Programms inklusive:
    - Syntaxhighlighting
    - ComboBox mit weiteren Hilfedateien, die zum Programm passen
    - Buttons zum Öffnen des Programmordners und Ausführen des Programms
    """

    def __init__(self, program, base_path):
        super().__init__()
        self.program = program
        self.base_path = Path(base_path)

        self.setWindowTitle(f"Manpage Viewer - {program}")
        self.resize(800, 600)

        layout = QVBoxLayout()

        # Textbereich für Manpage oder "No Manpage found"
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)

        # Syntax-Highlighter anwenden
        self.highlighter = ManSyntaxHighlighter(self.text_edit.document())

        # HBox für Combobox + Buttons
        controls_layout = QHBoxLayout()

        # Label und ComboBox für zusätzliche Hilfedateien
        self.help_label = QLabel("Additional Help Files:")
        controls_layout.addWidget(self.help_label)

        self.help_combo = QComboBox()
        self.help_combo.addItem("-- Select --")
        controls_layout.addWidget(self.help_combo)
        self.help_combo.currentIndexChanged.connect(self.open_help_file)

        # Button: Ordner öffnen
        self.open_folder_btn = QPushButton("Open Folder")
        controls_layout.addWidget(self.open_folder_btn)
        self.open_folder_btn.clicked.connect(self.open_folder)

        # Button: Programm ausführen
        self.run_program_btn = QPushButton("Run Program")
        controls_layout.addWidget(self.run_program_btn)
        self.run_program_btn.clicked.connect(self.run_program)

        layout.addLayout(controls_layout)
        self.setLayout(layout)

        # Manpage laden und anzeigen
        self.load_manpage()

        # Zusätzliche Hilfedateien suchen und in ComboBox einfügen
        self.load_help_files()

    def load_manpage(self):
        """Versucht, die Manpage über das 'man'-Kommando zu laden, ansonsten Fehlermeldung anzeigen."""
        try:
            # man gibt oft ANSI-Farbcodes zurück, wir wandeln sie mit col -b um in reinen Text
            proc1 = subprocess.Popen(["man", self.program], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            proc2 = subprocess.Popen(["col", "-b"], stdin=proc1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            proc1.stdout.close()
            output, _ = proc2.communicate()
            text = output.decode("utf-8", errors="ignore").strip()
            if not text:
                text = "No Manpage found"
        except Exception as e:
            text = "No Manpage found"
        self.text_edit.setPlainText(text)

    def load_help_files(self):
        """Sucht im Programmordner nach Hilfedateien, die den Programmnamen enthalten und populäre Endungen haben."""
        self.help_combo.blockSignals(True)  # Signale blockieren beim Befüllen
        self.help_combo.clear()
        self.help_combo.addItem("-- Select --")

        self.help_files = []
        program_lower = self.program.lower()
        valid_exts = (".txt", ".md", ".help", ".rst", ".readme")

        for f in self.base_path.iterdir():
            if not f.is_file():
                continue
            fname = f.name.lower()
            if program_lower in fname and fname.endswith(valid_exts):
                self.help_files.append(str(f))
                self.help_combo.addItem(f.name)
        self.help_combo.blockSignals(False)

    def open_help_file(self, index):
        """Wenn eine zusätzliche Hilfedatei ausgewählt wird, öffnet sie sich in neuem Fenster."""
        if index <= 0:
            return
        filepath = self.help_files[index - 1]
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            content = f"Could not read file:\n{filepath}\n\n{str(e)}"

        # Neues Fenster öffnen mit dem Inhalt
        win = QWidget()
        win.setWindowTitle(f"Help File - {Path(filepath).name}")
        win.resize(600, 500)
        layout = QVBoxLayout()
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setPlainText(content)
        layout.addWidget(text_edit)
        win.setLayout(layout)
        win.show()

        # Referenz auf Fenster behalten, sonst wird es sofort geschlossen
        self._help_window = win

        # ComboBox zurücksetzen auf "-- Select --"
        self.help_combo.setCurrentIndex(0)

    def open_folder(self):
        """Öffnet den Ordner mit xdg-open."""
        try:
            subprocess.Popen(["xdg-open", str(self.base_path)])
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to open folder:\n{str(e)}")

    def run_program(self):
        """Startet das Programm im Terminal (x-terminal-emulator)."""
        term = shutil.which("x-terminal-emulator") or shutil.which("gnome-terminal") or shutil.which("konsole")
        if term is None:
            QMessageBox.warning(self, "Error", "No supported terminal emulator found (x-terminal-emulator, gnome-terminal, konsole)")
            return

        try:
            # Einfaches Kommando zum Starten im Terminal und Programm ausführen
            subprocess.Popen([term, "-e", self.program])
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to run program:\n{str(e)}")


class MainWindow(QWidget):
    """
    Hauptfenster mit:
    - Pfadauswahl (standardmäßig /usr/bin)
    - Filterfeld zum Eingrenzen der Programme nach Beginn des Namens
    - Liste aller Programme im Verzeichnis, gefiltert nach Eingabe
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manpage Viewer")
        self.resize(600, 800)

        self.layout_main = QVBoxLayout()

        # Pfadauswahl Layout
        path_layout = QHBoxLayout()
        path_label = QLabel("Path:")
        path_layout.addWidget(path_label)

        self.path_edit = QLineEdit("/usr/bin")
        path_layout.addWidget(self.path_edit)

        self.browse_btn = QPushButton("Browse")
        path_layout.addWidget(self.browse_btn)

        self.layout_main.addLayout(path_layout)

        # Filterfeld
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Filter files by name prefix...")
        self.layout_main.addWidget(self.filter_edit)

        # Liste aller Programme
        self.list_widget = QListWidget()
        self.layout_main.addWidget(self.list_widget)

        self.setLayout(self.layout_main)

        # interne Liste aller Dateien (Strings)
        self.all_files = []

        # Signale verbinden
        self.browse_btn.clicked.connect(self.browse_folder)
        self.path_edit.returnPressed.connect(self.load_files)
        self.filter_edit.textChanged.connect(self.filter_list)
        self.list_widget.itemDoubleClicked.connect(self.open_manpage)

        # Initial Dateien laden
        self.load_files()

    def browse_folder(self):
        """Öffnet einen Dialog zur Auswahl eines Verzeichnisses."""
        dir_path = QFileDialog.getExistingDirectory(self, "Select Directory", self.path_edit.text())
        if dir_path:
            self.path_edit.setText(dir_path)
            self.load_files()

    def load_files(self):
        """Lädt alle ausführbaren Dateien im gewählten Verzeichnis und zeigt sie in der Liste an."""
        path = Path(self.path_edit.text())
        if not path.is_dir():
            QMessageBox.warning(self, "Error", "Invalid directory")
            return

        # Nur ausführbare Dateien anzeigen
        files = [f.name for f in path.iterdir() if f.is_file() and os.access(f, os.X_OK)]

        # Sortieren und speichern
        self.all_files = sorted(files)
        self.filter_list(self.filter_edit.text())

    def filter_list(self, text):
        """Filtert die Liste der Dateien, so dass nur Dateien angezeigt werden, die mit 'text' beginnen."""
        text = text.lower()
        self.list_widget.clear()
        for file in self.all_files:
            if file.lower().startswith(text):
                self.list_widget.addItem(file)

    def open_manpage(self, item):
        """Öffnet das Manpage-Fenster für das ausgewählte Programm."""
        program = item.text()
        win = ManPageWindow(program, self.path_edit.text())
        win.show()
        # Referenz behalten, damit Fenster nicht sofort geschlossen wird
        self._manpage_window = win


if __name__ == "__main__":
    import os
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
