import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QStatusBar,
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from worker import TrackerWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RPM Tracker")
        self.resize(1100, 800)

        self.worker = None

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # --- source input row ---
        source_row = QHBoxLayout()
        self.source_input = QLineEdit()
        self.source_input.setPlaceholderText(
            "Video source URL (e.g. http://192.168.1.31:5000/video)"
        )
        self.start_btn = QPushButton("Start")
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setEnabled(False)

        source_row.addWidget(self.source_input)
        source_row.addWidget(self.start_btn)
        source_row.addWidget(self.stop_btn)
        layout.addLayout(source_row)

        # --- video + RPM table row ---
        content_row = QHBoxLayout()

        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("background-color: #222;")
        content_row.addWidget(self.video_label, stretch=3)

        self.rpm_table = QTableWidget(0, 2)
        self.rpm_table.setHorizontalHeaderLabels(["Tag ID", "RPM"])
        content_row.addWidget(self.rpm_table, stretch=1)

        layout.addLayout(content_row)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.start_btn.clicked.connect(self.start_tracking)
        self.stop_btn.clicked.connect(self.stop_tracking)

    def start_tracking(self):
        source = self.source_input.text().strip()
        if not source:
            self.status_bar.showMessage("Enter a source URL first")
            return

        self.worker = TrackerWorker(source)
        self.worker.frame_ready.connect(self.on_frame)
        self.worker.rpm_updated.connect(self.on_rpm_update)
        self.worker.status.connect(self.status_bar.showMessage)
        self.worker.error.connect(self.on_error)
        self.worker.start()

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.source_input.setEnabled(False)

    def stop_tracking(self):
        if self.worker is not None:
            self.worker.stop()
            self.worker.wait(2000)
            self.worker = None

        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.source_input.setEnabled(True)
        self.status_bar.showMessage("Stopped")

    def on_frame(self, qimg):
        pixmap = QPixmap.fromImage(qimg)
        pixmap = pixmap.scaled(
            self.video_label.width(),
            self.video_label.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.video_label.setPixmap(pixmap)

    def on_rpm_update(self, rpm_dict):
        self.rpm_table.setRowCount(len(rpm_dict))
        for row, tag_id in enumerate(sorted(rpm_dict.keys())):
            self.rpm_table.setItem(row, 0, QTableWidgetItem(str(tag_id)))
            self.rpm_table.setItem(row, 1, QTableWidgetItem(f"{rpm_dict[tag_id]:.2f}"))

    def on_error(self, message):
        self.status_bar.showMessage(f"Error: {message}")
        self.stop_tracking()

    def closeEvent(self, event):
        self.stop_tracking()
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
