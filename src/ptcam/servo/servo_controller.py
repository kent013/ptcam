import RPi.GPIO as GPIO
import time
from ptcam.config.config import Config

class ServoController:
    def __init__(self, config: Config):
        self.config = config
        self.default_servo_config = {
            "pan": {"pin": 15, "default_angle": 0.0, "full_sweep_time": 1.0, "max_angle": 360.0},
            "tilt": {"pin": 14, "default_angle": 0.0, "step_size": 2, "delay_sec": 0.1, "max_angle": 180.0},
        }
        self.servo_config = self.config.get("servo_config")
        if not self.servo_config:
            self.servo_config = self.default_servo_config
            self.config.set("servo_config", self.default_servo_config)
            self.config.save()
            
        self.angle_file = self.config.get("angle_file", os.path.join(os.getcwd(), "tmp", "servo_angles.txt"))
        if not self.config.get("angle_file"):
            self.config.set("angle_file", self.angle_file)
            self.config.save()

        self.min_duty = self.config.get("min_duty", 2.5)
        self.max_duty = self.config.get("max_duty", 10.0)
        self.ensure_tmp_directory()

    def ensure_tmp_directory(self):
        tmp_dir = os.path.dirname(self.angle_file)
        os.makedirs(tmp_dir, exist_ok=True)

    def read_last_angle(self, servo_name):
        try:
            with open(self.angle_file, "r") as f:
                angles = dict(line.strip().split("=") for line in f if "=" in line)
                return float(angles.get(servo_name, self.servo_config[servo_name]["default_angle"]))
        except FileNotFoundError:
            return self.servo_config[servo_name]["default_angle"]

    def write_last_angle(self, servo_name, angle):
        try:
            angles = {}
            with open(self.angle_file, "r") as f:
                angles = dict(line.strip().split("=") for line in f if "=" in line)
        except FileNotFoundError:
            pass

        angles[servo_name] = str(angle)
        with open(self.angle_file, "w") as f:
            for key, value in angles.items():
                f.write(f"{key}={value}\n")

    def initialize_servo(self, servo_name):
        if servo_name not in self.servo_config:
            raise ValueError(f"Invalid servo name: {servo_name}")

        GPIO.setmode(GPIO.BCM)
        servo_pin = self.servo_config[servo_name]["pin"]
        GPIO.setup(servo_pin, GPIO.OUT)
        pwm = GPIO.PWM(servo_pin, 50)
        pwm.start(0)

        current_angle = self.read_last_angle(servo_name)
        return pwm, current_angle

    def cleanup_servo(self, pwm):
        pwm.stop()
        GPIO.cleanup()

    def move_pan_by_offset(self, pwm, current_angle, offset):
        max_angle = self.servo_config["pan"]["max_angle"]
        target_angle = max(0, min(max_angle, current_angle + offset))

        angle_difference = abs(target_angle - current_angle)
        move_time = (angle_difference / 180.0) * self.servo_config["pan"]["full_sweep_time"]

        target_duty = 7.809 if offset > 0 else 6.434
        pwm.ChangeDutyCycle(target_duty)
        time.sleep(move_time)

        self.write_last_angle("pan", target_angle)

    def move_pan_to_absolute(self, pwm, current_angle, target_angle):
        offset = target_angle - current_angle
        self.move_pan_by_offset(pwm, current_angle, offset)

    def tilt_angle_to_duty(self, angle):
        return self.min_duty + (self.max_duty - self.min_duty) * (angle / 180.0)

    def move_tilt_by_offset(self, pwm, current_angle, offset):
        max_angle = self.servo_config["tilt"]["max_angle"]
        target_angle = max(0, min(max_angle, current_angle + offset))

        step_size = self.servo_config["tilt"]["step_size"]
        delay_sec = self.servo_config["tilt"]["delay_sec"]

        if target_angle > current_angle:
            angles = range(int(current_angle), int(target_angle) + 1, step_size)
        else:
            angles = range(int(current_angle), int(target_angle) - 1, -step_size)

        for ang in angles:
            duty = self.tilt_angle_to_duty(ang)
            pwm.ChangeDutyCycle(duty)
            time.sleep(delay_sec)

        self.write_last_angle("tilt", target_angle)

    def move_tilt_to_absolute(self, pwm, current_angle, target_angle):
        offset = target_angle - current_angle
        self.move_tilt_by_offset(pwm, current_angle, offset)