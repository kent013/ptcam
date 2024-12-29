from PyQt5.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QSizePolicy
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
from ptcam.ui.settings_dialog import settings_dialog
from ptcam.tracker import TrackerRunner
from ptcam.config.config import Config


class VideoStreamApp(QMainWindow):
    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        self.runner = VideoStreamRunner(config, self.update_ui)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("RTSP Object Tracking")
        self.setGeometry(100, 100, 1000, 600)

        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        button_panel = QVBoxLayout()
        button_panel.setContentsMargins(10, 10, 10, 10)
        self.settings_button = QPushButton("Settings", self)
        self.settings_button.clicked.connect(self.open_settings_dialog)
        button_panel.addWidget(self.settings_button)

        self.clear_tracker_button = QPushButton("Clear Tracker", self)
        self.clear_tracker_button.clicked.connect(self.runner.reset_tracker)
        button_panel.addWidget(self.clear_tracker_button)

        button_panel.addStretch()
        main_layout.addLayout(button_panel)

        video_layout = QVBoxLayout()
        video_layout.setContentsMargins(0, 0, 0, 0)
        video_layout.setSpacing(0)

        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.video_label.setSizePolicy(size_policy)
        video_layout.addWidget(self.video_label)

        main_layout.addLayout(video_layout)
        main_layout.setStretch(1, 1)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.runner.run)
        self.timer.start(30)

    def update_ui(self, frame, results):
        for i, x, y, w, h, distance in results:
            label_text = f"Tracker{i}: {distance:.2f} mm" if distance is not None else f"Tracker{i}: Distance N/A"
            cv2.rectangle(frame, (int(x), int(y)), (int(x + w), int(y + h)), (0, 255, 0), 2)
            cv2.putText(frame, label_text, (int(x), int(y) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        qt_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(qt_image))

    def open_settings_dialog(self):
        dialog = SettingsDialog(self.config, self)
        if dialog.exec_():
            self.config.save()
            self.runner.cap.release()
            self.runner = VideoStreamRunner(self.config, self.update_ui)

    def closeEvent(self, event):
        self.runner.cap.release()
        super().closeEvent(event)