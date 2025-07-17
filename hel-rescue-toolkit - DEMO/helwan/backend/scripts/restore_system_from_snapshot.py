import sys
import subprocess
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QListWidget, QMessageBox, QHBoxLayout
)


class SnapshotRestorer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Btrfs Snapshot Restore")
        self.setMinimumWidth(450)

        self.layout = QVBoxLayout()
        self.label = QLabel("🔍 Detecting Btrfs snapshots in /.snapshots ...")
        self.layout.addWidget(self.label)

        self.snapshot_list = QListWidget()
        self.layout.addWidget(self.snapshot_list)

        self.button_layout = QHBoxLayout()
        self.restore_button = QPushButton("🛠 Restore Selected Snapshot")
        self.restore_button.clicked.connect(self.confirm_restore)
        self.button_layout.addWidget(self.restore_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.close)
        self.button_layout.addWidget(self.cancel_button)

        self.layout.addLayout(self.button_layout)
        self.setLayout(self.layout)

        self.detect_filesystem()

    def detect_filesystem(self):
        try:
            result = subprocess.run(["stat", "-f", "-c", "%T", "/"], stdout=subprocess.PIPE, text=True)
            fs_type = result.stdout.strip()
            if fs_type != "btrfs":
                QMessageBox.critical(self, "Unsupported Filesystem",
                                     f"Root filesystem is '{fs_type}', not Btrfs.\nThis tool only supports Btrfs.")
                self.close()
                return

            self.load_snapshots()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not detect filesystem: {str(e)}")
            self.close()

    def load_snapshots(self):
        snapshot_dir = "/.snapshots"
        if not os.path.isdir(snapshot_dir):
            QMessageBox.critical(self, "Error", f"Snapshot directory '{snapshot_dir}' not found.")
            self.close()
            return

        try:
            cmd = ["btrfs", "subvolume", "list", "-o", "/"]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
            lines = result.stdout.splitlines()

            found = False
            for line in lines:
                if snapshot_dir in line:
                    path = line.split("path ")[-1]
                    self.snapshot_list.addItem(path.replace(f"{snapshot_dir}/", ""))
                    found = True

            if not found:
                QMessageBox.information(self, "No Snapshots", "No Btrfs snapshots found in /.snapshots.")
                self.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to list snapshots: {str(e)}")
            self.close()

    def confirm_restore(self):
        selected_item = self.snapshot_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "No Selection", "Please select a snapshot to restore.")
            return

        snapshot = selected_item.text()
        full_path = f"/.snapshots/{snapshot}"
        instructions = f"""
⚠️ Restoring from snapshot: {snapshot}

This operation requires booting from a Live USB.

Manual steps to perform:

1. Mount your Btrfs root partition.
2. Run the following command to set snapshot as default:
    sudo btrfs subvolume set-default <subvol_id>

You can get the subvolume ID using:
    sudo btrfs subvolume list / | grep '{full_path}'

3. Reboot your system.

⚠️ WARNING: This GUI does NOT perform actual restoration, it guides only.
"""

        QMessageBox.information(self, "Restore Instructions", instructions)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SnapshotRestorer()
    window.show()
    sys.exit(app.exec_())
