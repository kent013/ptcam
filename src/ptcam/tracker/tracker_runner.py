import cv2
from ptcam.tracker import Tracker, DistanceCalculator
from ptcam.config.config import Config


class TrackerRunner:
    def __init__(self, config: Config, callback=None):
        self.config = config
        self.tracker = Tracker(config)
        self.distance_calculator = DistanceCalculator(config)
        self.cap = cv2.VideoCapture(self.config.get("rtsp_url"))
        if not self.cap.isOpened():
            raise Exception(f"Failed to open RTSP stream: {self.config.get('rtsp_url')}")
        self.callback = callback

    def run(self):
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("Failed to read frame")
                    break

                height, width = frame.shape[:2]

                ok, boxes = self.tracker.update(frame)
                if not ok or len(boxes) == 0:
                    circles = self.tracker.detect_circles_in_frame(frame)
                    if circles:
                        self.tracker.reset_trackers()
                        self.tracker.add_circles_to_multitracker(frame, circles)

                results = []
                for i, (x, y, w, h) in enumerate(boxes):
                    distance = self.distance_calculator.calculate_distance(w, h, width, height)
                    results.append((i, x, y, w, h, distance))

                if self.callback:
                    self.callback(frame, results)

        finally:
            self.cap.release()

    def reset_tracker(self):
        self.tracker.reset_trackers()