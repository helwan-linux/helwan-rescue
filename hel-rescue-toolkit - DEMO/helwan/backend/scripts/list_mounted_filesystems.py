import sys
import os
import platform
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QMessageBox
)

class MountsLister(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mounted Filesystems")
        self.resize(700, 500)

        layout = QVBoxLayout()

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        self.btn_list = QPushButton("List Mounted Filesystems")
        self.btn_list.clicked.connect(self.list_mounts)
        layout.addWidget(self.btn_list)

        self.setLayout(layout)

    def list_mounts(self):
        self.output.clear()
        # تحقق من صلاحيات الروت على أنظمة يونكس
        if platform.system() in ("Linux", "Darwin"):
            if os.geteuid() != 0:
                self.output.setText("Error: Root access required to list mounts.")
                QMessageBox.warning(self, "Permission Denied", "Please run as root.")
                return

        system = platform.system()
        try:
            if system == "Linux":
                # استخدم findmnt -D -J كما في السكربت
                proc = subprocess.run(
                    ["findmnt", "-D", "-J"],
                    capture_output=True, text=True, check=True
                )
                self.output.setText(proc.stdout)

            elif system == "Darwin":
                # ماك: استخدم أمر mount العادي
                proc = subprocess.run(
                    ["mount"],
                    capture_output=True, text=True, check=True
                )
                self.output.setText(proc.stdout)

            elif system == "Windows":
                # ويندوز: عرض الأقراص فقط (مثال بسيط)
                proc = subprocess.run(
                    ["wmic", "logicaldisk", "get", "name,description"],
                    capture_output=True, text=True, shell=True
                )
                self.output.setText(proc.stdout)

            else:
                self.output.setText(f"Unsupported OS: {system}")

        except subprocess.CalledProcessError as e:
            self.output.setText(f"Failed to list mounts:\n{e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MountsLister()
    window.show()
    sys.exit(app.exec_())
