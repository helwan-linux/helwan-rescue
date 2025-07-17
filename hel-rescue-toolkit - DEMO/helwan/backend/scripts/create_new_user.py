import sys
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QMessageBox
)
import os
import platform

class UserCreator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("User Creator (Root Required)")
        self.setGeometry(300, 300, 400, 200)

        self.label = QLabel("Enter new username:")
        self.username_input = QLineEdit()
        self.create_button = QPushButton("Create User")
        self.create_button.clicked.connect(self.create_user)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.create_button)
        self.setLayout(layout)

    def create_user(self):
        username = self.username_input.text().strip()
        if not username:
            QMessageBox.warning(self, "Error", "Please enter a username.")
            return

        if os.geteuid() != 0:
            QMessageBox.critical(self, "Permission Error", "This operation requires root privileges.")
            return

        try:
            # Check if user already exists
            result = subprocess.run(
                ["id", "-u", username],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            if result.returncode == 0:
                QMessageBox.critical(self, "Error", f"User '{username}' already exists.")
                return

            # Create user with home directory and bash shell
            subprocess.check_call(["useradd", "-m", "-s", "/bin/bash", username])

            # Set user password (calls passwd command)
            QMessageBox.information(self, "Password", f"Set password for '{username}' in terminal.")
            subprocess.call(["passwd", username])

            # Add to sudo group (wheel in Arch/Fedora, sudo in Ubuntu/Debian)
            group = "wheel" if self.distro_is_arch_or_fedora() else "sudo"
            subprocess.check_call(["usermod", "-aG", group, username])

            QMessageBox.information(
                self,
                "Success",
                f"✅ User '{username}' created and added to '{group}' group."
            )

        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Error", f"Failed to create user: {e}")

    def distro_is_arch_or_fedora(self):
        try:
            with open("/etc/os-release") as f:
                contents = f.read().lower()
                return "arch" in contents or "fedora" in contents
        except Exception:
            return False

if __name__ == "__main__":
    if platform.system() == "Windows":
        print("⚠️ This script is designed for Linux/Mac only.")
        sys.exit(1)

    app = QApplication(sys.argv)
    window = UserCreator()
    window.show()
    sys.exit(app.exec_())
