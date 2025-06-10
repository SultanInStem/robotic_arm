from pymycobot.mycobot import MyCobot
import time
mc = MyCobot('/dev/ttyAMA0', 115200)


def open():
    mc.init_gripper()
    mc.set_gripper_value(0, 50)
    time.sleep(2)
    return
open()

