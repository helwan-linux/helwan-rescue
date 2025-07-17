import os
import sys
import tarfile
import shutil
from datetime import datetime
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QMessageBox
)

def get_usb_mount_point():
    usb_paths = []
    if sys.platform.startswith("linux"):
        media = Path("/media")
        if media.exists():
            for user_dir in media.iterdir():
                for mount in user_dir.iterdir():
                    if mount.is_dir():
                        usb_paths.append(str(mount))
    elif sys.platform.startswith("win"):
        from string import ascii_uppercase
        import ctypes
        DRIVE_REMOVABLE = 2
        for letter in ascii_uppercase:
            path = f"{letter}:/"
            if os.path.exists(path):
                drive_type = ctypes.windll.kernel32.GetDriveTypeW(path)
                if drive_type == DRIVE_REMOVABLE:
                    usb_paths.append(path)
    elif sys.platform.startswith("darwin"):
        volumes = Path("/Volumes")
        usb_paths = [str(p) for p in volumes.iterdir() if p.is_dir() and "Macintosh" not in p.name]

    return usb_paths[0] if usb_paths else None

def create_log_archive(output_path):
    log_dir = Path("/var/log") if os.name != "nt" else Path(os.environ.get("SystemRoot", "C:\\Windows")) / "Logs"
    if not log_dir.exists():
        raise FileNotFoundError(f"Log directory not found: {log_dir}")
    with tarfile.open(output_path, "w:gz") as tar:
        tar.add(str(log_dir), arcname=log_dir.name)

class LogExporter(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Log Exporter")
        self.setFixedSize(400, 150)

        layout = QVBoxLayout()

        self.label = QLabel("Click the button to collect system logs and export to USB (if available).")
        layout.addWidget(self.label)

        self.button = QPushButton("Export Logs")
        self.button.clicked.connect(self.export_logs)
        layout.addWidget(self.button)

        self.setLayout(layout)

    def export_logs(self):
        snapshot_name = f"helwan_logs_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.tar.gz"
        local_dir = Path.home() / "helwan_backups"
        local_dir.mkdir(exist_ok=True)

        archive_path = local_dir / snapshot_name

        try:
            create_log_archive(archive_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create archive:\n{e}")
            return

        usb_mount = get_usb_mount_point()
        if usb_mount:
            try:
                shutil.copy(archive_path, usb_mount)
                QMessageBox.information(self, "Success", f"Logs exported to USB:\n{usb_mount}")
            except Exception as e:
                QMessageBox.warning(self, "Copy Failed", f"Failed to copy to USB:\n{e}\nLogs saved locally at:\n{archive_path}")
        else:
            QMessageBox.information(self, "No USB Found", f"No USB found.\nLogs saved locally at:\n{archive_path}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LogExporter()
    window.show()
    sys.exit(app.exec_())
