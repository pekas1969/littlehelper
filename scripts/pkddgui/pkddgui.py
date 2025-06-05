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
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QComboBox, QFileDialog, QCheckBox, QDialog, QMessageBox, QProgressBar, QTextEdit
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

# -------------------------------------------------------------------
#Funktion zum Abrufen der Blockgeräte
def get_block_devices():
    """
    Ruft alle verfügbaren Blockgeräte und deren Partitionen ab und gibt sie als Liste zurück.
    """
    try:
        output = subprocess.check_output(['lsblk', '-ln', '-o', 'NAME,SIZE'], text=True)
        devices = []
        for line in output.strip().split('\n'):
            parts = line.split()
            if len(parts) == 2:
                name, size = parts
                devices.append((f"/dev/{name}", size))
        return devices
    except Exception as e:
        return [("Fehler beim Laden", str(e))]

# -------------------------------------------------------------------
#Klasse für den Hintergrundprozess (dd-Kommando)
class DDWorker(QThread):
    """
    Führt das dd-Kommando in einem separaten Thread aus.
    """
    progress = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, source, dest, dry_run):
        super().__init__()
        self.source = source
        self.dest = dest
        self.dry_run = dry_run
        self._abort = False

    def run(self):
        if self.dry_run:
            self.progress.emit(f"[DRY RUN] dd if={self.source} of={self.dest} bs=4M status=progress")
        else:
            try:
                process = subprocess.Popen(
                    ['dd', f'if={self.source}', f'of={self.dest}', 'bs=4M', 'status=progress'],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
                )
                while True:
                    if self._abort:
                        process.terminate()
                        self.progress.emit("Abgebrochen.")
                        break
                    line = process.stdout.readline()
                    if not line:
                        break
                    self.progress.emit(line.strip())
                process.wait()
            except Exception as e:
                self.progress.emit(f"Fehler: {e}")
        self.finished.emit()

    def abort(self):
        """
        Setzt das Abbruch-Flag, um den Prozess zu beenden.
        """
        self._abort = True

# -------------------------------------------------------------------
# Dialog zur Anzeige des Fortschritts
class ProgressDialog(QDialog):
    """
    Zeigt den Fortschritt des dd-Kommandos an.
    """
    def __init__(self, worker):
        super().__init__()
        self.setWindowTitle("Fortschritt")
        self.resize(500, 300)

        self.worker = worker
        self.layout = QVBoxLayout()
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.progress = QProgressBar()
        self.abort_button = QPushButton("Abbrechen")

        self.layout.addWidget(self.output)
        self.layout.addWidget(self.progress)
        self.layout.addWidget(self.abort_button)
        self.setLayout(self.layout)

        self.abort_button.clicked.connect(self.on_abort)

        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def on_progress(self, text):
        """
        Aktualisiert die Textausgabe mit dem aktuellen Fortschritt.
        """
        self.output.append(text)

    def on_finished(self):
        """
        Wird aufgerufen, wenn der dd-Prozess abgeschlossen ist.
        """
        self.abort_button.setText("Beenden")

    def on_abort(self):
        """
        Behandelt den Abbruch des Prozesses.
        """
        if self.worker.isRunning():
            self.worker.abort()
        else:
            self.accept()

