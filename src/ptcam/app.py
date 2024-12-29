import argparse
from PyQt5.QtWidgets import QApplication
from ptcam.config.config import Config
from ptcam.ui.video_stream_app import VideoStreamApp
from ptcam.tracker.cli_tracker_runner import CLITrackerRunner

def main():
    parser = argparse.ArgumentParser(description="RTSP Object Tracking")
    parser.add_argument("--gui", action="store_true", help="Run in GUI mode")
    args = parser.parse_args()

    config = Config()

    if args.gui:
        app = QApplication([])
        main_window = VideoStreamApp(config)
        main_window.show()
        main_window.start_tracking()
        exit_code = app.exec_()
        main_window.stop_tracking()
        return exit_code
    else:
        runner = CLITrackerRunner(config)
        runner.start()

if __name__ == "__main__":
    main()