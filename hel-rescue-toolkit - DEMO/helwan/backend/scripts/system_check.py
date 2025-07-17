import sys
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt


def run_command(command):
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.DEVNULL)
        return output.decode().strip()
    except subprocess.CalledProcessError:
        return "Error"


def get_kernel():
    return run_command("uname -r")


def get_ram_total():
    return run_command("free -h | awk '/Mem/ {print $2}'")


def get_disk_free():
    return run_command("df -h / | awk 'NR==2{print $4}'")


def check_internet():
    result = subprocess.call("ping -c 1 archlinux.org", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return "✅ Online" if result == 0 else "❌ Offline"


class SystemInfoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("System Info")
        self.setFixedSize(400, 300)

        font = QFont("Consolas", 11)
        layout = QVBoxLayout()

        self.text_output = QTextEdit()
        self.text_output.setFont(font)
        self.text_output.setReadOnly(True)
        self.text_output.setStyleSheet("background-color: #1e1e1e; color: #00ff88;")

        self.refresh_button = QPushButton("🔄 Refresh")
        self.refresh_button.setStyleSheet("background-color: #444; color: white; padding: 6px;")
        self.refresh_button.clicked.connect(self.update_info)

        self.exit_button = QPushButton("❌ Exit")
        self.exit_button.setStyleSheet("background-color: #a00; color: white; padding: 6px;")
        self.exit_button.clicked.connect(self.close)

        layout.addWidget(self.text_output)
        layout.addWidget(self.refresh_button)
        layout.addWidget(self.exit_button)
        self.setLayout(layout)

        self.update_info()

    def update_info(self):
        info = []
        info.append(f"🖥 Kernel: {get_kernel()}")
        info.append(f"🧠 RAM Total: {get_ram_total()}")
        info.append(f"💽 Disk Free on /: {get_disk_free()}")
        info.append(f"🌐 Internet: {check_internet()}")
        self.text_output.setText("\n".join(info))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SystemInfoApp()
    window.show()
    sys.exit(app.exec_())
