import sys
import os
import time
from pymycobot.mycobot import MyCobot 
sys.path.append(os.path.abspath(".."))
from utils.funcs import compute_ik
from utils.globals import PORT, BANDWIDTH
mc = MyCobot(PORT, BANDWIDTH)

def open_gripper(speed=80):
    if speed > 100: 
        print("speed cannot be greater than 100")
        return -1
    mc.set_gripper_state(0, speed)
    time.sleep(2)

    return 0 

def close_gripper(speed=80): 
    if speed > 100:
        print("speed cannot be greater than 100")
        return -1 
    mc.set_gripper_state(1, speed)
    time.sleep(2)
    return 0 

def move_to_location(point, speed): 
    mc = MyCobot(PORT, BANDWIDTH)
    angles = compute_ik(point)
    if len(angles) < 6: return -1
    elif speed > 90: 
        print("speed must not exceed 90")
        return -1
    mc.send_angles(angles, speed)
    while mc.is_moving():
        time.sleep(0.1)
    time.sleep(2)
    return 0

def reset(): 
    mc.send_angles([0,0,0,0,0,0], 30)
    while mc.is_moving(): ### Allows for the movement to finish properly
        time.sleep(0.1)
    time.sleep(2)
    mc.set_gripper_calibration()
    return 0

def calibrate_joints(): 
    mc.set_servo_calibration(1)
    print("You have 8 seconds to align all the joints")
    time.sleep(8)
    mc.focus_servo(1)
