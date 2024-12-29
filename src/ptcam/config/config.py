import yaml
import os

DEFAULT_CONFIG = {
    "rtsp_url": "rtsp://192.168.1.51:8554/stream",
    "screenshot_dir": "/path/to/screenshots",
    "skip_frames": 5,
    "hough_params": {
        "dp": 1.2,
        "min_dist": 50,
        "param1": 100,
        "param2": 70,
        "min_radius": 20,
        "max_radius": 100,
    },
}

CONFIG_FILE = "config.yaml"

class Config:
    def __init__(self):
        self.data = DEFAULT_CONFIG.copy()
        self.load()

    def load(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as file:
                self.data.update(yaml.safe_load(file))

    def save(self):
        with open(CONFIG_FILE, "w") as file:
            yaml.dump(self.data, file)

    def get(self, key, default=None):
        keys = key.split(".")
        value = self.data
        for k in keys:
            if not isinstance(value, dict) or k not in value:
                return default
            value = value[k]
        return value

    def set(self, key, value):
        keys = key.split(".")
        config = self.data
        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value