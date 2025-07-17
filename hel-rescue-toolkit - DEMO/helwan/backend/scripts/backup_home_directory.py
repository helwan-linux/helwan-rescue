import os
import shutil
import platform
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel,
    QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal


class BackupThread(QThread):
    progress = pyqtSignal(str)
    error = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, destination_folder):
        super().__init__()
        self.destination_folder = destination_folder

    def run(self):
        try:
            home_dir = str(Path.home())
            dest = os.path.join(self.destination_folder, "home_backup")
            if not os.path.exists(dest):
                os.makedirs(dest)
            for root, dirs, files in os.walk(home_dir):
                for file in files:
                    src_file = os.path.join(root, file)
                    rel_path = os.path.relpath(src_file, home_dir)
                    dest_file = os.path.join(dest, rel_path)
                    os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                    shutil.copy2(src_file, dest_file)
                    self.progress.emit(f"Copied: {rel_path}")
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()


class BackupApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Home Backup Tool")
        self.setGeometry(200, 200, 400, 200)

        self.label = QLabel("Click below to start backup of your home folder.")
        self.label.setAlignment(Qt.AlignCenter)

        self.button = QPushButton("Start Backup")
        self.button.clicked.connect(self.select_folder)

        self.status = QLabel("")
        self.status.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)
        layout.addWidget(self.status)
        self.setLayout(layout)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Select Backup Destination"
        )
        if folder:
            self.status.setText("Starting backup...")
            self.button.setEnabled(False)
            self.thread = BackupThread(folder)
            self.thread.progress.connect(self.update_status)
            self.thread.error.connect(self.show_error)
            self.thread.finished.connect(self.backup_done)
            self.thread.start()

    def update_status(self, message):
        self.status.setText(message)

    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)

    def backup_done(self):
        self.status.setText("✅ Backup completed.")
        self.button.setEnabled(True)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = BackupApp()
    window.show()
    sys.exit(app.exec_())
