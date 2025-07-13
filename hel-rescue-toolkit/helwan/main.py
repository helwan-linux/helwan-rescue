import sys
from pathlib import Path
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget,
    QPushButton, QLabel, QHBoxLayout, QMessageBox,
    QFileDialog, QMenuBar, QToolBar, QStatusBar
)
import subprocess
import os
from helwan.backend.runner import run_script

BASE_DIR = Path(__file__).resolve().parent
ICON_DIR = BASE_DIR / "resources" / "icons"
SCRIPTS_DIR = BASE_DIR / "backend" / "scripts"

class RecoveryWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Helwan Rescue Toolkit")
        self.setWindowIcon(QIcon(str(ICON_DIR / "logo.png")))
        self.setFixedSize(520, 620)

        layout = QVBoxLayout()
        layout.setSpacing(16)

        title = QLabel("<h2>🛠 Helwan Rescue Toolkit</h2>", alignment=Qt.AlignCenter)
        layout.addWidget(title)

        buttons = [
            ("Fix GRUB / EFI", "fix_grub.sh"),
            ("Repair Network", "fix_network.sh"),
            ("Regen Initramfs", "regen_initramfs.sh"),
            ("Clean Cache / Logs", "clean_cache.sh"),
            ("Rollback Last Update", "rollback_updates.sh"),
            ("Fix Permissions", "fix_permissions.sh"),
            ("Open chroot", "open_chroot.sh"),
            ("Export Logs to USB", "export_logs.sh"),
            ("System Status Check", "system_check.sh"),
            ("Safe Exit", "safe_exit.sh"),
        ]

        for label, script in buttons:
            btn = QPushButton(label)
            btn.setMinimumHeight(40)
            btn.clicked.connect(lambda _, s=script: run_script(SCRIPTS_DIR / s))
            layout.addWidget(btn)

        path_row = QHBoxLayout()
        self.script_path_label = QLabel(f"Scripts: {SCRIPTS_DIR}")
        change_btn = QPushButton("Change…")
        change_btn.clicked.connect(self.change_script_path)
        path_row.addWidget(self.script_path_label)
        path_row.addWidget(change_btn)
        layout.addLayout(path_row)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.create_menu()
        self.setStatusBar(QStatusBar(self))

    def create_menu(self):
        menu = QMenuBar(self)
        self.setMenuBar(menu)

        help_menu = menu.addMenu("Help")
        about_icon = QIcon(str(ICON_DIR / "about.png"))
        help_icon = QIcon(str(ICON_DIR / "help.png"))

        about_act = help_menu.addAction(about_icon, "About")
        about_act.triggered.connect(self.show_about)

        help_act = help_menu.addAction(help_icon, "Usage Help")
        help_act.triggered.connect(self.show_help)

        log_act = help_menu.addAction("Show Operation Log")
        log_act.triggered.connect(self.open_log_file)

        toolbar = QToolBar("Toolbar", self)
        self.addToolBar(toolbar)
        toolbar.setMovable(False)

        toolbar.addAction(about_icon, "About", self.show_about)
        toolbar.addAction(help_icon, "Help", self.show_help)

    def change_script_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select script folder")
        if path:
            global SCRIPTS_DIR
            SCRIPTS_DIR = Path(path)
            self.script_path_label.setText(f"Scripts: {SCRIPTS_DIR}")

    def show_about(self):
        QMessageBox.information(self, "About", "Helwan Rescue Toolkit\nBy Saeed.")

    def show_help(self):
        QMessageBox.information(self, "Help", "Click any tool button to run it. Make sure you're root.")

    def open_log_file(self):
        log_path = os.path.expanduser("~/.cache/helwan-rescue/history.log")
        if os.path.exists(log_path):
            subprocess.run(["xdg-open", log_path])
        else:
            QMessageBox.information(self, "Log", "No logs yet.")

def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(ICON_DIR / "logo.png")))
    window = RecoveryWindow()
    window.show()
    sys.exit(app.exec_())
