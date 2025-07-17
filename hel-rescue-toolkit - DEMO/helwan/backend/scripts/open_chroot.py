import sys
import os
import subprocess
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QTextEdit, QMessageBox, QFileDialog, QInputDialog
)

class ChrootSetupApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chroot Setup Helper")
        self.setGeometry(300, 300, 700, 500)

        layout = QVBoxLayout()

        self.info_label = QLabel("This tool detects and mounts a root partition for chroot operations.\n"
                                 "You may be prompted to select a partition if auto-detection fails.\n"
                                 "Requires root privileges.")
        layout.addWidget(self.info_label)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)

        self.btn_start = QPushButton("Start Mounting Process")
        self.btn_start.clicked.connect(self.start_mounting)
        layout.addWidget(self.btn_start)

        self.setLayout(layout)

    def log_message(self, msg):
        self.log.append(msg)
        QApplication.processEvents()

    def check_root(self):
        if os.name == "nt":
            self.log_message("⚠️ This script is designed for Linux/macOS systems only.")
            return False
        try:
            if os.geteuid() != 0:
                self.log_message("Error: Root access required for this operation.")
                QMessageBox.critical(self, "Error", "Root access required. Please run as root (sudo).")
                return False
        except AttributeError:
            # On some systems os.geteuid may not exist
            self.log_message("Warning: Unable to verify root access.")
        return True

    def start_mounting(self):
        self.log.clear()
        if not self.check_root():
            return

        # Unmount /mnt if mounted
        self.log_message("Checking if /mnt is mounted...")
        if self.is_mounted("/mnt"):
            self.log_message("Warning: /mnt is already mounted. Attempting to unmount submounts and /mnt.")
            for subdir in ["dev", "proc", "sys", "run"]:
                mount_point = f"/mnt/{subdir}"
                if self.is_mounted(mount_point):
                    self.unmount(mount_point)
            self.unmount("/mnt")
            if self.is_mounted("/mnt"):
                self.log_message("Error: Could not unmount /mnt. Please unmount manually and try again.")
                QMessageBox.critical(self, "Error", "Could not unmount /mnt. Please unmount manually and try again.")
                return

        root_part = self.detect_root_partition()
        if not root_part:
            root_part, ok = QInputDialog.getText(self, "Manual Input Required",
                                                 "Automatic root partition detection failed.\n"
                                                 "Please enter root partition path (e.g. /dev/sda1):")
            if not ok or not root_part:
                self.log_message("Operation cancelled by user.")
                return
            if not Path(root_part).exists():
                QMessageBox.critical(self, "Error", f"Partition '{root_part}' does not exist.")
                return

        self.log_message(f"Selected root partition: {root_part}")

        if not self.mount_partition(root_part, "/mnt"):
            self.log_message(f"Error: Failed to mount {root_part} to /mnt.")
            QMessageBox.critical(self, "Error", f"Failed to mount {root_part} to /mnt.")
            return

        self.log_message("Mounting essential directories...")
        self.create_dirs(["dev", "proc", "sys", "run", "boot/efi"], base="/mnt")

        for d in ["dev", "proc", "sys", "run"]:
            self.mount_bind(f"/{d}", f"/mnt/{d}")

        efi_partition = self.detect_efi_partition()
        if efi_partition:
            self.log_message(f"Detected EFI partition: {efi_partition}")
            if not self.is_mounted("/mnt/boot/efi"):
                if self.mount_partition(efi_partition, "/mnt/boot/efi"):
                    self.log_message("EFI partition mounted to /mnt/boot/efi.")
                else:
                    self.log_message(f"Warning: Failed to mount EFI partition {efi_partition}.")

        self.log_message("✅ System successfully mounted to /mnt. Ready for chroot operations.")
        QMessageBox.information(self, "Success", "System successfully mounted to /mnt.")

    def run_cmd(self, cmd):
        try:
            result = subprocess.run(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return result.returncode, result.stdout.strip(), result.stderr.strip()
        except Exception as e:
            return 1, "", str(e)

    def is_mounted(self, path):
        ret, out, err = self.run_cmd(["mountpoint", "-q", path])
        return ret == 0

    def unmount(self, path):
        ret, out, err = self.run_cmd(["umount", "-R", path])
        if ret != 0:
            ret, out, err = self.run_cmd(["umount", path])
        if ret == 0:
            self.log_message(f"Unmounted {path}")
        else:
            self.log_message(f"Failed to unmount {path}: {err}")

    def detect_root_partition(self):
        self.log_message("Detecting root partition...")
        ret, out, err = self.run_cmd(["lsblk", "-o", "NAME,TYPE,FSTYPE,MOUNTPOINT"])
        if ret != 0:
            self.log_message(f"lsblk error: {err}")
            return None

        lines = out.splitlines()
        for line in lines:
            parts = line.split()
            if len(parts) < 4:
                continue
            name, typ, fstype, mountpoint = parts[0], parts[1], parts[2], " ".join(parts[3:])
            if typ == "part" and fstype in ("ext4", "btrfs", "xfs", "f2fs") and mountpoint == "":
                # Mount temporarily and check dirs
                tmp_dir = Path("/tmp/chroot_tmp_mount")
                tmp_dir.mkdir(exist_ok=True)
                ret_m, out_m, err_m = self.run_cmd(["mount", f"/dev/{name}", str(tmp_dir)])
                if ret_m == 0:
                    etc_dir = tmp_dir / "etc"
                    home_dir = tmp_dir / "home"
                    usr_dir = tmp_dir / "usr"
                    var_dir = tmp_dir / "var"
                    if etc_dir.is_dir() and home_dir.is_dir() and usr_dir.is_dir() and var_dir.is_dir():
                        self.run_cmd(["umount", str(tmp_dir)])
                        tmp_dir.rmdir()
                        return f"/dev/{name}"
                    self.run_cmd(["umount", str(tmp_dir)])
                tmp_dir.rmdir()
        return None

    def mount_partition(self, partition, target):
        Path(target).mkdir(parents=True, exist_ok=True)
        ret, out, err = self.run_cmd(["mount", partition, target])
        if ret != 0:
            self.log_message(f"Mount error: {err}")
            return False
        self.log_message(f"Mounted {partition} to {target}")
        return True

    def create_dirs(self, dirs, base="/"):
        for d in dirs:
            p = Path(base) / d
            p.mkdir(parents=True, exist_ok=True)

    def mount_bind(self, src, dest):
        ret, out, err = self.run_cmd(["mount", "--bind", src, dest])
        if ret == 0:
            self.log_message(f"Bind-mounted {src} to {dest}")
        else:
            self.log_message(f"Failed to bind-mount {src} to {dest}: {err}")

    def detect_efi_partition(self):
        ret, out, err = self.run_cmd(["lsblk", "-o", "NAME,FSTYPE,MOUNTPOINT"])
        if ret != 0:
            return None
        for line in out.splitlines():
            parts = line.split()
            if len(parts) >= 3:
                name, fstype, mountpoint = parts[0], parts[1], parts[2]
                if "vfat" in fstype.lower() and "efi" in mountpoint.lower():
                    return f"/dev/{name}"
        return None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChrootSetupApp()
    window.show()
    sys.exit(app.exec_())
