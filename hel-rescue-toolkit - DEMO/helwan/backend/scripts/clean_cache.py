import os
import sys
import shutil
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt
import subprocess
import platform


class CleanerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("System Cleaner")
        self.setGeometry(200, 200, 400, 200)
        self.setLayout(QVBoxLayout())

        self.label = QLabel("Click the button to clean system cache and old logs.")
        self.label.setAlignment(Qt.AlignCenter)

        self.clean_button = QPushButton("🧹 Start Cleaning")
        self.clean_button.clicked.connect(self.clean_system)

        self.layout().addWidget(self.label)
        self.layout().addWidget(self.clean_button)

    def clean_system(self):
        os_type = platform.system()

        if os_type != "Linux":
            QMessageBox.critical(self, "Unsupported OS", "This tool is for Linux only.")
            return

        if os.geteuid() != 0:
            QMessageBox.critical(self, "Permission Error", "Please run this tool as root.")
            return

        try:
            self.label.setText("🧹 Cleaning pacman cache...")
            subprocess.run(["pacman", "-Scc"], input=b'y\n', check=True)

            self.label.setText("🗑 Removing logs older than 7 days...")
            subprocess.run(["find", "/var/log", "-type", "f", "-mtime", "+7", "-exec", "rm", "-f", "{}", ";"], check=True)

            QMessageBox.information(self, "Done", "✅ System cleaned successfully.")
            self.label.setText("✅ All done!")

        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Error", f"Error occurred: {e}")
            self.label.setText("❌ Cleaning failed.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CleanerApp()
    window.show()
    sys.exit(app.exec_())
