from pymycobot.mycobot import MyCobot
import pymycobot
import time
mc = MyCobot('/dev/ttyAMA0', 115200)


def close():
    mc.set_gripper_state(100, 70)
    time.sleep(2)
    return
close()