import cv2
import threading
from typing import Callable


class FrameReader:
    def __init__(self, config):
        self.rtsp_url = config.get("rtsp_url")
        self.skip_frames = config.get("skip_frames", 0)
        self.cap = None
        self.running = False
        self.frame_counter = 0
        self.callback = None
        self.lock = threading.Lock()

    def start(self):
        self.running = True
        self.cap = cv2.VideoCapture(self.rtsp_url)
        if not self.cap.isOpened():
            raise Exception(f"Failed to open RTSP stream: {self.rtsp_url}")

        self.thread = threading.Thread(target=self._read_frames, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread.is_alive():
            self.thread.join()
        if self.cap:
            self.cap.release()

    def set_callback(self, callback: Callable[[any], None]):
        with self.lock:
            self.callback = callback
            
    def _read_frames(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                continue

            self.frame_counter += 1

            if self.frame_counter <= self.skip_frames:
                continue

            self.frame_counter = 0
            self._trigger_callback(frame)

    def _trigger_callback(self, frame):
        with self.lock:
            if self.callback:
                self.callback(frame)