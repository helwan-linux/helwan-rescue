import sys
from pathlib import Path
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget,
    QPushButton, QLabel, QHBoxLayout, QMessageBox,
    QFileDialog, QMenuBar, QToolBar, QStatusBar,
    QDialog, QTextBrowser, QProgressBar
)
import subprocess
import os
from helwan.backend.runner import run_script

BASE_DIR = Path(__file__).resolve().parent
ICON_DIR = BASE_DIR / "resources" / "icons"
SCRIPTS_DIR = BASE_DIR / "backend" / "scripts"

class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Usage Help")
        self.setFixedSize(400, 500)

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
        self.setWindowIcon(QIcon(str(ICON_DIR / "logo.png")))
        self.setFixedSize(520, 750)

        layout = QVBoxLayout()
        layout.setSpacing(16)

        title = QLabel("<h2>🛠 Helwan Rescue Toolkit</h2>", alignment=Qt.AlignCenter)
        layout.addWidget(title)

        buttons_data = [
            ("Fix GRUB / EFI", "fix_grub.sh", "grub_icon.png"),
            ("Repair Network", "fix_network.sh", "network_icon.png"),
            ("Regen Initramfs", "regen_initramfs.sh", "initramfs_icon.png"),
            ("Clean Cache / Logs", "clean_cache.sh", "clean_icon.png"),
            ("Rollback Last Update", "rollback_updates.sh", "rollback_icon.png"),
            ("Fix Permissions", "fix_permissions.sh", "permissions_icon.png"),
            ("Open chroot", "open_chroot.sh", "chroot_icon.png"),
            ("Export Logs to USB", "export_logs.sh", "export_icon.png"),
            ("System Status Check", "system_check.sh", "status_icon.png"),
            ("Safe Exit", "safe_exit.sh", "exit_icon.png"),
        ]

        self.script_buttons = []
        for label, script, icon_name in buttons_data:
            btn = QPushButton(label)
            btn.setMinimumHeight(40)
            icon_path = ICON_DIR / icon_name
            if icon_path.exists():
                btn.setIcon(QIcon(str(icon_path)))
            btn.clicked.connect(lambda _, s=script: self.execute_script(SCRIPTS_DIR / s))
            layout.addWidget(btn)
            self.script_buttons.append(btn)

        path_row = QHBoxLayout()
        self.script_path_label = QLabel(f"Scripts: {SCRIPTS_DIR}")
        change_btn = QPushButton("Change…")
        change_btn.clicked.connect(self.change_script_path)
        path_row.addWidget(self.script_path_label)
        path_row.addWidget(change_btn)
        layout.addLayout(path_row)

        output_label = QLabel("Script Output:")
        layout.addWidget(output_label)
        self.output_text_browser = QTextBrowser()
        self.output_text_browser.setFixedSize(500, 150)
        layout.addWidget(self.output_text_browser)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.create_menu()
        self.setStatusBar(QStatusBar(self))

    def create_menu(self):
        menu = QMenuBar(self)
        self.setMenuBar(menu)

        help_menu = menu.addMenu("Help")
        about_icon = QIcon(str(ICON_DIR / "about.png"))
        help_icon = QIcon(str(ICON_DIR / "help.png"))

        about_act = help_menu.addAction(about_icon, "About")
        about_act.triggered.connect(self.show_about)

        help_act = help_menu.addAction(help_icon, "Usage Help")
        help_act.triggered.connect(self.show_help)

        log_act = help_menu.addAction("Show Operation Log")
        log_act.triggered.connect(self.open_log_file)

        toolbar = QToolBar("Toolbar", self)
        self.addToolBar(toolbar)
        toolbar.setMovable(False)

        toolbar.addAction(about_icon, "About", self.show_about)
        toolbar.addAction(help_icon, "Help", self.show_help)

    def change_script_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select script folder")
        if path:
            global SCRIPTS_DIR
            SCRIPTS_DIR = Path(path)
            self.script_path_label.setText(f"Scripts: {SCRIPTS_DIR}")

    def show_about(self):
        QMessageBox.information(self, "About", "Helwan Rescue Toolkit\nBy Saeed.")

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
            QMessageBox.information(self, "Usage Help", "Help file not found.")

    def open_log_file(self):
        log_path = os.path.expanduser("~/.cache/helwan-rescue/history.log")
        if os.path.exists(log_path):
            subprocess.run(["xdg-open", log_path])
        else:
            QMessageBox.information(self, "Log", "No logs yet.")

    def set_buttons_enabled(self, enabled):
        for btn in self.script_buttons:
            btn.setEnabled(enabled)
        # تعطيل/تفعيل زر تغيير المسار أيضًا
        self.findChild(QPushButton, "Change…").setEnabled(enabled)

    def execute_script(self, script_path):
        script_name = script_path.name

        # إضافة تأكيد للمستخدم للعمليات الخطيرة
        if script_name in ["clean_cache.sh", "rollback_updates.sh"]:
            reply = QMessageBox.question(
                self, 'Confirmation',
                f"Are you sure you want to run '{script_name}'? This operation can significantly alter your system.",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.No:
                self.statusBar().showMessage("Operation cancelled.", 2000)
                return # إلغاء العملية إذا رفض المستخدم

        self.set_buttons_enabled(False)
        self.output_text_browser.clear()
        self.progress_bar.setValue(0)
        self.statusBar().showMessage(f"Running {script_name}...", 2000)

        success, output = run_script(script_path)

        self.progress_bar.setValue(100)
        self.output_text_browser.setText(output)

        if success:
            QMessageBox.information(self, "Success", f"Script '{script_name}' finished successfully.")
        else:
            QMessageBox.warning(self, "Failed", f"Script '{script_name}' failed.")

        self.set_buttons_enabled(True)
        self.statusBar().clearMessage()


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(ICON_DIR / "logo.png")))
    window = RecoveryWindow()
    window.show()
    sys.exit(app.exec_())
