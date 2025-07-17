import sys
import os
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, 
    QLineEdit, QPushButton, QMessageBox
)

class PacmanReinstall(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Force Reinstall Package (pacman)")
        self.setFixedSize(400, 150)

        layout = QVBoxLayout()

        self.label = QLabel("Enter package name to force reinstall:")
        layout.addWidget(self.label)

        self.package_input = QLineEdit()
        layout.addWidget(self.package_input)

        self.reinstall_button = QPushButton("Reinstall Package")
        self.reinstall_button.clicked.connect(self.reinstall_package)
        layout.addWidget(self.reinstall_button)

        self.setLayout(layout)

    def reinstall_package(self):
        package_name = self.package_input.text().strip()
        if not package_name:
            QMessageBox.warning(self, "Input Error", "Please enter a package name.")
            return

        # Check root
        if os.geteuid() != 0:
            QMessageBox.critical(self, "Permission Error", "This operation requires root privileges.")
            return

        # Check if package installed
        result = subprocess.run(
            ["pacman", "-Qs", package_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if result.returncode != 0 or package_name not in result.stdout.decode():
            QMessageBox.critical(self, "Error", f"Package '{package_name}' is not installed.")
            return

        # Run pacman reinstall
        try:
            proc = subprocess.run(
                ["pacman", "-S", package_name, "--noconfirm", "--overwrite", "*"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if proc.returncode == 0:
                QMessageBox.information(
                    self, "Success", f"✅ Package '{package_name}' reinstalled successfully."
                )
            else:
                QMessageBox.critical(
                    self, "Error",
                    f"❌ Failed to reinstall package.\nError:\n{proc.stderr}"
                )
        except Exception as e:
            QMessageBox.critical(self, "Exception", f"An error occurred:\n{e}")

if __name__ == "__main__":
    if not sys.platform.startswith("linux"):
        print("This tool is designed for Linux systems with pacman.")
        sys.exit(1)

    app = QApplication(sys.argv)
    window = PacmanReinstall()
    window.show()
    sys.exit(app.exec_())
