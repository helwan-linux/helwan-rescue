import sys
import os
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QListWidget, QPushButton, QTextEdit, QMessageBox
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt

PKG_CACHE_PATH = "/var/cache/pacman/pkg"

def get_cached_packages():
    try:
        files = sorted(
            (f for f in os.listdir(PKG_CACHE_PATH) if f.endswith(".pkg.tar.zst")),
            key=lambda f: os.path.getmtime(os.path.join(PKG_CACHE_PATH, f)),
            reverse=True
        )
        return files
    except Exception as e:
        return []

def rollback_package(pkg_filename):
    try:
        full_path = os.path.join(PKG_CACHE_PATH, pkg_filename)
        result = subprocess.run(["pkexec", "pacman", "-U", full_path, "--noconfirm"],
                                capture_output=True, text=True)
        return result.stdout + result.stderr
    except Exception as e:
        return str(e)

class RollbackApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Helwan Package Rollback")
        self.setGeometry(200, 200, 600, 500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Rollback Cached Package")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.pkg_list = QListWidget()
        self.pkg_list.addItems(get_cached_packages())
        layout.addWidget(self.pkg_list)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)

        self.rollback_button = QPushButton("Rollback Selected Package")
        self.rollback_button.clicked.connect(self.perform_rollback)
        layout.addWidget(self.rollback_button)

        self.exit_button = QPushButton("Exit")
        self.exit_button.clicked.connect(self.close)
        layout.addWidget(self.exit_button)

        self.setLayout(layout)

    def perform_rollback(self):
        selected = self.pkg_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select a package first.")
            return
        pkg_name = selected.text()
        self.log_area.append(f"Rolling back: {pkg_name}")
        output = rollback_package(pkg_name)
        self.log_area.append(output)
        self.pkg_list.clear()
        self.pkg_list.addItems(get_cached_packages())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = RollbackApp()
    win.show()
    sys.exit(app.exec_())
