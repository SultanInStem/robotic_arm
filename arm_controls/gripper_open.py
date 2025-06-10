from pymycobot.mycobot import MyCobot
import pymycobot
import time
mc = MyCobot('/dev/ttyAMA0', 115200)


def open():
    mc.set_gripper_state(254, 80)
    time.sleep(2)
    return
open()

