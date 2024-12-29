import argparse
from PyQt5.QtWidgets import QApplication
from ptcam.config.config import Config
from ptcam.ui.video_stream_app import VideoStreamApp
from ptcam.tracker import TrackerRunner


def main():
    parser = argparse.ArgumentParser(description="RTSP Object Tracking")
    parser.add_argument("--gui", action="store_true", help="Run in GUI mode")
    args = parser.parse_args()

    config = Config()

    if args.gui:
        app = QApplication([])
        main_window = VideoStreamApp(config)
        main_window.show()
        app.exec_()
    else:
        runner = TrackerRunner(config)
        runner.run()