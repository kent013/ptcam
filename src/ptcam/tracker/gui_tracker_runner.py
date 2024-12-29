from PyQt5.QtCore import QObject, QThread, pyqtSignal
import cv2
from ptcam.tracker.tracker_processor import TrackerProcessor


class GUITrackerRunner(QObject):
    frame_processed = pyqtSignal(object, list)
    error_signal = pyqtSignal(str)

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.processor = TrackerProcessor(config)
        self.running = False

    def start_tracking(self):
        self.running = True
        self.thread = QThread()
        self.moveToThread(self.thread)
        self.thread.started.connect(self.run)
        self.thread.start()

    def stop_tracking(self):
        self.running = False
        if hasattr(self, 'thread'):
            self.thread.quit()
            self.thread.wait()

    def run(self):
        try:
            cap = cv2.VideoCapture(self.config.get("rtsp_url"))
            if not cap.isOpened():
                raise Exception(f"Failed to open RTSP stream: {self.config.get('rtsp_url')}")

            while self.running:
                ret, frame = cap.read()
                if not ret:
                    continue

                results = self.processor.process_frame(frame)
                self.frame_processed.emit(frame, results)

            cap.release()
        except Exception as e:
            self.error_signal.emit(str(e))

    def reset_trackers(self):
        try:
            self.processor.reset_trackers()
            print("Tracker cleared.")
        except AttributeError as e:
            print(f"Error clearing trackers: {e}")