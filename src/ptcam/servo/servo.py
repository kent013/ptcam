import RPi.GPIO as GPIO
import time
import argparse
import math

# ==============================================
# 定数定義
# ==============================================
ANGLE_FILE = "servo_angles.txt"  # 角度を保存するファイル
SERVO_CONFIG = {
  "pan": {"pin": 15, "default_angle": 0.0, "full_sweep_time": 1.0, "max_angle": 360.0},
  "tilt": {"pin": 14, "default_angle": 0.0, "step_size": 2, "delay_sec": 0.1, "max_angle": 180.0},
}
MIN_DUTY = 2.5      # 最小デューティ比 (0度 = 1ms)
MAX_DUTY = 10.0     # 最大デューティ比 (180度 = 2ms)

# ==============================================
# 共通関数
# ==============================================
def read_last_angle(servo_name):
    """
    ファイルから指定されたサーボの最後の角度を読み取る
    """
    try:
        with open(ANGLE_FILE, "r") as f:
            angles = dict(line.strip().split("=") for line in f if "=" in line)
            return float(angles.get(servo_name, SERVO_CONFIG[servo_name]["default_angle"]))
    except FileNotFoundError:
        print(f"No angle file found. Using default angle for {servo_name}: {SERVO_CONFIG[servo_name]['default_angle']} degrees")
        return SERVO_CONFIG[servo_name]["default_angle"]

def write_last_angle(servo_name, angle):
    """
    指定されたサーボの角度をファイルに書き込む
    """
    try:
        angles = {}
        # 既存の内容を読み込む
        with open(ANGLE_FILE, "r") as f:
            angles = dict(line.strip().split("=") for line in f if "=" in line)
    except FileNotFoundError:
        pass

    # 新しい角度で更新
    angles[servo_name] = str(angle)

    # ファイルに書き戻す
    with open(ANGLE_FILE, "w") as f:
        for key, value in angles.items():
            f.write(f"{key}={value}\n")
        print(f"{servo_name} angle {angle} written to file")

def initialize_servo(servo_name):
    """
    サーボの初期化を行い、PWMオブジェクトと現在角度を返す
    """
    if servo_name not in SERVO_CONFIG:
        raise ValueError(f"Invalid servo name: {servo_name}")

    GPIO.setmode(GPIO.BCM)
    servo_pin = SERVO_CONFIG[servo_name]["pin"]
    GPIO.setup(servo_pin, GPIO.OUT)

    pwm = GPIO.PWM(servo_pin, 50)  # 周波数50Hz
    pwm.start(0)

    current_angle = read_last_angle(servo_name)
    return pwm, current_angle

def cleanup_servo(pwm):
    """
    サーボの終了処理
    """
    pwm.stop()
    GPIO.cleanup()

# ==============================================
# PANサーボ制御関数
# ==============================================
def move_pan_by_offset(pwm, current_angle, offset):
    """
    panサーボを現在角度から相対移動
    """
    max_angle = SERVO_CONFIG["pan"]["max_angle"]
    target_angle = max(0, min(max_angle, current_angle + offset))

    angle_difference = abs(target_angle - current_angle)
    move_time = (angle_difference / 180.0) * SERVO_CONFIG["pan"]["full_sweep_time"]

    target_duty = 7.809 if offset > 0 else 6.434
    print(f"[PAN] Moving from {current_angle}° by offset {offset}° to {target_angle}° in {move_time:.2f}s (Duty={target_duty:.2f}%)")

    pwm.ChangeDutyCycle(target_duty)
    time.sleep(move_time)

    write_last_angle("pan", target_angle)

def move_pan_to_absolute(pwm, current_angle, target_angle):
    """
    panサーボを絶対角度に移動
    """
    offset = target_angle - current_angle
    move_pan_by_offset(pwm, current_angle, offset)

# ==============================================
# TILTサーボ制御関数
# ==============================================
def tilt_angle_to_duty(angle):
    """
    tiltサーボのデューティ比を計算
    - 0度から180度で線形変化
    """
    return MIN_DUTY + (MAX_DUTY - MIN_DUTY) * (angle / 180.0)

def move_tilt_by_offset(pwm, current_angle, offset):
    """
    tiltサーボを現在角度から相対移動
    """
    max_angle = SERVO_CONFIG["tilt"]["max_angle"]
    target_angle = max(0, min(max_angle, current_angle + offset))

    print(f"[TILT] Moving from {current_angle}° by offset {offset}° to {target_angle}° in steps of {SERVO_CONFIG['tilt']['step_size']}°")

    step_size = SERVO_CONFIG["tilt"]["step_size"]
    delay_sec = SERVO_CONFIG["tilt"]["delay_sec"]

    if target_angle > current_angle:
        angles = range(int(current_angle), int(target_angle) + 1, step_size)
    else:
        angles = range(int(current_angle), int(target_angle) - 1, -step_size)

    for ang in angles:
        duty = tilt_angle_to_duty(ang)
        pwm.ChangeDutyCycle(duty)
        time.sleep(delay_sec)

    write_last_angle("tilt", target_angle)

def move_tilt_to_absolute(pwm, current_angle, target_angle):
    """
    tiltサーボを絶対角度に移動
    """
    offset = target_angle - current_angle
    move_tilt_by_offset(pwm, current_angle, offset)

# ==============================================
# メイン処理
# ==============================================
def main():
    parser = argparse.ArgumentParser(description="Control servos (pan or tilt) with absolute or relative movement")
    parser.add_argument("--servo", type=str, required=True, choices=SERVO_CONFIG.keys(), help="Servo to control (pan or tilt)")
    parser.add_argument("--angle", type=float, help="Target absolute angle (0 to max_angle)")
    parser.add_argument("--offset", type=float, help="Relative movement offset (-max_angle to max_angle)")
    args = parser.parse_args()

    if args.angle is None and args.offset is None:
        raise ValueError("You must specify either --angle (absolute) or --offset (relative)")

    pwm, current_angle = initialize_servo(args.servo)

    try:
        if args.servo == "pan":
            if args.angle is not None:
                move_pan_to_absolute(pwm, current_angle, args.angle)
            elif args.offset is not None:
                move_pan_by_offset(pwm, current_angle, args.offset)
        elif args.servo == "tilt":
            if args.angle is not None:
                move_tilt_to_absolute(pwm, current_angle, args.angle)
            elif args.offset is not None:
                move_tilt_by_offset(pwm, current_angle, args.offset)
    finally:
        cleanup_servo(pwm)

if __name__ == "__main__":
    main()
