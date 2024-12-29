import cv2
from ptcam.tracker import Tracker, DistanceCalculator

class TrackerProcessor:
    def __init__(self, config):
        self.config = config
        self.tracker = Tracker(config)
        self.distance_calculator = DistanceCalculator(config)

    def process_frame(self, frame):
        height, width = frame.shape[:2]
        ok, boxes = self.tracker.update(frame)
        if not ok or len(boxes) == 0:
            circles = self.tracker.detect_circles_in_frame(frame)
            if circles:
                self.tracker.reset_trackers()
                self.tracker.add_circles_to_multitracker(frame, circles)

        results = []
        for x, y, w, h in boxes:
            distance = self.distance_calculator.calculate_distance(w, h, width, height)
            results.append(((x, y, w, h), distance))
        return results

    def reset_trackers(self):
        self.tracker.reset_trackers()