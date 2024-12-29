from ptcam.config.config import Config

class DistanceCalculator:
    def __init__(self, config):
        self.config = config

    def calculate_distance(self, diameter_px_width, diameter_px_height, frame_width, frame_height):
        if diameter_px_width <= 0 or diameter_px_height <= 0:
            return None

        # ピクセルサイズ計算（補正ファクタ k を追加可能）
        pixel_size_width = self.config.get("sensor_width_mm") / frame_width
        pixel_size_height = self.config.get("sensor_height_mm") / frame_height

        # 実際の直径計算（縦横で分けて平均）
        diameter_mm_width = diameter_px_width * pixel_size_width
        diameter_mm_height = diameter_px_height * pixel_size_height
        diameter_mm = (diameter_mm_width + diameter_mm_height) / 2

        # 距離計算
        if diameter_mm > 0:
            return self.config.get("real_diameter_mm") * self.config.get("focal_length_mm") / diameter_mm
        return None