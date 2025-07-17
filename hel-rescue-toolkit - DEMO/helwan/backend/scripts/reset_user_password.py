import sys
import os
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt

class PasswordResetApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reset User Password")
        self.setFixedSize(400, 180)

        layout = QVBoxLayout()

        self.info_label = QLabel("Enter the username to reset password:")
        layout.addWidget(self.info_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        layout.addWidget(self.username_input)

        self.new_pass_label = QLabel("Enter the new password:")
        layout.addWidget(self.new_pass_label)

        self.new_pass_input = QLineEdit()
        self.new_pass_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.new_pass_input)

        self.confirm_pass_label = QLabel("Confirm the new password:")
        layout.addWidget(self.confirm_pass_label)

        self.confirm_pass_input = QLineEdit()
        self.confirm_pass_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.confirm_pass_input)

        self.reset_button = QPushButton("Reset Password")
        self.reset_button.clicked.connect(self.reset_password)
        layout.addWidget(self.reset_button)

        self.setLayout(layout)

    def is_root(self):
        if sys.platform.startswith('win'):
            # في ويندوز، عادة لازم تشغل كأدمن، لكن تحققها صعب من هنا
            return True  # نفترض نعم، أو تجاهل الفحص
        else:
            # في لينكس وماك
            try:
                return os.geteuid() == 0
            except AttributeError:
                return False

    def reset_password(self):
        username = self.username_input.text().strip()
        new_pass = self.new_pass_input.text()
        confirm_pass = self.confirm_pass_input.text()

        if not username:
            QMessageBox.warning(self, "Input Error", "Please enter a username.")
            return

        if not new_pass:
            QMessageBox.warning(self, "Input Error", "Please enter the new password.")
            return

        if new_pass != confirm_pass:
            QMessageBox.warning(self, "Input Error", "Passwords do not match.")
            return

        if not self.is_root():
            reply = QMessageBox.warning(
                self,
                "Warning",
                "You are not running with administrative/root privileges.\n"
                "Password reset might fail due to insufficient permissions.\n"
                "Do you want to continue?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

        # تحقق من وجود المستخدم فقط في لينكس وماك (لأن id موجود هناك)
        if not sys.platform.startswith('win'):
            try:
                subprocess.check_output(['id', '-u', username])
            except subprocess.CalledProcessError:
                QMessageBox.critical(self, "Error", f"User '{username}' does not exist.")
                return

        try:
            if sys.platform.startswith('win'):
                # ويندوز: تغيير كلمة المرور باستخدام net user
                cmd = ['net', 'user', username, new_pass]
                proc = subprocess.run(cmd, capture_output=True, text=True, shell=True)
                if proc.returncode == 0:
                    QMessageBox.information(self, "Success", f"Password for user '{username}' has been reset.")
                else:
                    QMessageBox.critical(self, "Error", f"Failed to reset password:\n{proc.stderr or proc.stdout}")
            else:
                # لينكس وماك: استخدم chpasswd
                proc = subprocess.Popen(['chpasswd'], stdin=subprocess.PIPE, text=True)
                proc.communicate(f"{username}:{new_pass}")
                if proc.returncode == 0:
                    QMessageBox.information(self, "Success", f"Password for user '{username}' has been reset.")
                else:
                    QMessageBox.critical(self, "Error", "Failed to reset password. Check permissions.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PasswordResetApp()
    window.show()
    sys.exit(app.exec_())
