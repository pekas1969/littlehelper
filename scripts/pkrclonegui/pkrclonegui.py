# pkrclonegui.py

import sys
import os
import configparser
import subprocess
from functools import partial

from PyQt6.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QMessageBox
)
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QTimer


RCLONE_CONF_PATH = os.path.expanduser("~/.config/rclone/rclone.conf")


def get_rclone_remotes():
    """Liest alle Remotenamen aus der rclone.conf-Datei."""
    if not os.path.exists(RCLONE_CONF_PATH):
        return []

    config = configparser.ConfigParser()
    config.read(RCLONE_CONF_PATH)
    return config.sections()


def is_service_active(remote):
    """Prüft, ob der systemd-user-service rclone@<remote> aktiv ist."""
    try:
        result = subprocess.run(
            ["systemctl", "--user", "is-active", f"rclone@{remote}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True
        )
        return result.stdout.strip() == "active"
    except Exception:
        return False


def start_service(remote):
    """Startet den systemd-user-Service."""
    subprocess.run(["systemctl", "--user", "start", f"rclone@{remote}"])


def stop_service(remote):
    """Stoppt den systemd-user-Service."""
    subprocess.run(["systemctl", "--user", "stop", f"rclone@{remote}"])


class RcloneTrayApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(QIcon.fromTheme("network-server"))
        self.menu = QMenu()

        self.build_menu()
        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.show()

        # regelmäßige Aktualisierung des Menüs
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_menu)
        self.timer.start(10000)  # alle 10 Sekunden

    def build_menu(self):
        self.menu.clear()
        remotes = get_rclone_remotes()

        if not remotes:
            self.menu.addAction("No rclone remotes found").setEnabled(False)
        else:
            for remote in remotes:
                submenu = QMenu(remote, self.menu)

                mount_action = QAction("Mount", submenu)
                unmount_action = QAction("Unmount", submenu)

                active = is_service_active(remote)
                mount_action.setEnabled(not active)
                unmount_action.setEnabled(active)

                mount_action.triggered.connect(partial(self.mount_remote, remote))
                unmount_action.triggered.connect(partial(self.unmount_remote, remote))

                submenu.addAction(mount_action)
                submenu.addAction(unmount_action)

                self.menu.addMenu(submenu)

        self.menu.addSeparator()
        quit_action = QAction("Quit", self.menu)
        quit_action.triggered.connect(self.app.quit)
        self.menu.addAction(quit_action)

    def refresh_menu(self):
        self.build_menu()

    def mount_remote(self, remote):
        start_service(remote)
        self.tray_icon.showMessage("Rclone Mount", f"{remote} mounted.", QSystemTrayIcon.MessageIcon.Information)
        QTimer.singleShot(1500, self.refresh_menu)

    def unmount_remote(self, remote):
        stop_service(remote)
        self.tray_icon.showMessage("Rclone Unmount", f"{remote} unmounted.", QSystemTrayIcon.MessageIcon.Information)
        QTimer.singleShot(1500, self.refresh_menu)

    def run(self):
        self.app.exec()


if __name__ == "__main__":
    app = RcloneTrayApp()
    app.run()
