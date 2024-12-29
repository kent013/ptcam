import cv2
import numpy as np


class Tracker:
    def __init__(self, config):
        self.config = config
        self.trackers = cv2.legacy.MultiTracker_create()

    def detect_circles_in_frame(self, frame):
        hough_params = {
            "dp": self.config.get("hough_params.dp", 1.2),
            "min_dist": self.config.get("hough_params.min_dist", 50),
            "param1": self.config.get("hough_params.param1", 100),
            "param2": self.config.get("hough_params.param2", 70),
            "min_radius": self.config.get("hough_params.min_radius", 20),
            "max_radius": self.config.get("hough_params.max_radius", 100),
        }

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

    def add_circles_to_multitracker(self, frame, circles):
        h, w = frame.shape[:2]
        for (cx, cy, r) in circles:
            x0 = max(0, cx - r)
            y0 = max(0, cy - r)
            w0 = min(2 * r, w - x0)
            h0 = min(2 * r, h - y0)

            bbox = (x0, y0, w0, h0)
            tracker = self.create_single_tracker()
            ok = self.trackers.add(tracker, frame, bbox)
            if not ok:
                print(f"Warning: Could not add tracker for circle: (x={cx}, y={cy}, r={r})")

    def create_single_tracker(self):
        return cv2.legacy.TrackerCSRT_create()

    def update(self, frame):
        ok, boxes = self.trackers.update(frame)
        return ok, boxes

    def reset_trackers(self):
        self.trackers = cv2.legacy.MultiTracker_create()