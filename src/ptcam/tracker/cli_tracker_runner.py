from ptcam.tracker.frame_reader import FrameReader
from ptcam.tracker.tracker_processor import TrackerProcessor


class CLITrackerRunner:
    def __init__(self, config):
        self.config = config
        self.processor = TrackerProcessor(config)
        self.frame_reader = FrameReader(config)

    def start(self):
        self.frame_reader.set_callback(self.process_frame)
        self.frame_reader.start()
        print("Starting tracking in CLI mode. Press Ctrl+C to stop.")

        try:
            while self.frame_reader.running:
                pass  # メインスレッドはここで待機
        except KeyboardInterrupt:
            print("Stopping tracking...")
        finally:
            self.frame_reader.stop()

    def process_frame(self, frame):
        results = self.processor.process_frame(frame)
        self.print_results(results)

    def print_results(self, results):
        for i, ((x, y, w, h), distance) in enumerate(results):
            if distance is not None:
                print(f"Object {i}: Box=({x}, {y}, {w}, {h}), Distance={distance:.2f} mm")
            else:
                print(f"Object {i}: Box=({x}, {y}, {w}, {h}), Distance=N/A")