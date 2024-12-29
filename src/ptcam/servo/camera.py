import cv2
import numpy as np
from collections import deque

class BallTracker:
    def __init__(self, max_disappeared=50):
        self.next_object_id = 1
        self.objects = {}  # トラッキング中のオブジェクト {id: (x, y)}
        self.disappeared = {}  # トラッキングから消えたカウント {id: count}
        self.max_disappeared = max_disappeared

    def register(self, centroid):
        """新しいオブジェクトを登録"""
        self.objects[self.next_object_id] = centroid
        self.disappeared[self.next_object_id] = 0
        self.next_object_id += 1

    def deregister(self, object_id):
        """トラッキングからオブジェクトを削除"""
        del self.objects[object_id]
        del self.disappeared[object_id]

    def update(self, input_centroids):
        """入力されたセントロイド（重心）に基づいてトラッキング情報を更新"""
        if len(input_centroids) == 0:
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
            return self.objects

        if len(self.objects) == 0:
            for centroid in input_centroids:
                self.register(centroid)
        else:
            object_ids = list(self.objects.keys())
            object_centroids = list(self.objects.values())

            distances = np.linalg.norm(np.array(object_centroids)[:, None] - np.array(input_centroids), axis=2)
            rows = distances.min(axis=1).argsort()
            cols = distances.argmin(axis=1)[rows]

            used_rows, used_cols = set(), set()

            for row, col in zip(rows, cols):
                if row in used_rows or col in used_cols:
                    continue

                object_id = object_ids[row]
                self.objects[object_id] = input_centroids[col]
                self.disappeared[object_id] = 0

                used_rows.add(row)
                used_cols.add(col)

            unused_rows = set(range(0, distances.shape[0])) - used_rows
            unused_cols = set(range(0, distances.shape[1])) - used_cols

            for row in unused_rows:
                object_id = object_ids[row]
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)

            for col in unused_cols:
                self.register(input_centroids[col])

        return self.objects

def main():
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

    rtsp_pipe = (
        "appsrc ! videoconvert ! v4l2h264enc extra-controls=\"encode,frame_level_rate_control_enable=1,video_bitrate=500000\" "
        "! rtph264pay config-interval=1 pt=96 ! udpsink host=0.0.0.0 port=8554"
    )

    out = cv2.VideoWriter(rtsp_pipe, cv2.CAP_GSTREAMER, 0, 20.0, (320, 240), True)

    if not camera.isOpened() or not out.isOpened():
        print("カメラまたはGStreamerの初期化に失敗しました。")
        return

    tracker = BallTracker()
    while True:
        ret, frame = camera.read()
        if not ret:
            print("フレームの読み取りに失敗しました。")
            break

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_red1 = np.array([0, 120, 70])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 120, 70])
        upper_red2 = np.array([180, 255, 255])
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = mask1 + mask2

        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        centroids = []
        for contour in contours:
            if cv2.contourArea(contour) > 500:
                x, y, w, h = cv2.boundingRect(contour)
                centroids.append((x + w // 2, y + h // 2))
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        tracked_objects = tracker.update(centroids)

        for object_id, centroid in tracked_objects.items():
            x, y = centroid
            cv2.putText(frame, f"ball({object_id})", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

        out.write(frame)
        cv2.imshow("Tracked Red Balls", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camera.release()
    out.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()