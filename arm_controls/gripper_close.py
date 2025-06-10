from pymycobot.mycobot import MyCobot
import pymycobot
import time
mc = MyCobot('/dev/ttyAMA0', 115200)


def close():
    mc.set_gripper_value(, 70)
    time.sleep(4)
    return
close()