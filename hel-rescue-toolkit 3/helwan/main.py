import sys
from pathlib import Path
from PyQt5.QtCore import Qt, QTimer, QSize, QProcess, QIODevice
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget,
    QPushButton, QLabel, QHBoxLayout, QMessageBox,
    QFileDialog, QMenuBar, QStatusBar,
    QDialog, QTextBrowser, QGridLayout, QLineEdit,
    QInputDialog, QComboBox, QFormLayout # QFormLayout for custom dialogs
)
import subprocess
import os
import stat # Imported stat but not directly used in the current version of main.py
from helwan.backend.runner import run_script_async, check_chroot_status
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


# NEW: Dialog for displaying script output in real-time
class ScriptOutputDialog(QDialog):
    def __init__(self, script_command, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Script Output: {script_command[1].name}") # Use script name for title
        self.setMinimumSize(800, 600)

        self.command = script_command
        self.process = QProcess(self)

        self.layout = QVBoxLayout(self)

        self.output_browser = QTextBrowser(self)
        self.output_browser.setLineWrapMode(QTextBrowser.NoWrap) # Prevent line wrapping for log readability
        self.layout.addWidget(self.output_browser)

        # Progress bar (basic implementation, requires script support for real updates)
        self.progress_bar = QLabel("Running script...") # Placeholder for progress
        self.layout.addWidget(self.progress_bar)

        self.buttons_layout = QHBoxLayout()
        self.save_log_button = QPushButton("Save Log")
        self.save_log_button.clicked.connect(self.save_log)
        self.buttons_layout.addWidget(self.save_log_button)

        self.close_button = QPushButton("Close")
        self.close_button.setEnabled(False) # Enabled after process finishes
        self.close_button.clicked.connect(self.accept)
        self.buttons_layout.addWidget(self.close_button)

        self.layout.addLayout(self.buttons_layout)

        self._connect_signals()
        self.start_process()

    def _connect_signals(self):
        self.process.readyReadStandardOutput.connect(self.read_stdout)
        self.process.readyReadStandardError.connect(self.read_stderr)
        self.process.finished.connect(self.process_finished)
        self.process.errorOccurred.connect(self.process_error)

    def start_process(self):
        # Clear previous output
        self.output_browser.clear()
        self.output_browser.append(f"Starting command: {' '.join(map(str, self.command))}\n")
        
        # Start the process with the command list returned from runner
        # QProcess needs string paths, so map Path objects to strings
        str_command = [str(arg) for arg in self.command]
        self.process.start(str_command[0], str_command[1:])


    def read_stdout(self):
        data = self.process.readAllStandardOutput().data().decode()
        self.output_browser.append(data)
        self.output_browser.verticalScrollBar().setValue(self.output_browser.verticalScrollBar().maximum()) # Auto-scroll

    def read_stderr(self):
        data = self.process.readAllStandardError().data().decode()
        self.output_browser.append(f"<span style='color:red;'>{data}</span>") # Display errors in red
        self.output_browser.verticalScrollBar().setValue(self.output_browser.verticalScrollBar().maximum()) # Auto-scroll

    def process_finished(self, exit_code, exit_status):
        self.progress_bar.setText(f"Script finished with exit code: {exit_code} ({exit_status})")
        self.close_button.setEnabled(True)
        self.output_browser.append("\n--- Script Finished ---")
        if exit_code != 0:
            QMessageBox.warning(self, "Script Finished", f"Script finished with errors. Exit code: {exit_code}")

    def process_error(self, error):
        self.progress_bar.setText(f"Error starting script: {error}")
        self.output_browser.append(f"<span style='color:red;'>Error starting process: {error}</span>")
        self.close_button.setEnabled(True)
        QMessageBox.critical(self, "Process Error", f"Failed to start script process: {error}")

    def save_log(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Log File", "script_output.log", "Log Files (*.log);;All Files (*)", options=options)
        if file_name:
            try:
                with open(file_name, "w", encoding="utf-8") as f:
                    f.write(self.output_browser.toPlainText())
                QMessageBox.information(self, "Save Log", "Log saved successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Save Log Error", f"Could not save log: {e}")

# NEW: Generic input dialog for package names
class PackageInputDialog(QDialog):
    def __init__(self, title, prompt, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(400, 150) # Fixed size for input dialog

        layout = QFormLayout(self)
        
        self.label = QLabel(prompt)
        self.line_edit = QLineEdit(self)
        self.line_edit.setPlaceholderText("Enter package name here...")
        
        layout.addRow(self.label)
        layout.addRow("Package Name:", self.line_edit)

        self.buttons_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.buttons_layout.addWidget(self.ok_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.buttons_layout.addWidget(self.cancel_button)

        layout.addRow(self.buttons_layout)

    def get_package_name(self):
        return self.line_edit.text()


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
            ("downgrade.png", "Downgrade Package", "downgrade_package_handler"), # Changed to handler name
            ("reinstall.png", "Force Reinstall Package", "force_reinstall_package_handler"), # Changed to handler name
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
            button.clicked.connect(lambda: self.execute_script_with_output(script_name_or_handler))
        else:
            # Handle special tasks that require user input (e.g., package name)
            if script_name_or_handler == "downgrade_package_handler": # Updated handler name
                button.clicked.connect(self.downgrade_package_gui) # New GUI handler
            elif script_name_or_handler == "force_reinstall_package_handler": # Updated handler name
                button.clicked.connect(self.force_reinstall_package_gui) # New GUI handler
            # Add more specific handlers here if needed
            else:
                # Fallback for any other custom handlers
                button.clicked.connect(lambda: self.execute_script_with_output(script_name_or_handler)) 
        return button

    # Helper function to get QIcon from path
    def get_icon(self, icon_name):
        icon_path = ICON_DIR / icon_name
        if icon_path.exists():
            return QIcon(str(icon_path))
        return QIcon() # Return an empty QIcon if file doesn't exist

    # NEW: Function to execute script and show output dialog
    def execute_script_with_output(self, script_name, *args):
        script_path = SCRIPTS_DIR / script_name
        if not script_path.exists():
            QMessageBox.critical(self, "Error", f"Script '{script_name}' not found at {script_path}")
            return

        command = run_script_async(script_path, *args)
        output_dialog = ScriptOutputDialog(command, self)
        output_dialog.exec_() # Show dialog modally

    def update_chroot_status(self):
        if check_chroot_status():
            self.chroot_status_label.setText("Chroot Status: Active ✅")
        else:
            self.chroot_status_label.setText("Chroot Status: Not Active 🔴")

    def show_about(self):
        QMessageBox.information(self, "About", "Helwan Rescue Toolkit\nBy Saeed Badrelden\nhelwanlinux@gmail.com.")

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

    # NEW: GUI handler for downgrade package
    def downgrade_package_gui(self):
        dialog = PackageInputDialog("Downgrade Package", "Enter package name to downgrade:", self)
        if dialog.exec_() == QDialog.Accepted:
            pkg_name = dialog.get_package_name().strip()
            if pkg_name:
                self.execute_script_with_output("downgrade_package.sh", pkg_name)
            else:
                QMessageBox.warning(self, "Input Error", "Package name cannot be empty.")

    # NEW: GUI handler for force reinstall package
    def force_reinstall_package_gui(self):
        dialog = PackageInputDialog("Force Reinstall Package", "Enter package name to reinstall:", self)
        if dialog.exec_() == QDialog.Accepted:
            pkg_name = dialog.get_package_name().strip()
            if pkg_name:
                self.execute_script_with_output("force_reinstall_package.sh", pkg_name)
            else:
                QMessageBox.warning(self, "Input Error", "Package name cannot be empty.")

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
