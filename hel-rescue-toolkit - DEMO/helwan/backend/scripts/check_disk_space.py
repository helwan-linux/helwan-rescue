import sys
import shutil
import psutil
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QMessageBox
)
from PyQt5.QtCore import Qt


class DiskUsageApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Disk Usage Viewer")
        self.setGeometry(100, 100, 600, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        label = QLabel("💽 Disk Usage Report")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Device", "Mountpoint", "Total", "Used", "Free"])

        partitions = psutil.disk_partitions()
        table.setRowCount(len(partitions))

        for row, part in enumerate(partitions):
            try:
                usage = shutil.disk_usage(part.mountpoint)
            except PermissionError:
                continue

            total_gb = f"{usage.total // (1024 ** 3)} GB"
            used_gb = f"{usage.used // (1024 ** 3)} GB"
            free_gb = f"{usage.free // (1024 ** 3)} GB"

            table.setItem(row, 0, QTableWidgetItem(part.device))
            table.setItem(row, 1, QTableWidgetItem(part.mountpoint))
            table.setItem(row, 2, QTableWidgetItem(total_gb))
            table.setItem(row, 3, QTableWidgetItem(used_gb))
            table.setItem(row, 4, QTableWidgetItem(free_gb))

        table.resizeColumnsToContents()
        layout.addWidget(table)

        self.setLayout(layout)


def main():
    try:
        app = QApplication(sys.argv)
        window = DiskUsageApp()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        QMessageBox.critical(None, "Error", f"An error occurred: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
