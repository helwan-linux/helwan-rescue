import sys
from pathlib import Path
from PyQt5.QtCore import Qt, QTimer, QSize, QProcess, QIODevice
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget,
    QPushButton, QLabel, QHBoxLayout, QMessageBox,
    QFileDialog, QMenuBar, QStatusBar,
    QDialog, QTextBrowser, QGridLayout, QLineEdit,
    QInputDialog, QComboBox, QFormLayout, QTextEdit,
    QActionGroup # Imported QActionGroup
)
import subprocess
import os
import stat
from helwan.backend.runner import run_script_async, check_chroot_status
from helwan.backend.runner import LOGFILE as runner_logfile

# --- Global Translation System ---
TRANSLATIONS = {
    "en": {
        "Helwan Rescue Toolkit": "Helwan Rescue Toolkit",
        "Scripts:": "Scripts:",
        "Chroot Status:": "Chroot Status:",
        "Chroot Status: Checking...": "Chroot Status: Checking...",
        "Chroot Status: Active ✅": "Chroot Status: Active ✅",
        "Chroot Status: Not Active 🔴": "Chroot Status: Not Active 🔴",
        "File": "File",
        "Exit": "Exit",
        "Help": "Help",
        "Usage Help": "Usage Help",
        "Show Operation Log": "Show Operation Log",
        "About": "About",
        "About Helwan Rescue Toolkit": "Helwan Rescue Toolkit\nBy Saeed Badrelden\nhelwanlinux@gmail.com.",
        "Error": "Error",
        "Script '{}' not found at {}": "Script '{}' not found at {}",
        "Script Output:": "Script Output:",
        "Starting command:": "Starting command:",
        "Running script...": "Running script...",
        "Save Log": "Save Log",
        "Close": "Close",
        "Script finished with exit code: {} ({})": "Script finished with exit code: {} ({})",
        "Script Finished": "Script Finished",
        "Script finished with errors. Exit code: {}": "Script finished with errors. Exit code: {}",
        "Error starting script:": "Error starting script:",
        "Error starting process: {}": "Error starting process: {}",
        "Process Error": "Process Error",
        "Failed to start script process: {}": "Failed to start script process: {}",
        "Save Log File": "Save Log File",
        "Log Files (*.log);;All Files (*)": "Log Files (*.log);;All Files (*)",
        "Save Log": "Save Log",
        "Log saved successfully.": "Log saved successfully.",
        "Save Log Error": "Save Log Error",
        "Could not save log: {}": "Could not save log: {}",
        "Package Name:": "Package Name:",
        "OK": "OK",
        "Cancel": "Cancel",
        "Input Error": "Input Error",
        "Package name cannot be empty.": "Package name cannot be empty.",
        "Log": "Log",
        "No operation logs yet.": "No operation logs yet.",
        "Could not open log file: {}\nIs xdg-open installed? (on Linux)": "Could not open log file: {}\nIs xdg-open installed? (on Linux)",
        "Could not read help file: {}": "Could not read help file: {}",
        "Help file not found at: {}": "Help file not found at: {}",
        # Script names as they appear on buttons
        "Open Chroot": "Open Chroot",
        "Safe Exit": "Safe Exit",
        "Fix GRUB / EFI": "Fix GRUB / EFI",
        "Repair Network": "Repair Network",
        "Regen Initramfs": "Regen Initramfs",
        "Fix Permissions": "Fix Permissions",
        "Rollback Last Update": "Rollback Last Update",
        "Downgrade Package": "Downgrade Package",
        "Force Reinstall Package": "Force Reinstall Package",
        "System Status Check": "System Status Check",
        "Clean Cache / Logs": "Clean Cache / Logs",
        "Export Logs to USB": "Export Logs to USB",
        "Backup Home Directory": "Backup Home Directory",
        "List Mounted Filesystems": "List Mounted Filesystems",
        "Check Disk Space": "Check Disk Space",
        "Check Journal Logs": "Check Journal Logs",
        "Reset User Password": "Reset User Password",
        "Create New User": "Create New User",
        "Create Snapshot (Btrfs)": "Create Snapshot (Btrfs)",
        "Restore From Snapshot (Btrfs)": "Restore From Snapshot (Btrfs)",
        "Kill Rogue Processes": "Kill Rogue Processes",
        "Language": "Language",
        "English": "English",
        "Arabic": "Arabic",
        "Create Custom Script": "Create Custom Script",
        "New Script": "New Script",
        "Script Filename (e.g., my_script.sh)": "Script Filename (e.g., my_script.sh)",
        "Script Content (Bash Script)": "Script Content (Bash Script)",
        "Create": "Create",
        "Script Creation Error": "Script Creation Error",
        "Filename cannot be empty.": "Filename cannot be empty.",
        "Filename must end with .sh": "Filename must end with .sh",
        "Script saved successfully!": "Script saved successfully!",
        "Could not save script: {}": "Could not save script: {}",
        "Save Script": "Save Script",
    },
    "ar": {
        "Helwan Rescue Toolkit": "أداة حلوان للإنقاذ",
        "Scripts:": "السكربتات:",
        "Chroot Status:": "حالة Chroot:",
        "Chroot Status: Checking...": "حالة Chroot: جارٍ التحقق...",
        "Chroot Status: Active ✅": "حالة Chroot: نشط ✅",
        "Chroot Status: Not Active 🔴": "حالة Chroot: غير نشط 🔴",
        "File": "ملف",
        "Exit": "خروج",
        "Help": "مساعدة",
        "Usage Help": "تعليمات الاستخدام",
        "Show Operation Log": "عرض سجل العمليات",
        "About": "حول",
        "About Helwan Rescue Toolkit": "أداة حلوان للإنقاذ\nبواسطة سعيد بدر الدين\nhelwanlinux@gmail.com.",
        "Error": "خطأ",
        "Script '{}' not found at {}": "السكربت '{}' غير موجود في {}",
        "Script Output:": "مخرجات السكربت:",
        "Starting command:": "جارٍ بدء الأمر:",
        "Running script...": "السكربت قيد التشغيل...",
        "Save Log": "حفظ السجل",
        "Close": "إغلاق",
        "Script finished with exit code: {} ({})": "اكتمل السكربت برمز خروج: {} ({})",
        "Script Finished": "اكتمل السكربت",
        "Script finished with errors. Exit code: {}": "اكتمل السكربت بأخطاء. رمز الخروج: {}",
        "Error starting script:": "خطأ في بدء السكربت:",
        "Error starting process: {}": "خطأ في بدء العملية: {}",
        "Process Error": "خطأ في العملية",
        "Failed to start script process: {}": "فشل في بدء عملية السكربت: {}",
        "Save Log File": "حفظ ملف السجل",
        "Log Files (*.log);;All Files (*)": "ملفات السجل (*.log);;جميع الملفات (*)",
        "Save Log": "حفظ السجل",
        "Log saved successfully.": "تم حفظ السجل بنجاح.",
        "Save Log Error": "خطأ في حفظ السجل",
        "Could not save log: {}": "تعذر حفظ السجل: {}",
        "Package Name:": "اسم الحزمة:",
        "OK": "موافق",
        "Cancel": "إلغاء",
        "Input Error": "خطأ في الإدخال",
        "Package name cannot be empty.": "لا يمكن أن يكون اسم الحزمة فارغاً.",
        "Log": "السجل",
        "No operation logs yet.": "لا توجد سجلات عمليات حتى الآن.",
        "Could not open log file: {}\nIs xdg-open installed? (on Linux)": "تعذر فتح ملف السجل: {}\nهل xdg-open مثبت؟ (على لينكس)",
        "Could not read help file: {}": "تعذر قراءة ملف المساعدة: {}",
        "Help file not found at: {}": "ملف المساعدة غير موجود في: {}",
        # Script names as they appear on buttons
        "Open Chroot": "فتح Chroot",
        "Safe Exit": "خروج آمن",
        "Fix GRUB / EFI": "إصلاح GRUB / EFI",
        "Repair Network": "إصلاح الشبكة",
        "Regen Initramfs": "إعادة إنشاء Initramfs",
        "Fix Permissions": "إصلاح الصلاحيات",
        "Rollback Last Update": "العودة لتحديث سابق",
        "Downgrade Package": "تخفيض إصدار حزمة",
        "Force Reinstall Package": "إعادة تثبيت حزمة بالقوة",
        "System Status Check": "فحص حالة النظام",
        "Clean Cache / Logs": "تنظيف ذاكرة التخزين المؤقت / السجلات",
        "Export Logs to USB": "تصدير السجلات إلى USB",
        "Backup Home Directory": "نسخ احتياطي لمجلد المنزل",
        "List Mounted Filesystems": "قائمة أنظمة الملفات المثبتة",
        "Check Disk Space": "فحص مساحة القرص",
        "Check Journal Logs": "فحص سجلات Journal",
        "Reset User Password": "إعادة تعيين كلمة مرور المستخدم",
        "Create New User": "إنشاء مستخدم جديد",
        "Create Snapshot (Btrfs)": "إنشاء لقطة (Btrfs)",
        "Restore From Snapshot (Btrfs)": "الاستعادة من لقطة (Btrfs)",
        "Kill Rogue Processes": "إنهاء العمليات المارقة",
        "Language": "اللغة",
        "English": "الإنجليزية",
        "Arabic": "العربية",
        "Create Custom Script": "إنشاء سكربت مخصص",
        "New Script": "سكربت جديد",
        "Script Filename (e.g., my_script.sh)": "اسم ملف السكربت (مثال: my_script.sh)",
        "Script Content (Bash Script)": "محتوى السكربت (Bash Script)",
        "Create": "إنشاء",
        "Script Creation Error": "خطأ في إنشاء السكربت",
        "Filename cannot be empty.": "لا يمكن أن يكون اسم الملف فارغًا.",
        "Filename must end with .sh": "يجب أن ينتهي اسم الملف بـ .sh",
        "Script saved successfully!": "تم حفظ السكربت بنجاح!",
        "Could not save script: {}": "تعذر حفظ السكربت: {}",
        "Save Script": "حفظ السكربت",
    }
}

