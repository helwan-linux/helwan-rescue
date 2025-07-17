import sys
import os
import subprocess
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QPushButton, QTextEdit, QMessageBox
)
from PyQt5.QtCore import Qt

class PermissionsFixerAllOS(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fix Common Directory Permissions (Admin/Root Required)")
        self.setFixedSize(600, 500)

        layout = QVBoxLayout()

        self.label = QLabel("Press the button to fix common directory permissions.\nRequires Admin/Root privileges.")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)

        self.button = QPushButton("Fix Permissions")
        self.button.clicked.connect(self.fix_permissions)
        layout.addWidget(self.button)

        self.setLayout(layout)

    def log_message(self, message):
        self.log.append(message)
        QApplication.processEvents()

    def is_admin(self):
        # Windows admin check
        if sys.platform.startswith("win"):
            try:
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin()
            except Exception:
                return False
        else:
            # Unix-like root check
            return hasattr(os, "geteuid") and os.geteuid() == 0

    def fix_permissions(self):
        self.log.clear()

        if not self.is_admin():
            QMessageBox.critical(self, "Permission Denied", "This operation requires Admin (Windows) or Root (Linux/macOS) privileges.")
            return

        if sys.platform.startswith("win"):
            self.fix_permissions_windows()
        elif sys.platform.startswith("linux") or sys.platform.startswith("darwin"):
            self.fix_permissions_unix()
        else:
            QMessageBox.warning(self, "Unsupported OS", "Your operating system is not supported by this tool.")
            return

    def fix_permissions_unix(self):
        self.log_message("Fixing directory permissions on Unix-like system...")

        # Fix /home directories permissions to 755
        home_path = Path("/home")
        if home_path.exists():
            self.log_message("  • Fixing /home directory permissions to 755...")
            self.run_command("find /home -maxdepth 1 -type d -print0 | xargs -0 chmod 755")

            # Fix ownership and permissions for each user home directory to 700
            try:
                for user_home in home_path.iterdir():
                    if user_home.is_dir():
                        username = user_home.name
                        self.log_message(f"    - Setting ownership for {username}'s home directory...")
                        self.run_command(f"chown -R {username}:{username} '{user_home}'")
                        self.log_message(f"    - Setting permissions for {username}'s home directory to 700...")
                        self.run_command(f"chmod 700 '{user_home}'")
            except Exception as e:
                self.log_message(f"Error processing /home users: {e}")
        else:
            self.log_message("Warning: /home directory does not exist.")

        # Fix root directory permissions
        root_path = Path("/root")
        if root_path.exists():
            self.log_message("  • Fixing /root directory permissions to 700 and ownership to root:root...")
            self.run_command("chmod 700 /root")
            self.run_command("chown -R root:root /root")
        else:
            self.log_message("Warning: /root directory does not exist.")

        # Fix /tmp directory permissions to 1777
        tmp_path = Path("/tmp")
        if tmp_path.exists():
            self.log_message("  • Fixing /tmp directory permissions to 1777...")
            self.run_command("chmod 1777 /tmp")
        else:
            self.log_message("Warning: /tmp directory does not exist.")

        self.log_message("✅ Permissions fix completed on Unix-like system.")

    def fix_permissions_windows(self):
        self.log_message("Fixing directory permissions on Windows...")

        # Common Windows user profiles path
        users_path = Path("C:/Users")
        if not users_path.exists():
            self.log_message("Error: Could not find C:/Users directory.")
            return

        # Note: Windows permission fixing is complex and varies.
        # Here we will try to reset permissions to default for user folders.
        # This is a simplified approach using 'icacls' command.

        try:
            # Fix Users folder permission inheritance enabled
            self.log_message("  • Resetting permissions on C:/Users...")
            result = subprocess.run(f'icacls "C:\\Users" /reset /T /C', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out = result.stdout.decode()
            err = result.stderr.decode()
            if out:
                self.log_message(f"> {out}")
            if err:
                self.log_message(f"! {err}")
            if result.returncode != 0:
                self.log_message("Warning: Failed to reset all permissions on C:/Users")
            else:
                self.log_message("  • Permissions reset on C:/Users successfully.")

            # Fix TEMP folder permissions
            temp_path = Path(os.getenv('TEMP') or "C:/Windows/Temp")
            if temp_path.exists():
                self.log_message(f"  • Resetting permissions on {temp_path}...")
                result = subprocess.run(f'icacls "{temp_path}" /reset /T /C', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out = result.stdout.decode()
                err = result.stderr.decode()
                if out:
                    self.log_message(f"> {out}")
                if err:
                    self.log_message(f"! {err}")
                if result.returncode != 0:
                    self.log_message(f"Warning: Failed to reset permissions on {temp_path}")
                else:
                    self.log_message(f"  • Permissions reset on {temp_path} successfully.")
            else:
                self.log_message(f"Warning: TEMP directory {temp_path} does not exist.")

        except Exception as e:
            self.log_message(f"Exception while fixing Windows permissions: {e}")

        self.log_message("✅ Permissions fix completed on Windows.")

    def run_command(self, cmd):
        try:
            result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out = result.stdout.decode().strip()
            err = result.stderr.decode().strip()
            if out:
                self.log_message(f"> {out}")
            if err:
                self.log_message(f"! {err}")
            return result.returncode
        except Exception as e:
            self.log_message(f"Exception running command: {e}")
            return -1


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PermissionsFixerAllOS()
    window.show()
    sys.exit(app.exec_())
