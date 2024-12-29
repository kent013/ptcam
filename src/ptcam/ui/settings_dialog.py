from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QDoubleSpinBox, QSpinBox, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QGroupBox
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

        # General Settings Group
        general_group = QGroupBox("General Settings")
        general_layout = QFormLayout()
        self.rtsp_url_input = QLineEdit(self.config.get("rtsp_url", ""))
        self.rtsp_url_input.setMinimumWidth(400)
        general_layout.addRow("RTSP URL:", self.rtsp_url_input)

        self.screenshot_dir_input = QLineEdit(self.config.get("screenshot_dir", ""))
        self.screenshot_dir_input.setMinimumWidth(400)
        general_layout.addRow("Screenshot Directory:", self.screenshot_dir_input)

        self.skip_frames_input = QSpinBox()
        self.skip_frames_input.setMaximum(1000)
        self.skip_frames_input.setValue(self.config.get("skip_frames", 0))
        general_layout.addRow("Skip Frames:", self.skip_frames_input)
        general_group.setLayout(general_layout)
        layout.addWidget(general_group)

        # Hough Circle Settings Group
        hough_group = QGroupBox("Hough Circle Settings")
        hough_layout = QFormLayout()
        self.hough_dp_input = QDoubleSpinBox()
        self.hough_dp_input.setDecimals(2)
        self.hough_dp_input.setSingleStep(0.1)
        self.hough_dp_input.setMaximum(1000)
        self.hough_dp_input.setValue(self.config.get("hough_params.dp", 1.2))
        hough_layout.addRow("Hough DP:", self.hough_dp_input)

        self.hough_min_dist_input = QDoubleSpinBox()
        self.hough_min_dist_input.setDecimals(1)
        self.hough_min_dist_input.setSingleStep(1)
        self.hough_min_dist_input.setMaximum(1000)
        self.hough_min_dist_input.setValue(self.config.get("hough_params.min_dist", 50))
        hough_layout.addRow("Hough Min Dist:", self.hough_min_dist_input)

        self.hough_param1_input = QSpinBox()
        self.hough_param1_input.setMaximum(1000)
        self.hough_param1_input.setValue(self.config.get("hough_params.param1", 100))
        hough_layout.addRow("Hough Param1:", self.hough_param1_input)

        self.hough_param2_input = QSpinBox()
        self.hough_param2_input.setMaximum(1000)
        self.hough_param2_input.setValue(self.config.get("hough_params.param2", 70))
        hough_layout.addRow("Hough Param2:", self.hough_param2_input)

        self.hough_min_radius_input = QSpinBox()
        self.hough_min_radius_input.setMaximum(1000)
        self.hough_min_radius_input.setValue(self.config.get("hough_params.min_radius", 20))
        hough_layout.addRow("Hough Min Radius:", self.hough_min_radius_input)

        self.hough_max_radius_input = QSpinBox()
        self.hough_max_radius_input.setMaximum(1000)
        self.hough_max_radius_input.setValue(self.config.get("hough_params.max_radius", 100))
        hough_layout.addRow("Hough Max Radius:", self.hough_max_radius_input)
        hough_group.setLayout(hough_layout)
        layout.addWidget(hough_group)

        # Distance Settings Group
        distance_group = QGroupBox("Distance Settings")
        distance_layout = QFormLayout()
        self.real_diameter_input = QDoubleSpinBox()
        self.real_diameter_input.setDecimals(2)
        self.real_diameter_input.setMaximum(1000)
        self.real_diameter_input.setValue(self.config.get("real_diameter_mm", 49))
        distance_layout.addRow("Real Diameter (mm):", self.real_diameter_input)

        self.focal_length_input = QDoubleSpinBox()
        self.focal_length_input.setDecimals(2)
        self.focal_length_input.setMaximum(1000)
        self.focal_length_input.setValue(self.config.get("focal_length_mm", 3.04))
        distance_layout.addRow("Focal Length (mm):", self.focal_length_input)

        self.sensor_width_input = QDoubleSpinBox()
        self.sensor_width_input.setDecimals(2)
        self.sensor_width_input.setMaximum(1000)
        self.sensor_width_input.setValue(self.config.get("sensor_width_mm", 3.68))
        distance_layout.addRow("Sensor Width (mm):", self.sensor_width_input)

        self.sensor_height_input = QDoubleSpinBox()
        self.sensor_height_input.setDecimals(2)
        self.sensor_height_input.setMaximum(1000)
        self.sensor_height_input.setValue(self.config.get("sensor_height_mm", 2.76))
        distance_layout.addRow("Sensor Height (mm):", self.sensor_height_input)
        distance_group.setLayout(distance_layout)
        layout.addWidget(distance_group)

        # Servo Settings Group
        servo_group = QGroupBox("Servo Settings")
        servo_layout = QFormLayout()
        self.pan_pin_input = QSpinBox()
        self.pan_pin_input.setMaximum(1000)
        self.pan_pin_input.setValue(self.config.get("servo_config.pan.pin", 15))
        servo_layout.addRow("Pan Servo Pin:", self.pan_pin_input)

        self.pan_default_angle_input = QDoubleSpinBox()
        self.pan_default_angle_input.setDecimals(2)
        self.pan_default_angle_input.setMaximum(1000)
        self.pan_default_angle_input.setValue(self.config.get("servo_config.pan.default_angle", 0.0))
        servo_layout.addRow("Pan Default Angle:", self.pan_default_angle_input)

        self.tilt_pin_input = QSpinBox()
        self.tilt_pin_input.setMaximum(1000)
        self.tilt_pin_input.setValue(self.config.get("servo_config.tilt.pin", 14))
        servo_layout.addRow("Tilt Servo Pin:", self.tilt_pin_input)

        self.tilt_default_angle_input = QDoubleSpinBox()
        self.tilt_default_angle_input.setDecimals(2)
        self.tilt_default_angle_input.setMaximum(1000)
        self.tilt_default_angle_input.setValue(self.config.get("servo_config.tilt.default_angle", 0.0))
        servo_layout.addRow("Tilt Default Angle:", self.tilt_default_angle_input)
        servo_group.setLayout(servo_layout)
        layout.addWidget(servo_group)

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
        self.config.set("servo_config.pan.pin", self.pan_pin_input.value())
        self.config.set("servo_config.pan.default_angle", self.pan_default_angle_input.value())
        self.config.set("servo_config.tilt.pin", self.tilt_pin_input.value())
        self.config.set("servo_config.tilt.default_angle", self.tilt_default_angle_input.value())
        self.config.save()
        self.accept()