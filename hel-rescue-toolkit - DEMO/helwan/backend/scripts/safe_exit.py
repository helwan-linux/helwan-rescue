import sys
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QTextEdit, QVBoxLayout, QMessageBox
)
from PyQt5.QtGui import QColor, QTextCharFormat, QTextCursor
from PyQt5.QtCore import Qt

class UnmountTool(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Safe System Unmounter")
        self.setGeometry(200, 200, 600, 400)

        self.layout = QVBoxLayout()
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)

        self.btn_unmount = QPushButton("Start Safe Unmount")
        self.btn_exit = QPushButton("Exit")

        self.btn_unmount.clicked.connect(self.start_unmount)
        self.btn_exit.clicked.connect(self.close)

        self.layout.addWidget(self.log_output)
        self.layout.addWidget(self.btn_unmount)
        self.layout.addWidget(self.btn_exit)
        self.setLayout(self.layout)

        self.check_root()

    def check_root(self):
        if subprocess.getoutput("id -u") != "0":
            QMessageBox.warning(self, "Permission Warning",
                "You are not running as root.\nSome unmount operations may fail.")

    def log(self, text, color="black"):
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        self.log_output.setCurrentCharFormat(fmt)
        self.log_output.append(text)
        self.log_output.moveCursor(QTextCursor.End)

    def run_cmd(self, command):
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0, result.stdout.decode().strip() + "\n" + result.stderr.decode().strip()

    def start_unmount(self):
        self.log("🚀 Starting safe unmount process...", "blue")

        dirs = ["run", "sys", "proc", "dev"]
        for d in dirs:
            mount_path = f"/mnt/{d}"
            if self.run_cmd(f"mountpoint -q {mount_path}")[0]:
                self.log(f"  • Unmounting {mount_path}...", "orange")
                ok, out = self.run_cmd(f"umount -R {mount_path}")
                self.log(out, "green" if ok else "red")

        if self.run_cmd("mountpoint -q /mnt/boot/efi")[0]:
            self.log("  • Unmounting /mnt/boot/efi...", "orange")
            ok, out = self.run_cmd("umount /mnt/boot/efi")
            self.log(out, "green" if ok else "red")

        if self.run_cmd("mountpoint -q /mnt")[0]:
            self.log("  • Unmounting /mnt...", "orange")
            ok, out = self.run_cmd("umount /mnt")
            self.log(out, "green" if ok else "red")

        if self.run_cmd("mountpoint -q /mnt")[0]:
            self.log("❌ Failed to unmount all partitions. Check manually.", "red")
        else:
            self.log("✅ All system partitions unmounted safely.", "green")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UnmountTool()
    window.show()
    sys.exit(app.exec_())
