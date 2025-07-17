import sys
import subprocess
import os
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox, QVBoxLayout, QLabel

class GrubRepairApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GRUB Repair Tool")
        self.setGeometry(200, 200, 400, 150)

        layout = QVBoxLayout()

        self.label = QLabel("Click below to reinstall GRUB:")
        layout.addWidget(self.label)

        self.repair_button = QPushButton("🔧 Reinstall GRUB")
        self.repair_button.clicked.connect(self.repair_grub)
        layout.addWidget(self.repair_button)

        self.setLayout(layout)

    def show_message(self, title, message):
        QMessageBox.information(self, title, message)

    def repair_grub(self):
        if os.name != 'nt':  # لو مش Windows
            if os.geteuid() != 0:
                self.show_message("Permission Error", "⚠️ Please run this program as root!")
                return

        efidir = "/boot/efi"
        if not os.path.isdir(efidir):
            self.show_message("Error", f"❌ EFI directory not found at {efidir}")
            return

        self.label.setText("🔧 Repairing GRUB... Please wait...")

        try:
            subprocess.run([
                "grub-install", "--target=x86_64-efi",
                f"--efi-directory={efidir}",
                "--bootloader-id=GRUB",
                "--recheck"
            ], check=True)

            subprocess.run(["grub-mkconfig", "-o", "/boot/grub/grub.cfg"], check=True)

            self.show_message("Success", "✅ GRUB restored successfully.")
        except subprocess.CalledProcessError as e:
            self.show_message("Error", f"❌ Failed: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GrubRepairApp()
    window.show()
    sys.exit(app.exec_())