current_language = "en" # Default language

# Define LANGUAGES dict here for the language menu
LANGUAGES = {
    "en": "English",
    "ar": "Arabic"
}

def _(text):
    """Translation function."""
    return TRANSLATIONS[current_language].get(text, text) # Return original text if translation not found

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
        super().__init__(parent)
        self.setWindowTitle(_("Usage Help"))
        self.setFixedSize(700, 700)

        layout = QVBoxLayout(self)

        self.text_browser = QTextBrowser(self)
        self.text_browser.setOpenExternalLinks(True)
        layout.addWidget(self.text_browser)

        close_button = QPushButton(_("Close"))
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button, alignment=Qt.AlignCenter)

    def set_help_content(self, content):
        self.text_browser.setText(content)


class ScriptOutputDialog(QDialog):
    def __init__(self, script_command, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("Script Output:") + f" {script_command[1].name}")
        self.setMinimumSize(800, 600)

        self.command = script_command
        self.process = QProcess(self)

        self.layout = QVBoxLayout(self)

        self.output_browser = QTextBrowser(self)
        self.output_browser.setLineWrapMode(QTextBrowser.NoWrap)
        self.layout.addWidget(self.output_browser)

        self.progress_bar = QLabel(_("Running script..."))
        self.layout.addWidget(self.progress_bar)

        self.buttons_layout = QHBoxLayout()
        self.save_log_button = QPushButton(_("Save Log"))
        self.save_log_button.clicked.connect(self.save_log)
        self.buttons_layout.addWidget(self.save_log_button)

        self.close_button = QPushButton(_("Close"))
        self.close_button.setEnabled(False)
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
        self.output_browser.clear()
        self.output_browser.append(_("Starting command:") + f" {' '.join(map(str, self.command))}\n")
        
        str_command = [str(arg) for arg in self.command]
        self.process.start(str_command[0], str_command[1:])

    def read_stdout(self):
        data = self.process.readAllStandardOutput().data().decode()
        self.output_browser.append(data)
        self.output_browser.verticalScrollBar().setValue(self.output_browser.verticalScrollBar().maximum())

    def read_stderr(self):
        data = self.process.readAllStandardError().data().decode()
        self.output_browser.append(f"<span style='color:red;'>{data}</span>")
        self.output_browser.verticalScrollBar().setValue(self.output_browser.verticalScrollBar().maximum())

    def process_finished(self, exit_code, exit_status):
        self.progress_bar.setText(_("Script finished with exit code: {} ({})").format(exit_code, exit_status))
        self.close_button.setEnabled(True)
        self.output_browser.append("\n--- Script Finished ---")
        if exit_code != 0:
            QMessageBox.warning(self, _("Script Finished"), _("Script finished with errors. Exit code: {}").format(exit_code))

    def process_error(self, error):
        self.progress_bar.setText(_("Error starting script:") + f" {error}")
        self.output_browser.append(f"<span style='color:red;'>{_('Error starting process: {}').format(error)}</span>")
        self.close_button.setEnabled(True)
        QMessageBox.critical(self, _("Process Error"), _("Failed to start script process: {}").format(error))

    def save_log(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, _("Save Log File"), "script_output.log", _("Log Files (*.log);;All Files (*)"), options=options)
        if file_name:
            try:
                with open(file_name, "w", encoding="utf-8") as f:
                    f.write(self.output_browser.toPlainText())
                QMessageBox.information(self, _("Save Log"), _("Log saved successfully."))
            except Exception as e:
                QMessageBox.critical(self, _("Save Log Error"), _("Could not save log: {}").format(e))

