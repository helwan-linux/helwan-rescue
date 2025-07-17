import sys
import os
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QMessageBox
)

class InitramfsRegenerator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Initramfs Regenerator")
        self.resize(500, 300)

        self.layout = QVBoxLayout()

        self.info_label = QLabel("Press the button to regenerate initramfs for all kernels.")
        self.layout.addWidget(self.info_label)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.layout.addWidget(self.output)

        self.run_button = QPushButton("Regenerate initramfs")
        self.run_button.clicked.connect(self.regenerate_initramfs)
        self.layout.addWidget(self.run_button)

        self.setLayout(self.layout)

    def regenerate_initramfs(self):
        self.output.clear()
        self.output.append("Detecting installed kernels in /boot ...")

        try:
            kernels = subprocess.check_output(
                "ls /boot/vmlinuz-* 2>/dev/null | sed 's/.*vmlinuz-//'",
                shell=True, text=True).strip().split('\n')
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to detect kernels: {e}")
            return

        if not kernels or kernels == ['']:
            QMessageBox.critical(self, "Error", "No kernel files found in /boot.")
            return

        self.output.append(f"Detected kernels: {', '.join(kernels)}")
        self.output.append("Running mkinitcpio -P to regenerate all initramfs images...")

        try:
            process = subprocess.Popen(
                ["mkinitcpio", "-P"],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True
            )
            for line in process.stdout:
                self.output.append(line.strip())

            process.wait()
            if process.returncode == 0:
                self.output.append("\n✅ Initramfs regenerated successfully for all kernels.")
            else:
                self.output.append("\n❌ Failed to regenerate initramfs. Check logs for errors.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to run mkinitcpio: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InitramfsRegenerator()
    window.show()
    sys.exit(app.exec_())
