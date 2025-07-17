import os
import platform
import subprocess
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QTextEdit, QMessageBox
)


class JournalLogViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("System Journal Log Viewer")
        self.setMinimumSize(600, 400)

        layout = QVBoxLayout()

        self.info_label = QLabel("أدخل الأمر (مثال: 'boot', 'service systemd-udevd', 'all', أو 'cancel'):")
        layout.addWidget(self.info_label)

        self.command_input = QLineEdit()
        layout.addWidget(self.command_input)

        self.execute_button = QPushButton("تشغيل")
        self.execute_button.clicked.connect(self.run_command)
        layout.addWidget(self.execute_button)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)

        self.setLayout(layout)

        if platform.system() != "Linux":
            QMessageBox.critical(self, "خطأ", "هذا البرنامج يعمل فقط على نظام Linux (systemd/journalctl).")
            self.close()

        if os.geteuid() != 0:
            QMessageBox.critical(self, "صلاحيات مطلوبة", "يجب تشغيل هذا البرنامج كـ root.")
            self.close()

    def run_command(self):
        cmd = self.command_input.text().strip()

        if cmd.lower() == "cancel":
            self.output_text.setText("✅ تم إلغاء العملية.")
            return

        elif cmd.lower() == "boot":
            shell_cmd = ["journalctl", "-b", "-p", "err..warn", "-n", "50", "--no-pager"]

        elif cmd.lower() == "all":
            shell_cmd = ["journalctl", "-n", "50", "--no-pager"]

        elif cmd.startswith("service "):
            service_name = cmd[8:].strip()
            if not service_name:
                self.output_text.setText("❌ خطأ: يجب تحديد اسم الخدمة بعد كلمة 'service'.")
                return
            shell_cmd = ["journalctl", "-u", service_name, "-n", "50", "--no-pager"]

        else:
            shell_cmd = ["journalctl", "-n", "50", "--no-pager"]
            self.output_text.append("⚠️ أمر غير معروف. عرض السجلات الأخيرة فقط.")

        try:
            result = subprocess.run(shell_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                self.output_text.setText(result.stdout + "\n✅ تم عرض السجلات.")
            else:
                self.output_text.setText("❌ فشل في جلب السجلات:\n" + result.stderr)

        except Exception as e:
            self.output_text.setText(f"❌ حدث خطأ:\n{str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = JournalLogViewer()
    viewer.show()
    sys.exit(app.exec_())
