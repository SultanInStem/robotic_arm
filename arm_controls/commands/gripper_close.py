import time
from pymycobot.mycobot import MyCobot 
mc = MyCobot('/dev/ttyAMA0', 115200)

def close():
    mc.set_gripper_state(1, 70)
    time.sleep(2)
    return
close()