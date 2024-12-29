import cv2
import numpy as np

# RTSPストリームのURL
RTSP_URL = "rtsp://127.0.0.1:8554/stream"

# RTSPストリームから映像を取得
cap = cv2.VideoCapture(RTSP_URL)

if not cap.isOpened():
    print("Failed to open RTSP stream")
    exit()

def detect_red_ball(frame):
    """
    フレーム内の赤い物体を検出し、その中心座標を返す。
    """
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # 赤色の範囲を設定 (2つの範囲に分ける: 赤は色相が循環するため)
    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])

    # マスクを作成
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = mask1 | mask2

    # ノイズ除去
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))

    # 輪郭を検出
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # 検出した輪郭から一番大きいものを選ぶ
    for i, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        if area > 500:  # 小さいノイズを無視
            # バウンディングボックスを計算
            x, y, w, h = cv2.boundingRect(contour)
            # 中心座標を計算
            center_x, center_y = x + w // 2, y + h // 2
            return (center_x, center_y)

    return None

# メインループ
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame")
            break

        # 赤いボールを検出
        position = detect_red_ball(frame)

        if position:
            # 座標を標準出力に出力
            x, y = position
            print(f"ball1:{x},{y}")

except KeyboardInterrupt:
    print("Stopped by user")

finally:
    cap.release()
    cv2.destroyAllWindows()
