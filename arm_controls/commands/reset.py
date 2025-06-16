import time
from pymycobot.mycobot import MyCobot
mc = MyCobot('/dev/ttyAMA0', 115200)
# This file moves the arm back to its initial position 

def set_origin_coord(): 
    mc.send_angles([0,0,0,0,0,0], 50)
    while mc.is_moving(): ### Allows for the movement to finish properly
        time.sleep(0.1)
    time.sleep(2)
    mc.set_gripper_calibration()
    return
set_origin_coord()