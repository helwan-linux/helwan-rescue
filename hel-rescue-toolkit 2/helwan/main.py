import sys
from pathlib import Path
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget,
    QPushButton, QLabel, QHBoxLayout, QMessageBox,
    QFileDialog, QMenuBar, QStatusBar, # Removed QToolBar as it's not used for main buttons anymore
    QDialog, QTextBrowser, QGridLayout, QLineEdit,
    QInputDialog, QComboBox
)
import subprocess
import os
import stat # Imported stat but not directly used in the current version of main.py
from helwan.backend.runner import run_script, check_chroot_status
from helwan.backend.runner import LOGFILE as runner_logfile

# Set BASE_DIR to the directory containing main.py (i.e., 'helwan/')
BASE_DIR = Path(__file__).resolve().parent

# Now, paths relative to BASE_DIR are correct if resources/ and backend/ are direct subfolders of helwan/
ICON_DIR = BASE_DIR / "resources" / "icons"
SCRIPTS_DIR = BASE_DIR / "backend" / "scripts"

# Update the SCRIPTS_DIR in runner module directly using the calculated SCRIPTS_DIR from main.py
from helwan.backend import runner
runner.SCRIPTS_DIR = SCRIPTS_DIR


class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent) # CORRECTED: Added () after __init__
        self.setWindowTitle("Usage Help")
        self.setFixedSize(700, 700) # Adjusted size for better readability

        layout = QVBoxLayout(self)

        self.text_browser = QTextBrowser(self)
        self.text_browser.setOpenExternalLinks(True)
        layout.addWidget(self.text_browser)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button, alignment=Qt.AlignCenter)

    def set_help_content(self, content):
        self.text_browser.setText(content)


class RecoveryWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Helwan Rescue Toolkit")
        self.setMinimumSize(650, 500) # Reduced minimum window size
        
        # Attempt to set window icon, will print warning if not found
        self.setWindowIcon(self.get_icon("logo.png"))

        self.init_ui()
        self.update_chroot_status()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_chroot_status)
        self.timer.start(5000) # Update chroot status every 5 seconds

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Scripts Path Display (kept at top, without change button)
        scripts_path_layout = QHBoxLayout()
        self.script_path_label = QLabel(f"Scripts: {SCRIPTS_DIR}")
        # Removed "Change..." button for security and simplicity as per user request
        scripts_path_layout.addWidget(self.script_path_label)
        main_layout.addLayout(scripts_path_layout)

        # Chroot Status (kept below scripts path)
        chroot_status_layout = QHBoxLayout()
        self.chroot_status_label = QLabel("Chroot Status: Checking...")
        chroot_status_layout.addWidget(self.chroot_status_label)
        main_layout.addLayout(chroot_status_layout)

        # Grid Layout for Main Buttons (replaces single column and toolbar for main actions)
        buttons_grid_layout = QGridLayout()
        # Add spacing between buttons
        buttons_grid_layout.setHorizontalSpacing(10)
        buttons_grid_layout.setVerticalSpacing(10)

        button_specs = [
            ("chroot.png", "Open Chroot", "open_chroot.sh"),
            ("safe_exit.png", "Safe Exit", "safe_exit.sh"),
            ("grub.png", "Fix GRUB / EFI", "fix_grub.sh"),
            ("network.png", "Repair Network", "fix_network.sh"),
            ("initramfs.png", "Regen Initramfs", "regen_initramfs.sh"),
            ("permissions.png", "Fix Permissions", "fix_permissions.sh"),
            ("rollback.png", "Rollback Last Update", "rollback_updates.sh"),
            ("downgrade.png", "Downgrade Package", "downgrade_package"), # Custom handler
            ("reinstall.png", "Force Reinstall Package", "force_reinstall_package"), # Custom handler
            ("status.png", "System Status Check", "system_check.sh"),
            ("clean.png", "Clean Cache / Logs", "clean_cache.sh"),
            ("export_logs.png", "Export Logs to USB", "export_logs.sh"),
            ("backup.png", "Backup Home Directory", "backup_home.sh"),
            ("mountpoints.png", "List Mounted Filesystems", "list_mounts.sh"),
            ("disk_space.png", "Check Disk Space", "check_disk_space.sh"),
            ("journal.png", "Check Journal Logs", "check_journal.sh"),
            ("reset_password.png", "Reset User Password", "reset_user_password.sh"),
            ("add_user.png", "Create New User", "create_new_user.sh"),
            ("snapshot.png", "Create Snapshot (Btrfs)", "btrfs_create_snapshot.sh"),
            ("restore_snapshot.png", "Restore From Snapshot (Btrfs)", "btrfs_restore_snapshot.sh"),
            ("kill_process.png", "Kill Rogue Processes", "kill_rogue_process.sh"),
        ]

        row, col = 0, 0
        for icon_filename, text, script_name_or_handler in button_specs:
            button = self.create_grid_button(icon_filename, text, script_name_or_handler)
            buttons_grid_layout.addWidget(button, row, col)
            col += 1
            if col >= 3: # 3 buttons per row as requested by user's preference
                col = 0
                row += 1
        
        main_layout.addLayout(buttons_grid_layout)
        # Add a stretchable space to push content to the top if there's extra space
        main_layout.addStretch(1)

        # Menu Bar setup
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")
        file_menu.addAction("Exit", self.close)

        help_menu = menubar.addMenu("Help")
        help_menu.addAction("Usage Help", self.show_help)
        help_menu.addAction("Show Operation Log", self.open_log_file)
        help_menu.addAction("About", self.show_about)

        self.setStatusBar(QStatusBar(self)) # Status Bar


    # Helper function to create QPushButton for the grid
    def create_grid_button(self, icon_filename, text, script_name_or_handler):
        button = QPushButton(text) 
        icon = self.get_icon(icon_filename)
        if icon:
            button.setIcon(icon)
        else:
            # Detailed warning message if icon is not found, printed to console
            print(f"Warning: Icon not found for {icon_filename} at {ICON_DIR / icon_filename}")
        
        button.setIconSize(QSize(48, 48)) # Set icon size for better visibility
        
        # Connect the button's clicked signal to the appropriate slot/handler
        if isinstance(script_name_or_handler, str) and script_name_or_handler.endswith(".sh"):
            # For direct script execution
            button.clicked.connect(lambda: self.run_selected_script(script_name_or_handler))
        else:
            # Handle special tasks that require user input (e.g., package name)
            if script_name_or_handler == "downgrade_package":
                button.clicked.connect(self.downgrade_package)
            elif script_name_or_handler == "force_reinstall_package":
                button.clicked.connect(self.force_reinstall_package)
            # Add more specific handlers here if needed
            else:
                # Fallback for any other custom handlers
                button.clicked.connect(lambda: self.run_selected_script(script_name_or_handler)) 
        return button

    # Helper function to get QIcon from path
    def get_icon(self, icon_name):
        icon_path = ICON_DIR / icon_name
        if icon_path.exists():
            return QIcon(str(icon_path))
        return QIcon() # Return an empty QIcon if file doesn't exist

    # Executes a shell script
    def run_selected_script(self, script_name):
        script_path = SCRIPTS_DIR / script_name
        if script_path.exists():
            run_script(script_path)
        else:
            QMessageBox.critical(self, "Error", f"Script '{script_name}' not found at {script_path}")

    # Updates chroot status label
    def update_chroot_status(self):
        if check_chroot_status():
            self.chroot_status_label.setText("Chroot Status: Active ✅")
        else:
            self.chroot_status_label.setText("Chroot Status: Not Active 🔴")

    # The change_script_path function is now completely removed as per user request for simplicity and security.
    # No "Change..." button in the UI.

    # Shows About dialog
    def show_about(self):
        QMessageBox.information(self, "About", "Helwan Rescue Toolkit\nBy Saeed Badrelden\nhelwanlinux@gmail.com.")

    # Shows Usage Help dialog
    def show_help(self):
        help_file_path = BASE_DIR / "resources" / "usage_help.txt"
        if help_file_path.exists():
            try:
                with open(help_file_path, "r", encoding="utf-8") as f:
                    help_content = f.read()
                
                help_dialog = HelpDialog(self)
                help_dialog.set_help_content(help_content)
                help_dialog.exec_()

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not read help file: {e}")
        else:
            QMessageBox.information(self, "Usage Help", f"Help file not found at: {help_file_path}")

    # Opens the operation log file
    def open_log_file(self):
        log_path = runner_logfile
        if os.path.exists(log_path):
            try:
                # Use startfile for Windows, or xdg-open for Linux
                if sys.platform == "win32":
                    os.startfile(log_path)
                else:
                    subprocess.run(["xdg-open", log_path])
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open log file: {e}\nIs xdg-open installed? (on Linux)")
        else:
            QMessageBox.information(self, "Log", "No operation logs yet.")

    # Prompts for package name and runs downgrade script
    def downgrade_package(self):
        pkg_name, ok = QInputDialog.getText(self, "Downgrade Package", "Enter package name:")
        if ok and pkg_name:
            self.run_selected_script(f"downgrade_package.sh {pkg_name}")

    # Prompts for package name and runs force reinstall script
    def force_reinstall_package(self):
        pkg_name, ok = QInputDialog.getText(self, "Force Reinstall Package", "Enter package name to reinstall:")
        if ok and pkg_name:
            self.run_selected_script(f"force_reinstall_package.sh {pkg_name}")


def main():
    app = QApplication(sys.argv)
    # This line sets the main application icon, not the window icon
    # It might be redundant if RecoveryWindow already sets its own icon
    app.setWindowIcon(QIcon(str(ICON_DIR / "logo.png"))) 
    window = RecoveryWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