class PackageInputDialog(QDialog):
    def __init__(self, title, prompt, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_(title))
        self.setFixedSize(400, 150)

        layout = QFormLayout(self)
        
        self.label = QLabel(_(prompt))
        self.line_edit = QLineEdit(self)
        self.line_edit.setPlaceholderText(_("Enter package name here...")) # Placeholder text can be translated
        
        layout.addRow(self.label)
        layout.addRow(_("Package Name:"), self.line_edit)

        self.buttons_layout = QHBoxLayout()
        self.ok_button = QPushButton(_("OK"))
        self.ok_button.clicked.connect(self.accept)
        self.buttons_layout.addWidget(self.ok_button)

        self.cancel_button = QPushButton(_("Cancel"))
        self.cancel_button.clicked.connect(self.reject)
        self.buttons_layout.addWidget(self.cancel_button)

        layout.addRow(self.buttons_layout)

    def get_package_name(self):
        return self.line_edit.text()

# NEW: Dialog for creating a custom script
class CreateScriptDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("Create Custom Script"))
        self.setMinimumSize(600, 500)

        layout = QVBoxLayout(self)

        form_layout = QFormLayout()
        self.filename_input = QLineEdit(self)
        self.filename_input.setPlaceholderText(_("Script Filename (e.g., my_script.sh)"))
        form_layout.addRow(_("New Script"), self.filename_input)
        layout.addLayout(form_layout)

        self.script_content_input = QTextEdit(self)
        self.script_content_input.setPlaceholderText(_("Script Content (Bash Script)"))
        self.script_content_input.setAcceptRichText(False) # Ensure plain text input
        # Add a default shebang
        self.script_content_input.setText("#!/bin/bash\n\n")
        layout.addWidget(self.script_content_input)

        buttons_layout = QHBoxLayout()
        self.create_button = QPushButton(_("Create"))
        self.create_button.clicked.connect(self.save_script)
        buttons_layout.addWidget(self.create_button)

        self.cancel_button = QPushButton(_("Cancel"))
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)
        layout.addLayout(buttons_layout)

    def save_script(self):
        filename = self.filename_input.text().strip()
        content = self.script_content_input.toPlainText()

        if not filename:
            QMessageBox.warning(self, _("Script Creation Error"), _("Filename cannot be empty."))
            return

        if not filename.endswith(".sh"):
            QMessageBox.warning(self, _("Script Creation Error"), _("Filename must end with .sh"))
            return

        script_path = SCRIPTS_DIR / filename
        if script_path.exists():
            reply = QMessageBox.question(self, _("Save Script"),
                                         f"{_('File')} '{filename}' {_('already exists. Overwrite?')}",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No:
                return

        try:
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(content)
            # Make the script executable
            os.chmod(script_path, os.stat(script_path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            QMessageBox.information(self, _("Save Script"), _("Script saved successfully!"))
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, _("Script Creation Error"), _("Could not save script: {}").format(e))


class RecoveryWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(_("Helwan Rescue Toolkit"))
        self.setMinimumSize(650, 500)
        
        self.setWindowIcon(self.get_icon("logo.png"))

        self.init_ui()
        self.retranslateUi() # Initial translation
        self.update_chroot_status()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_chroot_status)
        self.timer.start(5000)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget) # Make main_layout accessible for retranslateUi

        self.scripts_path_layout = QHBoxLayout()
        self.script_path_label = QLabel() # Text set in retranslateUi
        self.scripts_path_layout.addWidget(self.script_path_label)
        self.main_layout.addLayout(self.scripts_path_layout)

        self.chroot_status_layout = QHBoxLayout()
        self.chroot_status_label = QLabel() # Text set in retranslateUi
        self.chroot_status_layout.addWidget(self.chroot_status_label)
        self.main_layout.addLayout(self.chroot_status_layout)

        self.buttons_grid_layout = QGridLayout()
        self.buttons_grid_layout.setHorizontalSpacing(10)
        self.buttons_grid_layout.setVerticalSpacing(10)

        # Store button references to update their text during retranslateUi
        self.buttons = [] 
        button_specs = [
            ("chroot.png", "Open Chroot", "open_chroot.sh"),
            ("safe_exit.png", "Safe Exit", "safe_exit.sh"),
            ("grub.png", "Fix GRUB / EFI", "fix_grub.sh"),
            ("network.png", "Repair Network", "fix_network.sh"),
            ("initramfs.png", "Regen Initramfs", "regen_initramfs.sh"),
            ("permissions.png", "Fix Permissions", "fix_permissions.sh"),
            ("rollback.png", "Rollback Last Update", "rollback_updates.sh"),
            ("downgrade.png", "Downgrade Package", "downgrade_package_handler"),
            ("reinstall.png", "Force Reinstall Package", "force_reinstall_package_handler"),
            ("status.png", "System Status Check", "system_check.sh"),
            ("clean.png", "Clean Cache / Logs", "clean_cache.sh"),
            ("export_logs.png", "Export Logs to USB", "export_logs.sh"),
            ("backup.png", "Backup Home Directory", "backup_home.sh"),
            ("mountpoints.png", "List Mounted Filesystems", "list_mounts.sh"),
            ("disk_space.png", "Check Disk Space", "check_disk_space.py"),
            ("journal.png", "Check Journal Logs", "check_journal.sh"),
            ("reset_password.png", "Reset User Password", "reset_user_password.sh"),
            ("add_user.png", "Create New User", "create_new_user.sh"),
            ("snapshot.png", "Create Snapshot (Btrfs)", "btrfs_create_snapshot.sh"),
            ("restore_snapshot.png", "Restore From Snapshot (Btrfs)", "btrfs_restore_snapshot.sh"),
            ("kill_process.png", "Kill Rogue Processes", "kill_rogue_process.sh"),
            # NEW: Custom Script Creation Button
            ("create.png", "Create Custom Script", "create_custom_script_handler"), # Assuming 'create.png' exists
        ]

        row, col = 0, 0
        for icon_filename, text, script_name_or_handler in button_specs:
            button = self.create_grid_button(icon_filename, text, script_name_or_handler)
            self.buttons.append((button, text)) # Store button and original text for retranslation
            self.buttons_grid_layout.addWidget(button, row, col)
            col += 1
            if col >= 3:
                col = 0
                row += 1
        
        self.main_layout.addLayout(self.buttons_grid_layout)
        self.main_layout.addStretch(1)

        # Menu Bar setup
        self.menubar = self.menuBar()

        self.file_menu = self.menubar.addMenu("") # Text set in retranslateUi
        self.exit_action = self.file_menu.addAction("") # Text set in retranslateUi
        self.exit_action.triggered.connect(self.close)

        self.help_menu = self.menubar.addMenu("") # Text set in retranslateUi
        self.usage_help_action = self.help_menu.addAction("") # Text set in retranslateUi
        self.usage_help_action.triggered.connect(self.show_help)
        self.show_log_action = self.help_menu.addAction("") # Text set in retranslateUi
        self.show_log_action.triggered.connect(self.open_log_file)
        self.about_action = self.help_menu.addAction("") # Text set in retranslateUi
        self.about_action.triggered.connect(self.show_about)

        # Language selection menu
        self.language_menu = self.menubar.addMenu("") # Text set in retranslateUi
        self.language_group = QActionGroup(self)
        self.language_group.setExclusive(True)

        self.lang_actions = {}
        for lang_code, lang_name in LANGUAGES.items():
            action = self.language_menu.addAction(_(lang_name)) # Use translated name for menu item
            action.setCheckable(True)
            action.setData(lang_code)
            self.language_group.addAction(action)
            self.lang_actions[lang_code] = action
            if lang_code == current_language:
                action.setChecked(True)
        
        self.language_group.triggered.connect(self.change_language)

        self.setStatusBar(QStatusBar(self)) # Status Bar

    # NEW: Function to retranslate all UI elements
    def retranslateUi(self):
        global current_language
        self.setWindowTitle(_("Helwan Rescue Toolkit"))
        self.script_path_label.setText(_("Scripts:") + f" {SCRIPTS_DIR}")
        self.chroot_status_label.setText(_("Chroot Status: Checking...")) # Initial state, updated by timer
        
        for button, original_text in self.buttons:
            button.setText(_(original_text))

        self.file_menu.setTitle(_("File"))
        self.exit_action.setText(_("Exit"))
        self.help_menu.setTitle(_("Help"))
        self.usage_help_action.setText(_("Usage Help"))
        self.show_log_action.setText(_("Show Operation Log"))
        self.about_action.setText(_("About"))
        self.language_menu.setTitle(_("Language"))

        # Update language menu item texts
        for lang_code, lang_action in self.lang_actions.items():
            lang_action.setText(_(LANGUAGES[lang_code]))

        # Re-set layout direction for Arabic if needed (might require QApplication restart for full effect)
        if current_language == "ar":
            self.setLayoutDirection(Qt.RightToLeft)
            # For menu bar, sometimes explicit alignment is needed
            self.menuBar().setLayoutDirection(Qt.RightToLeft)
        else:
            self.setLayoutDirection(Qt.LeftToRight)
            self.menuBar().setLayoutDirection(Qt.LeftToRight)

    def change_language(self, action):
        global current_language
        new_lang = action.data()
        if new_lang != current_language:
            current_language = new_lang
            self.retranslateUi()
            # For full RTL support on widgets like QFormLayout, often restart is needed or specific styling
            # For simple labels and buttons, retranslateUi usually suffices.

    def create_grid_button(self, icon_filename, text, script_name_or_handler):
        button = QPushButton(text) 
        icon = self.get_icon(icon_filename)
        if icon:
            button.setIcon(icon)
        else:
            print(f"Warning: Icon not found for {icon_filename} at {ICON_DIR / icon_filename}")
        
        button.setIconSize(QSize(48, 48))
        
        if isinstance(script_name_or_handler, str) and script_name_or_handler.endswith(".sh"):
            button.clicked.connect(lambda: self.execute_script_with_output(script_name_or_handler))
        else:
            if script_name_or_handler == "downgrade_package_handler":
                button.clicked.connect(self.downgrade_package_gui)
            elif script_name_or_handler == "force_reinstall_package_handler":
                button.clicked.connect(self.force_reinstall_package_gui)
            elif script_name_or_handler == "create_custom_script_handler": # NEW Handler
                button.clicked.connect(self.create_custom_script_gui)
            else:
                button.clicked.connect(lambda: self.execute_script_with_output(script_name_or_handler)) 
        return button

    def get_icon(self, icon_name):
        icon_path = ICON_DIR / icon_name
        if icon_path.exists():
            return QIcon(str(icon_path))
        return QIcon()

    def execute_script_with_output(self, script_name, *args):
        script_path = SCRIPTS_DIR / script_name
        if not script_path.exists():
            QMessageBox.critical(self, _("Error"), _("Script '{}' not found at {}").format(script_name, script_path))
            return

        command = run_script_async(script_path, *args)
        output_dialog = ScriptOutputDialog(command, self)
        output_dialog.exec_()

    def update_chroot_status(self):
        if check_chroot_status():
            self.chroot_status_label.setText(_("Chroot Status: Active ✅"))
        else:
            self.chroot_status_label.setText(_("Chroot Status: Not Active 🔴"))

    def show_about(self):
        QMessageBox.information(self, _("About"), _("About Helwan Rescue Toolkit"))

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
                QMessageBox.critical(self, _("Error"), _("Could not read help file: {}").format(e))
        else:
            QMessageBox.information(self, _("Usage Help"), _("Help file not found at: {}").format(help_file_path))

    def open_log_file(self):
        log_path = runner_logfile
        if os.path.exists(log_path):
            try:
                if sys.platform == "win32":
                    os.startfile(log_path)
                else:
                    subprocess.run(["xdg-open", log_path])
            except Exception as e:
                QMessageBox.critical(self, _("Error"), _("Could not open log file: {}\nIs xdg-open installed? (on Linux)").format(e))
        else:
            QMessageBox.information(self, _("Log"), _("No operation logs yet."))

    def downgrade_package_gui(self):
        dialog = PackageInputDialog(_("Downgrade Package"), _("Enter package name to downgrade:"), self)
        if dialog.exec_() == QDialog.Accepted:
            pkg_name = dialog.get_package_name().strip()
            if pkg_name:
                self.execute_script_with_output("downgrade_package.sh", pkg_name)
            else:
                QMessageBox.warning(self, _("Input Error"), _("Package name cannot be empty."))

    def force_reinstall_package_gui(self):
        dialog = PackageInputDialog(_("Force Reinstall Package"), _("Enter package name to reinstall:"), self)
        if dialog.exec_() == QDialog.Accepted:
            pkg_name = dialog.get_package_name().strip()
            if pkg_name:
                self.execute_script_with_output("force_reinstall_package.sh", pkg_name)
            else:
                QMessageBox.warning(self, _("Input Error"), _("Package name cannot be empty."))

    # NEW: Handler for creating custom script via GUI
    def create_custom_script_gui(self):
        dialog = CreateScriptDialog(self)
        dialog.exec_()


def main():
    app = QApplication(sys.argv)
    # This line sets the main application icon
    app.setWindowIcon(QIcon(str(ICON_DIR / "logo.png"))) 
    window = RecoveryWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
