from pymycobot.mycobot import MyCobot
import pymycobot
import time
mc = MyCobot('/dev/ttyAMA0', 115200)


def open():
    print("HELLO WORLD")
    mc.set_gripper_value(0, 70)
    time.sleep(2)
    return
open()

