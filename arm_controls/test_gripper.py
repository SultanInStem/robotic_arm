from pymycobot.mycobot import MyCobot
from pymycobot import PI_PORT, PI_BAUD

import time 

mc = MyCobot("/dev/ttyAMA0", 115200)
mc.set_gripper_mode(0)
mc.set_gripper_state(0,80)
time.sleep(3)
mc.set_gripper_state(1,80)
time.sleep(3)
mc.set_gripper_state(0,80)
time.sleep(3)