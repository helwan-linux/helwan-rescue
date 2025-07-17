import sys
import psutil
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QListWidget,
    QPushButton, QLineEdit, QMessageBox, QHBoxLayout
)


class ProcessManagerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Process Manager")
        self.setGeometry(400, 300, 600, 500)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Top 5 CPU consuming processes:"))
        self.cpu_list = QListWidget()
        layout.addWidget(self.cpu_list)

        layout.addWidget(QLabel("Top 5 RAM consuming processes:"))
        self.ram_list = QListWidget()
        layout.addWidget(self.ram_list)

        pid_layout = QHBoxLayout()
        pid_label = QLabel("Enter PID to kill (optional):")
        self.pid_input = QLineEdit()
        pid_layout.addWidget(pid_label)
        pid_layout.addWidget(self.pid_input)
        layout.addLayout(pid_layout)

        btn_layout = QHBoxLayout()
        self.stop_button = QPushButton("Kill Process")
        self.stop_button.clicked.connect(self.try_stop_process)
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_lists)
        btn_layout.addWidget(self.stop_button)
        btn_layout.addWidget(self.refresh_button)
        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.refresh_lists()

    def refresh_lists(self):
        self.cpu_list.clear()
        self.ram_list.clear()

        procs = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                procs.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        top_cpu = sorted(procs, key=lambda p: p.info['cpu_percent'], reverse=True)[:5]
        for p in top_cpu:
            self.cpu_list.addItem(f"PID: {p.pid} | CPU: {p.info['cpu_percent']:.1f}% | {p.info['name']}")

        top_ram = sorted(procs, key=lambda p: p.info['memory_percent'], reverse=True)[:5]
        for p in top_ram:
            self.ram_list.addItem(f"PID: {p.pid} | RAM: {p.info['memory_percent']:.1f}% | {p.info['name']}")

    def try_stop_process(self):
        pid_text = self.pid_input.text().strip()
        if not pid_text:
            QMessageBox.information(self, "Info", "No PID entered.")
            return

        if not pid_text.isdigit():
            QMessageBox.warning(self, "Error", "Please enter a valid numeric PID.")
            return

        pid = int(pid_text)
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            proc.wait(timeout=3)
            QMessageBox.information(self, "Success", f"Process PID {pid} terminated.")
            self.refresh_lists()
        except psutil.NoSuchProcess:
            QMessageBox.warning(self, "Error", f"No process with PID {pid}.")
        except psutil.AccessDenied:
            QMessageBox.warning(self, "Denied", "Insufficient permissions to kill this process.")
        except psutil.TimeoutExpired:
            QMessageBox.warning(self, "Timeout", "Failed to terminate process in time.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProcessManagerApp()
    window.show()
    sys.exit(app.exec_())
