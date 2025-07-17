import sys
import os
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QPushButton, QTextEdit, QMessageBox
)
from PyQt5.QtCore import Qt

class NetworkFixer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Network Connectivity Fixer (Root Required)")
        self.setFixedSize(500, 400)

        self.layout = QVBoxLayout()

        self.label = QLabel("Press the button to attempt fixing network connectivity.\n"
                            "This requires root privileges.")
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.layout.addWidget(self.log)

        self.button = QPushButton("Fix Network")
        self.button.clicked.connect(self.fix_network)
        self.layout.addWidget(self.button)

        self.setLayout(self.layout)

    def log_message(self, message):
        self.log.append(message)
        QApplication.processEvents()  # update GUI immediately

    def fix_network(self):
        # Clear previous logs
        self.log.clear()

        # Check root permissions (Linux/macOS)
        if hasattr(os, "geteuid") and os.geteuid() != 0:
            QMessageBox.critical(self, "Permission Denied", "This operation requires root privileges.")
            return

        self.log_message("Attempting to fix network connectivity...")

        # Restart NetworkManager service if available
        nm_status = self.run_command("systemctl restart NetworkManager")
        if nm_status != 0:
            self.log_message("Warning: Could not restart NetworkManager. Trying fallback methods...")

            # Detect active interfaces except loopback
            interfaces = self.get_network_interfaces()
            if not interfaces:
                self.log_message("No network interfaces detected. Cannot continue.")
                return

            for iface in interfaces:
                self.log_message(f"Bringing up interface: {iface}")
                self.run_command(f"ip link set {iface} up")

            # Try dhcpcd if available
            if self.command_exists("dhcpcd"):
                self.log_message("Starting dhcpcd daemon...")
                self.run_command("dhcpcd -B")
            else:
                self.log_message("dhcpcd not found on system.")

        else:
            self.log_message("NetworkManager restarted successfully.")

        # Reset DNS resolver to 1.1.1.1
        try:
            with open("/etc/resolv.conf", "w") as resolv:
                resolv.write("nameserver 1.1.1.1\n")
            self.log_message("DNS resolver reset to 1.1.1.1")
        except PermissionError:
            self.log_message("Error: Cannot write to /etc/resolv.conf (permission denied).")

        # Test internet connection
        self.log_message("Testing internet connection (ping archlinux.org)...")
        ping_result = self.run_command("ping -c 3 archlinux.org")

        if ping_result == 0:
            self.log_message("✅ Network is now working correctly.")
            QMessageBox.information(self, "Success", "Network is now working correctly.")
        else:
            self.log_message("❌ Network restart complete, but no stable connection detected.")
            QMessageBox.warning(self, "Warning", "Network restart complete, but no stable connection detected.\n"
                                                 "Please check your physical connection or network configuration.")

    def run_command(self, command):
        """Run shell command, return returncode."""
        try:
            result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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

    def get_network_interfaces(self):
        """Return list of network interfaces except loopback."""
        try:
            output = subprocess.check_output("ip -o link show | awk -F': ' '{print $2}'", shell=True).decode()
            interfaces = [line.strip() for line in output.splitlines() if line.strip() != "lo"]
            return interfaces
        except Exception as e:
            self.log_message(f"Error detecting interfaces: {e}")
            return []

    def command_exists(self, cmd):
        """Check if command exists on system."""
        return subprocess.call(f"type {cmd}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

if __name__ == "__main__":
    if sys.platform.startswith("win"):
        print("This script is designed for Linux/macOS systems only.")
        sys.exit(1)

    app = QApplication(sys.argv)
    window = NetworkFixer()
    window.show()
    sys.exit(app.exec_())
