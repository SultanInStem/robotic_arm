from pymycobot.mycobot import MyCobot
import pymycobot
import time
mc = MyCobot('/dev/ttyAMA0', 115200)


def open():
    grip_value = mc.set_gripper_state(0, 100)
    print(grip_value)
    time.sleep(4)
    return
open()

