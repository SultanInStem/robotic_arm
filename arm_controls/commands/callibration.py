from pymycobot.mycobot import MyCobot 
import time
mc = MyCobot("/dev/ttyAMA0",115200)

def callibrate(): 
    mc.set_servo_calibration(1)
    time.sleep(5)
    mc.focus_servo(1)
    print("callibration is finished")
callibrate()