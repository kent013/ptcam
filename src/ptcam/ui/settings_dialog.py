from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QDoubleSpinBox, QSpinBox, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout
)
from ptcam.config.config import Config


class SettingsDialog(QDialog):
    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Settings")
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # RTSP URL
        self.rtsp_url_input = QLineEdit(self.config.get("rtsp_url", ""))
        self.rtsp_url_input.setMinimumWidth(400)
        form_layout.addRow("RTSP URL:", self.rtsp_url_input)

        # Screenshot Directory
        self.screenshot_dir_input = QLineEdit(self.config.get("screenshot_dir", ""))
        self.screenshot_dir_input.setMinimumWidth(400)
        form_layout.addRow("Screenshot Directory:", self.screenshot_dir_input)

        # Skip Frames
        self.skip_frames_input = QSpinBox()
        self.skip_frames_input.setValue(self.config.get("skip_frames", 0))
        form_layout.addRow("Skip Frames:", self.skip_frames_input)

        # Hough DP
        self.hough_dp_input = QDoubleSpinBox()
        self.hough_dp_input.setDecimals(2)
        self.hough_dp_input.setSingleStep(0.1)
        self.hough_dp_input.setValue(self.config.get("hough_params.dp", 1.2))
        form_layout.addRow("Hough DP:", self.hough_dp_input)

        # Hough Min Dist
        self.hough_min_dist_input = QDoubleSpinBox()
        self.hough_min_dist_input.setDecimals(1)
        self.hough_min_dist_input.setSingleStep(1)
        self.hough_min_dist_input.setValue(self.config.get("hough_params.min_dist", 50))
        form_layout.addRow("Hough Min Dist:", self.hough_min_dist_input)

        # Hough Param1
        self.hough_param1_input = QSpinBox()
        self.hough_param1_input.setValue(self.config.get("hough_params.param1", 100))
        form_layout.addRow("Hough Param1:", self.hough_param1_input)

        # Hough Param2
        self.hough_param2_input = QSpinBox()
        self.hough_param2_input.setValue(self.config.get("hough_params.param2", 70))
        form_layout.addRow("Hough Param2:", self.hough_param2_input)

        # Hough Min Radius
        self.hough_min_radius_input = QSpinBox()
        self.hough_min_radius_input.setValue(self.config.get("hough_params.min_radius", 20))
        form_layout.addRow("Hough Min Radius:", self.hough_min_radius_input)

        # Hough Max Radius
        self.hough_max_radius_input = QSpinBox()
        self.hough_max_radius_input.setValue(self.config.get("hough_params.max_radius", 100))
        form_layout.addRow("Hough Max Radius:", self.hough_max_radius_input)

        # Real Diameter
        self.real_diameter_input = QDoubleSpinBox()
        self.real_diameter_input.setDecimals(3)
        self.real_diameter_input.setValue(self.config.get("real_diameter_mm", 49))
        form_layout.addRow("Real Diameter (mm):", self.real_diameter_input)

        # Focal Length
        self.focal_length_input = QDoubleSpinBox()
        self.focal_length_input.setDecimals(3)
        self.focal_length_input.setValue(self.config.get("focal_length_mm", 3.04))
        form_layout.addRow("Focal Length (mm):", self.focal_length_input)

        # Sensor Width
        self.sensor_width_input = QDoubleSpinBox()
        self.sensor_width_input.setDecimals(3)
        self.sensor_width_input.setValue(self.config.get("sensor_width_mm", 3.68))
        form_layout.addRow("Sensor Width (mm):", self.sensor_width_input)

        # Sensor Height
        self.sensor_height_input = QDoubleSpinBox()
        self.sensor_height_input.setDecimals(3)
        self.sensor_height_input.setValue(self.config.get("sensor_height_mm", 2.76))
        form_layout.addRow("Sensor Height (mm):", self.sensor_height_input)

        layout.addLayout(form_layout)

        # Save Button
        save_button = QPushButton("Save")
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        save_button.clicked.connect(self.save_settings)

    def save_settings(self):
        self.config.set("rtsp_url", self.rtsp_url_input.text())
        self.config.set("screenshot_dir", self.screenshot_dir_input.text())
        self.config.set("skip_frames", self.skip_frames_input.value())
        self.config.set("hough_params.dp", self.hough_dp_input.value())
        self.config.set("hough_params.min_dist", self.hough_min_dist_input.value())
        self.config.set("hough_params.param1", self.hough_param1_input.value())
        self.config.set("hough_params.param2", self.hough_param2_input.value())
        self.config.set("hough_params.min_radius", self.hough_min_radius_input.value())
        self.config.set("hough_params.max_radius", self.hough_max_radius_input.value())
        self.config.set("real_diameter_mm", self.real_diameter_input.value())
        self.config.set("focal_length_mm", self.focal_length_input.value())
        self.config.set("sensor_width_mm", self.sensor_width_input.value())
        self.config.set("sensor_height_mm", self.sensor_height_input.value())
        self.config.save()
        self.accept()