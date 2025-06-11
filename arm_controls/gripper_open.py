from pymycobot.mycobot import MyCobot
import pymycobot
import time
mc = MyCobot('/dev/ttyAMA0', 115200)


def open():
    mc.set_gripper_state(0, 100)
    value = mc.get_gripper_value()
    print(value)
    time.sleep(4)
    return
open()