# -------------------------------------------------------------------
# Fenster für die Auswahl von Quelle und Ziel
class DiskToImageWindow(QWidget):
    """
    Fenster zur Auswahl der Quell-Partition und des Ziel-Imagepfads.
    """
    back_to_menu = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Disk/Partition → Image")
        self.resize(400, 200)

        layout = QVBoxLayout()

        self.source_combo = QComboBox()
        self.devices = get_block_devices()
        for dev, size in self.devices:
            self.source_combo.addItem(f"{dev} ({size})", dev)

        self.target_button = QPushButton("Ziel-Image-Datei wählen...")
        self.target_label = QLabel("Kein Ziel gewählt.")
        self.dry_run = QCheckBox("Dry Run (nur anzeigen, nicht ausführen)")
        self.run_button = QPushButton("Starten")
        self.back_button = QPushButton("Zurück zur Aktionsauswahl")

        layout.addWidget(QLabel("Quelle:"))
        layout.addWidget(self.source_combo)
        layout.addWidget(self.target_button)
        layout.addWidget(self.target_label)
        layout.addWidget(self.dry_run)
        layout.addWidget(self.run_button)
        layout.addWidget(self.back_button)
        self.setLayout(layout)

        self.target_button.clicked.connect(self.choose_file)
        self.run_button.clicked.connect(self.start_dd)
        self.back_button.clicked.connect(self.go_back)

    def go_back(self):
        """
        Schließt das aktuelle Fenster und signalisiert die Rückkehr zum Hauptmenü.
        """
        self.close()
        self.back_to_menu.emit()

    def choose_file(self):
        """
        Öffnet einen Dialog zur Auswahl der Ziel-Image-Datei.
        """
        path, _ = QFileDialog.getSaveFileName(self, "Ziel-Datei wählen", "", "Image-Dateien (*.img);;Alle Dateien (*)")
        if path:
            self.target_label.setText(path)
            self.target_path = path

    def start_dd(self):
        source = self.source_combo.currentData()
        target = getattr(self, "target_path", None)
        if not target:
            self.target_label.setText("❗ Ziel nicht gewählt!")
            return
    
        # Überprüft den verfügbaren Speicherplatz
        free = shutil.disk_usage(target.rsplit("/", 1)[0]).free
        source_size = self.get_device_size_bytes(source)
        if source_size and source_size > free:
            self.target_label.setText("❗ Nicht genug Speicherplatz!")
            return
    
        # Sicherheitsabfrage
        reply = QMessageBox.question(
            self,
            "Bestätigung erforderlich",
            f"Sind Sie sicher, dass Sie den Vorgang mit dd starten möchten?\n\nQuelle: {source}\nZiel: {target}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return  # Abbrechen, wenn der Benutzer nicht bestätigt

        dry = self.dry_run.isChecked()
        self.worker = DDWorker(source, target, dry)
        self.dialog = ProgressDialog(self.worker)
        self.dialog.exec()

## -------------------------------------------------------------------
#Diskgrösse ermitteln
    def get_device_size_bytes(self, device):
        """
        Gibt die Größe des Geräts in Bytes zurück.
        """
        try:
            output = subprocess.check_output(['blockdev', '--getsize64', device], text=True)
            return int(output.strip())
        except Exception:
            return None

## -------------------------------------------------------------------
#Image to Disk/Partition
class ImageToDiskWindow(QWidget):
    """
    Fenster zur Auswahl des Imagepfads und der Zielpartition.
    """
    back_to_menu = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Image → Disk/Partition")
        self.resize(400, 200)

        layout = QVBoxLayout()

        self.image_button = QPushButton("Image-Datei wählen...")
        self.image_label = QLabel("Kein Image gewählt.")
        self.dest_combo = QComboBox()
        self.devices = get_block_devices()
        for dev, size in self.devices:
            self.dest_combo.addItem(f"{dev} ({size})", dev)

        self.dry_run = QCheckBox("Dry Run (nur anzeigen, nicht ausführen)")
        self.run_button = QPushButton("Starten")
        self.back_button = QPushButton("Zurück zur Aktionsauswahl")

        layout.addWidget(self.image_button)
        layout.addWidget(self.image_label)
        layout.addWidget(QLabel("Ziel:"))
        layout.addWidget(self.dest_combo)
        layout.addWidget(self.dry_run)
        layout.addWidget(self.run_button)
        layout.addWidget(self.back_button)
        self.setLayout(layout)

        self.image_button.clicked.connect(self.choose_file)
        self.run_button.clicked.connect(self.start_dd)
        self.back_button.clicked.connect(self.go_back)

    def go_back(self):
        """
        Schließt das aktuelle Fenster und signalisiert die Rückkehr zum Hauptmenü.
        """
        self.close()
        self.back_to_menu.emit()

    def choose_file(self):
        """
        Öffnet einen Dialog zur Auswahl der Image-Datei.
        """
        path, _ = QFileDialog.getOpenFileName(self, "Image-Datei wählen", "", "Image-Dateien (*.img);;Alle Dateien (*)")
        if path:
            self.image_label.setText(path)
            self.image_path = path

    def start_dd(self):
        """
        Startet den dd-Prozess mit den ausgewählten Parametern.
        """
        image = getattr(self, "image_path", None)
        dest = self.dest_combo.currentData()
        if not image:
            self.image_label.setText("❗ Image nicht gewählt!")
            return

        # Überprüft die Größe des Images und den verfügbaren Speicherplatz
        image_size = os.path.getsize(image)
        dest_size = self.get_device_size_bytes(dest)
        if dest_size and image_size > dest_size:
            self.image_label.setText("❗ Image größer als Zielgerät!")
            return

        dry = self.dry_run.isChecked()
        self.worker = DDWorker(image, dest, dry)
        self.dialog = ProgressDialog(self.worker)
        self.dialog.exec()

    def get_device_size_bytes(self, device):
        """
        Gibt die Größe des Geräts in Bytes zurück.
        """
        try:
            output = subprocess.check_output(['blockdev', '--getsize64', device], text=True)
            return int(output.strip())
        except Exception:
            return None
            
# Klonen
class DiskToDiskWindow(QWidget):
    """
    Fenster zur Auswahl des Quell- und Ziellaufwerks für das Klonen.
    """
    back_to_menu = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Laufwerk → Laufwerk")
        self.resize(400, 200)

        layout = QVBoxLayout()

        self.source_combo = QComboBox()
        self.dest_combo = QComboBox()
        self.devices = get_block_devices()
        for dev, size in self.devices:
            self.source_combo.addItem(f"{dev} ({size})", dev)
            self.dest_combo.addItem(f"{dev} ({size})", dev)

        self.dry_run = QCheckBox("Dry Run (nur anzeigen, nicht ausführen)")
        self.run_button = QPushButton("Starten")
        self.back_button = QPushButton("Zurück zur Aktionsauswahl")

        layout.addWidget(QLabel("Quelllaufwerk:"))
        layout.addWidget(self.source_combo)
        layout.addWidget(QLabel("Ziellaufwerk:"))
        layout.addWidget(self.dest_combo)
        layout.addWidget(self.dry_run)
        layout.addWidget(self.run_button)
        layout.addWidget(self.back_button)
        self.setLayout(layout)

        self.run_button.clicked.connect(self.start_dd)
        self.back_button.clicked.connect(self.go_back)

    def go_back(self):
        """
        Schließt das aktuelle Fenster und signalisiert die Rückkehr zum Hauptmenü.
        """
        self.close()
        self.back_to_menu.emit()

    def start_dd(self):
        """
        Startet den dd-Prozess mit den ausgewählten Parametern.
        """
        source = self.source_combo.currentData()
        dest = self.dest_combo.currentData()

        if source == dest:
            QMessageBox.warning(self, "Fehler", "Quell- und Ziellaufwerk dürfen nicht identisch sein.")
            return

        # Überprüft die Größe der Laufwerke
        source_size = self.get_device_size_bytes(source)
        dest_size = self.get_device_size_bytes(dest)
        if source_size and dest_size and source_size > dest_size:
            QMessageBox.warning(self, "Fehler", "Ziellaufwerk ist kleiner als das Quelllaufwerk.")
            return

        dry = self.dry_run.isChecked()
        self.worker = DDWorker(source, dest, dry)
        self.dialog = ProgressDialog(self.worker)
        self.dialog.exec()

    def get_device_size_bytes(self, device):
        """
        Gibt die Größe des Geräts in Bytes zurück.
        """
        try:
            output = subprocess.check_output(['blockdev', '--getsize64', device], text=True)
            return int(output.strip())
        except Exception:
            return None

# -------------------------------------------------------------------
#Hauptmenü zur Funktionsauswahl
class ActionSelector(QDialog):
    """
    Hauptmenü zur Auswahl der gewünschten Aktion.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aktion auswählen")
        self.resize(300, 150)

        layout = QVBoxLayout()
        self.combo = QComboBox()
        self.combo.addItems([
            "Disk/Partition → Image",
            "Image → Disk/Partition",
            "Laufwerk → Laufwerk"
        ])
        self.button = QPushButton("Ausführen")

        layout.addWidget(QLabel("Aktion wählen:"))
        layout.addWidget(self.combo)
        layout.addWidget(self.button)
        self.setLayout(layout)

        self.button.clicked.connect(self.launch)

    def launch(self):
        """
        Startet die ausgewählte Aktion.
        """
        index = self.combo.currentIndex()
        if index == 0:
            self.hide()
            self.window = DiskToImageWindow()
            self.window.back_to_menu.connect(self.show_again)
            self.window.show()
        elif index == 1:
            self.hide()
            self.window = ImageToDiskWindow()
            self.window.back_to_menu.connect(self.show_again)
            self.window.show()
        elif index == 2:
            self.hide()
            self.window = DiskToDiskWindow()
            self.window.back_to_menu.connect(self.show_again)
            self.window.show()

    def show_again(self):
        """
        Zeigt das Hauptmenü erneut an.
        """
        self.window.close()
        self.show()


# -------------------------------------------------------------------
# Starten der Anwendung
def main():
    """
    Startet die Anwendung.
    """
    app = QApplication(sys.argv)
    selector = ActionSelector()
    selector.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

