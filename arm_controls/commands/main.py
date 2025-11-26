import sys
import os
import time
from pymycobot.mycobot320 import MyCobot320

sys.path.append(os.path.abspath(".."))
from utils.funcs import compute_ik, compute_fk, convert_to_radians
from utils.globals import PORT, BANDWIDTH
mc = MyCobot320(PORT, BANDWIDTH)

def open_gripper(speed=80):
    mc.set_gripper_mode(1)
    if speed > 100: 
        print("speed cannot be greater than 100")
        return -1
    
    mc.set_gripper_value(100, speed)
    time.sleep(2)

    return 0 

def close_gripper(speed=80): 
    mc.set_gripper_mode(1)
    print("GRIPPER VALUE ", mc.get_gripper_mode())
    if speed > 100:
        print("speed cannot be greater than 100")
        return -1

    mc.set_gripper_value(0, speed)
    time.sleep(2)
    return 0 
def grab_object(speed, degree): 
    mc.set_gripper_mode(1)
    if speed > 100: 
        print("speed cannot be greater than 100")
        return -1
    if degree < 0 or degree > 100: 
        print("degree must be between 0 and 100")
        return -1
    mc.set_gripper_value(degree, speed)
    time.sleep(2)
    return 0

def move_to_location(point, speed): 
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
    mc.send_angles([0,0,0,0,0,0], 10)
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

def calibrate_gripper():
    mc.set_gripper_calibration()
    time.sleep(2)
 
def get_arms_orientation(): 
    angles = mc.get_angles() ## angles in degrees
    for i in range(0, len(angles)): 
        angles[i] = convert_to_radians(angles[i])
    angles.insert(0,0)
    angles.append(0)
    pos = compute_fk(angles)
    print("ANGLES (RAD): ", angles)
    print("POSITION: ", pos)
    return pos


def test_pro_gripper(speed=30):
    if speed > 100: 
        print("speed cannot be greater than 100")
        return -1
    mc.set_pro_gripper_close(speed)
    time.sleep(2)
    mc.set_pro_gripper_open(speed)    
    time.sleep(2)
    return 0




