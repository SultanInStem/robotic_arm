from pymycobot.mycobot import MyCobot
import time
mc = MyCobot('/dev/ttyAMA0', 115200)


def open():
    print(pymycobot.__version__)
    mc.set_gripper_state(0, 70)
    time.sleep(2)
    return
open()

