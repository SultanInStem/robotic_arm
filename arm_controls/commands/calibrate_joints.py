import time
import sys 
import os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from globals import mc

def calibrate(): 
    mc.set_servo_calibration(1)
    time.sleep(5)
    mc.focus_servo(1)
    print("callibration is finished")
calibrate()