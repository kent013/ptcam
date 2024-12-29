import RPi.GPIO as GPIO
import time
import argparse

# ==============================================
# 定数定義
# ==============================================
SERVO_PIN = 14      # BCM番号 (GPIO14)
STEP_SIZE = 5       # 5度刻みで動かす
DELAY_SEC = 0.1     # 各ステップでのウェイト (秒)
ANGLE_FILE = "servo_angle.txt"  # 最後の角度を保存するファイル
DEFAULT_ANGLE = 90.0  # ファイルがない場合の初期角度

# 0度 → 2.5% , 180度 → 12.5% の単純線形変換
def angle_to_duty(angle):
  """角度(0-180)をデューティ比(2.5-12.5)に変換"""
  return (angle / 18.0) + 2.5

def move_servo_slowly(pwm, start_angle, target_angle):
  """
  サーボ(PWM)を start_angle から target_angle まで
  STEP_SIZE度ずつゆっくり動かす。
  """
  if target_angle > start_angle:
    angles = range(int(start_angle), int(target_angle) + 1, STEP_SIZE)
  else:
    angles = range(int(start_angle), int(target_angle) - 1, -STEP_SIZE)

  for ang in angles:
    duty = angle_to_duty(ang)
    pwm.ChangeDutyCycle(duty)
    time.sleep(DELAY_SEC)

def read_last_angle():
  """最後の角度をファイルから読み取る"""
  try:
    with open(ANGLE_FILE, "r") as f:
      angle = float(f.read().strip())
      print(f"Last angle read from file: {angle} degrees")
      return angle
  except FileNotFoundError:
    print(f"No angle file found. Using default angle: {DEFAULT_ANGLE} degrees")
    return DEFAULT_ANGLE

def write_last_angle(angle):
  """最後の角度をファイルに書き込む"""
  with open(ANGLE_FILE, "w") as f:
    f.write(f"{angle}")
    print(f"Last angle {angle} written to file")  # 修正箇所

def main():
  parser = argparse.ArgumentParser(description="Control SG90 servo on GPIO14 slowly by 5-degree steps")
  parser.add_argument("--angle", type=float, required=True, help="Target angle (0 to 180)")
  args = parser.parse_args()

  # 目標角度を 0-180にクリップ
  target_angle = max(0, min(180, args.angle))

  # ファイルから現在角度を取得
  current_angle = read_last_angle()

  # 与えられた角度が保存されている角度と同じなら終了
  if current_angle == target_angle:
    print(f"Target angle {target_angle} is the same as the current angle. No action required.")
    return

  # GPIO初期化
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(SERVO_PIN, GPIO.OUT)

  pwm = GPIO.PWM(SERVO_PIN, 50)  # 周波数50Hz
  pwm.start(0)

  try:
    # サーボを動かす
    print(f"Moving servo from {current_angle} to {target_angle}, step={STEP_SIZE} deg, delay={DELAY_SEC} sec")
    move_servo_slowly(pwm, current_angle, target_angle)

    # 完了後、目標角度をファイルに保存
    write_last_angle(target_angle)

  finally:
    pwm.stop()
    GPIO.cleanup()

if __name__ == "__main__":
  main()
