import os
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QListWidget, QMessageBox
)
import sys

class DowngradeApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Downgrade Pacman Package")
        self.setFixedSize(500, 400)

        self.package_label = QLabel("Enter package name:")
        self.package_input = QLineEdit()
        self.list_widget = QListWidget()
        self.downgrade_button = QPushButton("Downgrade Selected Version")

        layout = QVBoxLayout()
        layout.addWidget(self.package_label)
        layout.addWidget(self.package_input)
        layout.addWidget(self.list_widget)
        layout.addWidget(self.downgrade_button)
        self.setLayout(layout)

        self.package_input.returnPressed.connect(self.load_cached_versions)
        self.downgrade_button.clicked.connect(self.downgrade_package)

    def load_cached_versions(self):
        self.list_widget.clear()
        package_name = self.package_input.text().strip()

        if not package_name:
            QMessageBox.warning(self, "Input Error", "Please enter a package name.")
            return

        if os.geteuid() != 0:
            QMessageBox.critical(self, "Permission Denied", "This operation requires root privileges.")
            return

        cache_dir = "/var/cache/pacman/pkg"
        try:
            files = sorted(
                [f for f in os.listdir(cache_dir) if f.startswith(package_name + "-")],
                reverse=True
            )
        except FileNotFoundError:
            QMessageBox.critical(self, "Error", "Could not access /var/cache/pacman/pkg/")
            return

        if not files:
            QMessageBox.information(self, "No Versions Found", f"No cached versions found for '{package_name}'.")
            return

        for f in files:
            self.list_widget.addItem(f)

    def downgrade_package(self):
        selected_item = self.list_widget.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "No Selection", "Please select a version from the list.")
            return

        selected_file = selected_item.text()
        package_path = os.path.join("/var/cache/pacman/pkg", selected_file)

        if not os.path.isfile(package_path):
            QMessageBox.critical(self, "File Not Found", f"Package file not found:\n{selected_file}")
            return

        try:
            result = subprocess.run(["pacman", "-U", package_path], check=True)
            QMessageBox.information(
                self,
                "Success",
                f"✅ Package downgraded successfully:\n{selected_file}"
            )
        except subprocess.CalledProcessError:
            QMessageBox.critical(
                self,
                "Error",
                f"❌ Failed to downgrade package.\nCheck for dependency conflicts or invalid package."
            )

if __name__ == "__main__":
    if sys.platform != "linux":
        print("⚠️ This tool only supports Linux systems with pacman.")
        sys.exit(1)

    app = QApplication(sys.argv)
    window = DowngradeApp()
    window.show()
    sys.exit(app.exec_())
