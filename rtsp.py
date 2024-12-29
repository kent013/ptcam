import sys
import cv2
import numpy as np
import argparse
import os
from datetime import datetime
import yaml
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget, QLabel, QLineEdit, QFileDialog, QMessageBox
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap

# ==============================================
# デフォルト設定
# ==============================================
CONFIG_FILE = "config.yaml"
DEFAULT_CONFIG = {
    "rtsp_url": "rtsp://192.168.1.51:8554/stream",
    "screenshot_dir": "/Users/ishitoya/Desktop/screenshots",
    "skip_frames": 5,
    "hough_params": {
        "dp": 1.2,
        "min_dist": 50,
        "param1": 100,
        "param2": 70,
        "min_radius": 20,
        "max_radius": 100,
    }
}

# ==============================================
# 設定の読み込み・保存
# ==============================================
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return yaml.safe_load(f)
    return DEFAULT_CONFIG

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        yaml.dump(config, f)

# ==============================================
# HoughCircles 関連
# ==============================================
def detect_circles_in_frame(frame, hough_params):
    """
    frame: BGR画像
    hough_params: HoughCirclesのパラメータ辞書
    return: list of (x, y, r)  （整数で返す）
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (9, 9), 2)

    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=hough_params["dp"],
        minDist=hough_params["min_dist"],
        param1=hough_params["param1"],
        param2=hough_params["param2"],
        minRadius=hough_params["min_radius"],
        maxRadius=hough_params["max_radius"],
    )

    results = []
    if circles is not None and len(circles) > 0:
        circles_rounded = np.uint16(np.around(circles))
        for (x, y, r) in circles_rounded[0, :]:
            results.append((int(x), int(y), int(r)))
    return results

# ==============================================
# UI: PyQtアプリケーション
# ==============================================
class VideoStreamApp(QMainWindow):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config

        # RTSPストリームの設定
        self.cap = cv2.VideoCapture(self.config["rtsp_url"])
        if not self.cap.isOpened():
            raise Exception(f"Failed to open RTSP stream: {self.config['rtsp_url']}")

        # UI初期化
        self.initUI()

        # タイマーでフレームを定期的に更新
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # 30msごとに更新（約30FPS）

    def initUI(self):
        """
        UIの初期設定
        """
        self.setWindowTitle("RTSP Object Tracking with PyQt")
        self.setGeometry(100, 100, 800, 600)

        # メインウィジェット
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # 動画表示用のラベル
        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.video_label)

        # 設定ボタン
        self.settings_button = QPushButton("Settings", self)
        self.settings_button.clicked.connect(self.open_settings_dialog)
        layout.addWidget(self.settings_button)

        # トラッキングクリアボタン
        self.clear_button = QPushButton("Clear Tracking", self)
        self.clear_button.clicked.connect(self.clear_tracking)
        layout.addWidget(self.clear_button)

    def update_frame(self):
        """
        フレームを取得してUIに表示
        """
        ret, frame = self.cap.read()
        if not ret:
            print("Failed to read frame")
            return

        # 円の検出
        hough_params = self.config["hough_params"]
        circles = detect_circles_in_frame(frame, hough_params)

        # 検出された円を描画
        for (x, y, r) in circles:
            cv2.circle(frame, (x, y), r, (0, 255, 0), 2)

        # PyQtに表示するための変換
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        qt_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(qt_image))

    def clear_tracking(self):
        """
        トラッキングをクリア
        """
        print("Tracking cleared")

    def open_settings_dialog(self):
        """
        設定ダイアログを開く
        """
        dialog = SettingsDialog(self.config, self)
        dialog.exec_()
        self.config = dialog.get_updated_config()
        save_config(self.config)
        print("Settings updated and saved")

    def closeEvent(self, event):
        """
        アプリケーション終了時の処理
        """
        self.cap.release()
        super().closeEvent(event)

# ==============================================
# 設定ダイアログ
# ==============================================
from PyQt5.QtWidgets import QDialog, QFormLayout, QDoubleSpinBox, QSpinBox, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout

class SettingsDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Settings")
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.rtsp_url_input = QLineEdit(self.config["rtsp_url"], self)
        self.rtsp_url_input.setMinimumWidth(400)
        form_layout.addRow("RTSP URL:", self.rtsp_url_input)

        self.screenshot_dir_input = QLineEdit(self.config["screenshot_dir"], self)
        self.screenshot_dir_input.setMinimumWidth(400)
        form_layout.addRow("Screenshot Directory:", self.screenshot_dir_input)

        self.skip_frames_input = QSpinBox(self)
        self.skip_frames_input.setValue(self.config["skip_frames"])
        form_layout.addRow("Skip Frames:", self.skip_frames_input)

        self.hough_dp_input = QDoubleSpinBox(self)
        self.hough_dp_input.setDecimals(2)
        self.hough_dp_input.setSingleStep(0.1)
        self.hough_dp_input.setValue(self.config["hough_params"]["dp"])
        form_layout.addRow("Hough DP:", self.hough_dp_input)

        self.hough_min_dist_input = QSpinBox(self)
        self.hough_min_dist_input.setValue(self.config["hough_params"]["min_dist"])
        form_layout.addRow("Min Distance:", self.hough_min_dist_input)

        self.hough_param1_input = QSpinBox(self)
        self.hough_param1_input.setValue(self.config["hough_params"]["param1"])
        form_layout.addRow("Param1:", self.hough_param1_input)

        self.hough_param2_input = QSpinBox(self)
        self.hough_param2_input.setValue(self.config["hough_params"]["param2"])
        form_layout.addRow("Param2:", self.hough_param2_input)

        self.hough_min_radius_input = QSpinBox(self)
        self.hough_min_radius_input.setValue(self.config["hough_params"]["min_radius"])
        form_layout.addRow("Min Radius:", self.hough_min_radius_input)

        self.hough_max_radius_input = QSpinBox(self)
        self.hough_max_radius_input.setValue(self.config["hough_params"]["max_radius"])
        form_layout.addRow("Max Radius:", self.hough_max_radius_input)

        layout.addLayout(form_layout)

        save_button = QPushButton("Save", self)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        save_button.clicked.connect(self.accept)

    def get_updated_config(self):
        return {
            "rtsp_url": self.rtsp_url_input.text(),
            "screenshot_dir": self.screenshot_dir_input.text(),
            "skip_frames": self.skip_frames_input.value(),
            "hough_params": {
                "dp": self.hough_dp_input.value(),
                "min_dist": self.hough_min_dist_input.value(),
                "param1": self.hough_param1_input.value(),
                "param2": self.hough_param2_input.value(),
                "min_radius": self.hough_min_radius_input.value(),
                "max_radius": self.hough_max_radius_input.value(),
            },
        }

# ==============================================
# メイン関数
# ==============================================
def main():
    config = load_config()

    app = QApplication(sys.argv)
    main_window = VideoStreamApp(config)
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()