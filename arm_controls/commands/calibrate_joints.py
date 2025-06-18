import time
from pymycobot.mycobot import MyCobot 
mc = MyCobot('/dev/ttyAMA0', 115200)

def calibrate(): 
    mc.set_servo_calibration(1)
    time.sleep(5)
    mc.focus_servo(1)
    print("callibration is finished")
calibrate()